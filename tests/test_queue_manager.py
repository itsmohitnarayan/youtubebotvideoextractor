"""
Unit tests for Video Processing Queue Manager
Tests priority queue, retry logic, and state management
"""
import pytest
import time
from datetime import datetime
from threading import Thread
from src.core.queue_manager import (
    VideoProcessingQueue, VideoPriority, VideoStatus, VideoTask
)


class TestVideoTask:
    """Test VideoTask dataclass"""
    
    def test_task_creation(self):
        """Test creating a VideoTask"""
        now = datetime.now()
        task = VideoTask(
            priority=VideoPriority.HIGH.value,
            timestamp=now,
            video_id='test123',
            video_info={'title': 'Test Video'}
        )
        
        assert task.priority == VideoPriority.HIGH.value
        assert task.video_id == 'test123'
        assert task.retry_count == 0
        assert task.max_retries == 3
    
    def test_task_ordering(self):
        """Test that tasks are ordered by priority then timestamp"""
        now = datetime.now()
        
        task1 = VideoTask(VideoPriority.NORMAL.value, now, 'vid1', {})
        task2 = VideoTask(VideoPriority.HIGH.value, now, 'vid2', {})
        task3 = VideoTask(VideoPriority.LOW.value, now, 'vid3', {})
        
        # HIGH < NORMAL < LOW (priority 1 < 2 < 3)
        assert task2 < task1
        assert task1 < task3
    
    def test_can_retry(self):
        """Test retry capability check"""
        task = VideoTask(VideoPriority.NORMAL.value, datetime.now(), 'vid1', {})
        
        assert task.can_retry() is True
        
        task.retry_count = 3
        assert task.can_retry() is False
        
        task.retry_count = 5
        assert task.can_retry() is False
    
    def test_increment_retry(self):
        """Test incrementing retry counter"""
        task = VideoTask(VideoPriority.NORMAL.value, datetime.now(), 'vid1', {})
        
        assert task.retry_count == 0
        task.increment_retry()
        assert task.retry_count == 1
        task.increment_retry()
        assert task.retry_count == 2


class TestVideoProcessingQueue:
    """Test VideoProcessingQueue class"""
    
    def setup_method(self):
        """Setup for each test"""
        self.queue = VideoProcessingQueue(max_concurrent=3)
    
    def teardown_method(self):
        """Cleanup after each test"""
        self.queue.clear_all()
    
    def test_add_task(self):
        """Test adding a task to queue"""
        video_info = {
            'video_id': 'abc123',
            'title': 'Test Video',
            'url': 'https://youtube.com/watch?v=abc123'
        }
        
        success = self.queue.add_task(video_info, VideoPriority.NORMAL)
        
        assert success is True
        assert self.queue.get_queue_size() == 1
    
    def test_add_task_without_video_id(self):
        """Test that adding task without video_id fails"""
        video_info = {'title': 'Test Video'}  # No video_id
        
        success = self.queue.add_task(video_info, VideoPriority.NORMAL)
        
        assert success is False
        assert self.queue.get_queue_size() == 0
    
    def test_add_duplicate_task(self):
        """Test that adding same video twice fails"""
        video_info = {'video_id': 'abc123', 'title': 'Test'}
        
        # Add first time - success
        success1 = self.queue.add_task(video_info, VideoPriority.NORMAL)
        assert success1 is True
        
        # Get task (moves to processing)
        task = self.queue.get_next_task(timeout=0.1)
        assert task is not None
        
        # Try to add again - should fail (in processing)
        success2 = self.queue.add_task(video_info, VideoPriority.NORMAL)
        assert success2 is False
    
    def test_get_next_task(self):
        """Test retrieving next task from queue"""
        video_info = {'video_id': 'abc123', 'title': 'Test'}
        self.queue.add_task(video_info, VideoPriority.NORMAL)
        
        task = self.queue.get_next_task(timeout=0.1)
        
        assert task is not None
        assert task.video_id == 'abc123'
        assert self.queue.get_processing_count() == 1
        assert self.queue.get_queue_size() == 0
    
    def test_get_next_task_empty_queue(self):
        """Test getting task from empty queue"""
        task = self.queue.get_next_task(timeout=0.1)
        
        assert task is None
    
    def test_priority_ordering(self):
        """Test that tasks are processed in priority order"""
        # Use max_concurrent=10 to ensure we can get all tasks
        queue = VideoProcessingQueue(max_concurrent=10)
        
        # Add tasks in mixed priority order
        queue.add_task({'video_id': 'low1'}, VideoPriority.LOW)
        queue.add_task({'video_id': 'high1'}, VideoPriority.HIGH)
        queue.add_task({'video_id': 'normal1'}, VideoPriority.NORMAL)
        queue.add_task({'video_id': 'high2'}, VideoPriority.HIGH)
        
        # Should get HIGH priority tasks first
        task1 = queue.get_next_task(timeout=0.1)
        assert task1.priority == VideoPriority.HIGH.value
        
        task2 = queue.get_next_task(timeout=0.1)
        assert task2.priority == VideoPriority.HIGH.value
        
        # Then NORMAL
        task3 = queue.get_next_task(timeout=0.1)
        assert task3.priority == VideoPriority.NORMAL.value
        
        # Finally LOW
        task4 = queue.get_next_task(timeout=0.1)
        assert task4.priority == VideoPriority.LOW.value
    
    def test_max_concurrent_limit(self):
        """Test that concurrent processing limit is enforced"""
        queue = VideoProcessingQueue(max_concurrent=2)
        
        # Add 5 tasks
        for i in range(5):
            queue.add_task({'video_id': f'vid{i}'}, VideoPriority.NORMAL)
        
        # Get tasks - should only get 2 (max_concurrent)
        task1 = queue.get_next_task(timeout=0.1)
        task2 = queue.get_next_task(timeout=0.1)
        task3 = queue.get_next_task(timeout=0.1)  # Should be None
        
        assert task1 is not None
        assert task2 is not None
        assert task3 is None  # Blocked by concurrent limit
        assert queue.get_processing_count() == 2
    
    def test_mark_completed(self):
        """Test marking a task as completed"""
        self.queue.add_task({'video_id': 'abc123'}, VideoPriority.NORMAL)
        task = self.queue.get_next_task(timeout=0.1)
        
        assert self.queue.get_processing_count() == 1
        assert self.queue.get_completed_count() == 0
        
        success = self.queue.mark_completed('abc123')
        
        assert success is True
        assert self.queue.get_processing_count() == 0
        assert self.queue.get_completed_count() == 1
    
    def test_mark_completed_not_processing(self):
        """Test marking non-processing task as completed fails"""
        success = self.queue.mark_completed('nonexistent')
        
        assert success is False
    
    def test_mark_failed_with_retry(self):
        """Test marking task as failed triggers retry"""
        self.queue.add_task({'video_id': 'abc123'}, VideoPriority.HIGH)
        task = self.queue.get_next_task(timeout=0.1)
        
        # Mark as failed (should re-queue for retry)
        success = self.queue.mark_failed('abc123', 'Test error')
        
        assert success is True
        assert self.queue.get_processing_count() == 0
        assert self.queue.get_queue_size() == 1  # Re-queued
        
        # Get retry task - should have lower priority
        retry_task = self.queue.get_next_task(timeout=0.1)
        assert retry_task.retry_count == 1
        assert retry_task.priority == VideoPriority.LOW.value  # Lowered priority
    
    def test_mark_failed_max_retries(self):
        """Test task fails permanently after max retries"""
        self.queue.add_task({'video_id': 'abc123'}, VideoPriority.NORMAL)
        
        # Fail 3 times (will retry each time)
        for i in range(3):
            task = self.queue.get_next_task(timeout=0.1)
            assert task is not None
            self.queue.mark_failed('abc123', f'Error {i}')
        
        # 4th failure - should not retry
        task = self.queue.get_next_task(timeout=0.1)
        assert task is not None
        assert task.retry_count == 3
        
        success = self.queue.mark_failed('abc123', 'Final error')
        
        assert success is False  # No more retries
        assert self.queue.get_failed_count() == 1
        assert self.queue.get_queue_size() == 0
    
    def test_cancel_task_in_queue(self):
        """Test cancelling a task that's in queue"""
        self.queue.add_task({'video_id': 'abc123'}, VideoPriority.NORMAL)
        self.queue.add_task({'video_id': 'def456'}, VideoPriority.NORMAL)
        
        assert self.queue.get_queue_size() == 2
        
        success = self.queue.cancel_task('abc123')
        
        assert success is True
        assert self.queue.get_queue_size() == 1
    
    def test_cancel_task_processing(self):
        """Test cancelling a task that's being processed"""
        self.queue.add_task({'video_id': 'abc123'}, VideoPriority.NORMAL)
        task = self.queue.get_next_task(timeout=0.1)
        
        assert self.queue.get_processing_count() == 1
        
        success = self.queue.cancel_task('abc123')
        
        assert success is True
        assert self.queue.get_processing_count() == 0
        assert self.queue.get_failed_count() == 1
    
    def test_get_statistics(self):
        """Test getting queue statistics"""
        # Use max_concurrent=10 to get all tasks
        queue = VideoProcessingQueue(max_concurrent=10)
        
        # Add task, move to processing, then leave it processing
        queue.add_task({'video_id': 'processing1'}, VideoPriority.NORMAL)
        task1 = queue.get_next_task(timeout=0.1)  # Now in processing
        assert task1 is not None
        assert task1.video_id == 'processing1'
        
        # Add task, move to processing, then complete it
        queue.add_task({'video_id': 'completed1'}, VideoPriority.NORMAL)
        task2 = queue.get_next_task(timeout=0.1)  # Now in processing
        assert task2 is not None
        assert task2.video_id == 'completed1'
        success = queue.mark_completed('completed1')  # Move to completed
        assert success is True
        
        # Add task, move to processing, then fail it (max retries)
        queue.add_task({'video_id': 'failed1'}, VideoPriority.NORMAL)
        task3 = queue.get_next_task(timeout=0.1)  # Now in processing
        assert task3 is not None
        assert task3.video_id == 'failed1'
        # Set max retries BEFORE calling mark_failed
        with queue._lock:
            queue._processing['failed1'].retry_count = 3  # Max retries
        success = queue.mark_failed('failed1', 'Error')  # Move to failed
        # Should return False because max retries reached
        assert success is False
        
        # Add task and leave it queued
        queue.add_task({'video_id': 'queued1'}, VideoPriority.NORMAL)
        
        stats = queue.get_statistics()
        
        assert stats['queued'] == 1  # queued1
        assert stats['processing'] == 1  # processing1
        assert stats['completed'] == 1  # completed1
        assert stats['failed'] == 1  # failed1
    
    def test_get_processing_tasks(self):
        """Test getting list of processing tasks"""
        self.queue.add_task({'video_id': 'vid1'}, VideoPriority.NORMAL)
        self.queue.add_task({'video_id': 'vid2'}, VideoPriority.NORMAL)
        
        task1 = self.queue.get_next_task(timeout=0.1)
        task2 = self.queue.get_next_task(timeout=0.1)
        
        processing = self.queue.get_processing_tasks()
        
        assert len(processing) == 2
        assert 'vid1' in processing
        assert 'vid2' in processing
    
    def test_clear_completed(self):
        """Test clearing completed tasks"""
        self.queue.add_task({'video_id': 'vid1'}, VideoPriority.NORMAL)
        task = self.queue.get_next_task(timeout=0.1)
        self.queue.mark_completed('vid1')
        
        assert self.queue.get_completed_count() == 1
        
        self.queue.clear_completed()
        
        assert self.queue.get_completed_count() == 0
    
    def test_clear_failed(self):
        """Test clearing failed tasks"""
        self.queue.add_task({'video_id': 'vid1'}, VideoPriority.NORMAL)
        task = self.queue.get_next_task(timeout=0.1)
        task.retry_count = 3
        self.queue.mark_failed('vid1', 'Error')
        
        assert self.queue.get_failed_count() == 1
        
        self.queue.clear_failed()
        
        assert self.queue.get_failed_count() == 0
    
    def test_clear_all(self):
        """Test clearing all queues"""
        # Add tasks in various states
        self.queue.add_task({'video_id': 'queued'}, VideoPriority.NORMAL)
        self.queue.add_task({'video_id': 'processing'}, VideoPriority.NORMAL)
        task = self.queue.get_next_task(timeout=0.1)
        
        self.queue.clear_all()
        
        stats = self.queue.get_statistics()
        assert stats['queued'] == 0
        assert stats['processing'] == 0
        assert stats['completed'] == 0
        assert stats['failed'] == 0
    
    def test_thread_safety(self):
        """Test thread-safe queue operations"""
        results = []
        
        def add_tasks():
            for i in range(50):
                self.queue.add_task(
                    {'video_id': f'vid_{i}_{time.time()}'},
                    VideoPriority.NORMAL
                )
        
        def get_tasks():
            for _ in range(25):
                task = self.queue.get_next_task(timeout=0.1)
                if task:
                    results.append(task)
                    self.queue.mark_completed(task.video_id)
        
        # Run multiple threads
        add_threads = [Thread(target=add_tasks) for _ in range(3)]
        get_threads = [Thread(target=get_tasks) for _ in range(2)]
        
        for t in add_threads + get_threads:
            t.start()
        
        for t in add_threads + get_threads:
            t.join()
        
        # Should have processed some tasks without crashes
        assert len(results) > 0
        assert self.queue.get_statistics()  # Should not crash


class TestVideoPriority:
    """Test VideoPriority enum"""
    
    def test_priority_values(self):
        """Test priority enum values"""
        assert VideoPriority.HIGH.value == 1
        assert VideoPriority.NORMAL.value == 2
        assert VideoPriority.LOW.value == 3
        
        # Lower number = higher priority
        assert VideoPriority.HIGH.value < VideoPriority.NORMAL.value
        assert VideoPriority.NORMAL.value < VideoPriority.LOW.value


class TestVideoStatus:
    """Test VideoStatus enum"""
    
    def test_status_values(self):
        """Test status enum values"""
        expected_statuses = [
            'queued', 'downloading', 'downloaded',
            'uploading', 'completed', 'failed', 'cancelled'
        ]
        
        for status in expected_statuses:
            assert hasattr(VideoStatus, status.upper())
