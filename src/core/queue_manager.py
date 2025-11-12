"""
Video Processing Queue System
Manages the pipeline of video processing: detection → download → upload
"""
from queue import PriorityQueue, Empty
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import logging
from threading import Lock


class VideoPriority(Enum):
    """Priority levels for video processing"""
    HIGH = 1      # Recent videos (< 1 hour old)
    NORMAL = 2    # Regular videos
    LOW = 3       # Retry/backlog videos


class VideoStatus(Enum):
    """Status of video in processing pipeline"""
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    DOWNLOADED = "downloaded"
    UPLOADING = "uploading"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(order=True)
class VideoTask:
    """
    Video task for processing queue
    Uses priority and timestamp for ordering
    """
    priority: int = field(compare=True)
    timestamp: datetime = field(compare=True)
    video_id: str = field(compare=False)
    video_info: Dict[str, Any] = field(compare=False, default_factory=dict)
    retry_count: int = field(compare=False, default=0)
    max_retries: int = field(compare=False, default=3)
    
    def __repr__(self):
        return f"VideoTask(priority={self.priority}, video_id={self.video_id}, retry={self.retry_count})"
    
    def can_retry(self) -> bool:
        """Check if task can be retried"""
        return self.retry_count < self.max_retries
    
    def increment_retry(self):
        """Increment retry counter"""
        self.retry_count += 1


class VideoProcessingQueue:
    """
    Thread-safe queue for managing video processing pipeline
    
    Features:
    - Priority-based processing
    - Retry mechanism
    - Status tracking
    - Error handling
    """
    
    def __init__(self, max_concurrent: int = 3):
        """
        Initialize processing queue
        
        Args:
            max_concurrent: Maximum number of concurrent downloads/uploads
        """
        self._queue = PriorityQueue()
        self._processing: Dict[str, VideoTask] = {}  # Currently processing
        self._completed: Dict[str, VideoTask] = {}   # Successfully completed
        self._failed: Dict[str, VideoTask] = {}      # Failed tasks
        self._lock = Lock()
        self._max_concurrent = max_concurrent
        self._logger = logging.getLogger(__name__)
    
    def add_task(self, video_info: Dict[str, Any], priority: VideoPriority = VideoPriority.NORMAL) -> bool:
        """
        Add a video task to the queue
        
        Args:
            video_info: Video information dictionary (must contain 'video_id')
            priority: Task priority
            
        Returns:
            True if added successfully, False if already in queue/processing
        """
        video_id = video_info.get('video_id')
        if not video_id:
            self._logger.error("Cannot add task without video_id")
            return False
        
        with self._lock:
            # Check if already processing or completed
            if video_id in self._processing:
                self._logger.warning(f"Video {video_id} is already being processed")
                return False
            
            if video_id in self._completed:
                self._logger.warning(f"Video {video_id} already completed")
                return False
        
        # Create task
        task = VideoTask(
            priority=priority.value,
            timestamp=datetime.now(),
            video_id=video_id,
            video_info=video_info
        )
        
        self._queue.put(task)
        self._logger.info(f"Added task to queue: {task}")
        return True
    
    def get_next_task(self, timeout: float = 1.0) -> Optional[VideoTask]:
        """
        Get next task from queue
        
        Args:
            timeout: Timeout in seconds to wait for task
            
        Returns:
            Next VideoTask or None if queue is empty
        """
        # Check if we've reached max concurrent
        with self._lock:
            if len(self._processing) >= self._max_concurrent:
                return None
        
        try:
            task = self._queue.get(timeout=timeout)
            
            with self._lock:
                self._processing[task.video_id] = task
            
            self._logger.info(f"Retrieved task from queue: {task}")
            return task
        
        except Empty:
            return None
    
    def mark_completed(self, video_id: str) -> bool:
        """
        Mark a task as completed
        
        Args:
            video_id: Video ID
            
        Returns:
            True if marked successfully
        """
        with self._lock:
            if video_id not in self._processing:
                self._logger.warning(f"Cannot mark {video_id} as completed - not in processing")
                return False
            
            task = self._processing.pop(video_id)
            self._completed[video_id] = task
            self._logger.info(f"Marked task as completed: {video_id}")
            return True
    
    def mark_failed(self, video_id: str, error: str = None) -> bool:
        """
        Mark a task as failed and optionally retry
        
        Args:
            video_id: Video ID
            error: Error message
            
        Returns:
            True if marked/retried successfully
        """
        with self._lock:
            if video_id not in self._processing:
                self._logger.warning(f"Cannot mark {video_id} as failed - not in processing")
                return False
            
            task = self._processing.pop(video_id)
        
        # Check if can retry
        if task.can_retry():
            task.increment_retry()
            # Lower priority for retries
            task.priority = VideoPriority.LOW.value
            task.timestamp = datetime.now()
            
            self._queue.put(task)
            self._logger.info(f"Re-queued failed task for retry ({task.retry_count}/{task.max_retries}): {video_id}")
            return True
        else:
            with self._lock:
                self._failed[video_id] = task
            self._logger.error(f"Task failed permanently (max retries reached): {video_id}")
            return False
    
    def cancel_task(self, video_id: str) -> bool:
        """
        Cancel a task (remove from queue or mark as cancelled if processing)
        
        Args:
            video_id: Video ID
            
        Returns:
            True if cancelled successfully
        """
        with self._lock:
            if video_id in self._processing:
                task = self._processing.pop(video_id)
                self._failed[video_id] = task
                self._logger.info(f"Cancelled processing task: {video_id}")
                return True
        
        # Try to remove from queue (harder - need to rebuild queue)
        tasks = []
        found = False
        
        while not self._queue.empty():
            try:
                task = self._queue.get_nowait()
                if task.video_id == video_id:
                    found = True
                    self._logger.info(f"Removed task from queue: {video_id}")
                else:
                    tasks.append(task)
            except Empty:
                break
        
        # Re-add remaining tasks
        for task in tasks:
            self._queue.put(task)
        
        return found
    
    def get_queue_size(self) -> int:
        """Get number of tasks in queue (waiting)"""
        return self._queue.qsize()
    
    def get_processing_count(self) -> int:
        """Get number of tasks currently processing"""
        with self._lock:
            return len(self._processing)
    
    def get_completed_count(self) -> int:
        """Get number of completed tasks"""
        with self._lock:
            return len(self._completed)
    
    def get_failed_count(self) -> int:
        """Get number of failed tasks"""
        with self._lock:
            return len(self._failed)
    
    def get_statistics(self) -> Dict[str, int]:
        """Get queue statistics"""
        return {
            'queued': self.get_queue_size(),
            'processing': self.get_processing_count(),
            'completed': self.get_completed_count(),
            'failed': self.get_failed_count()
        }
    
    def get_processing_tasks(self) -> Dict[str, VideoTask]:
        """Get currently processing tasks"""
        with self._lock:
            return self._processing.copy()
    
    def clear_completed(self):
        """Clear completed tasks history"""
        with self._lock:
            count = len(self._completed)
            self._completed.clear()
            self._logger.info(f"Cleared {count} completed tasks")
    
    def clear_failed(self):
        """Clear failed tasks history"""
        with self._lock:
            count = len(self._failed)
            self._failed.clear()
            self._logger.info(f"Cleared {count} failed tasks")
    
    def clear_all(self):
        """Clear all queues (use with caution)"""
        # Clear priority queue
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except Empty:
                break
        
        with self._lock:
            self._processing.clear()
            self._completed.clear()
            self._failed.clear()
        
        self._logger.warning("Cleared all queues")
