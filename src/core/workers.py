"""
QThread Workers for Background Operations
Provides thread-safe background processing for monitoring, downloading, and uploading
"""
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition
from typing import Optional, Dict, Any
from pathlib import Path
import logging
import time
from datetime import datetime

from youtube.monitor import ChannelMonitor
from youtube.downloader import VideoDownloader
from youtube.uploader import VideoUploader
from core.events import EventType, publish
from core.database import DatabaseManager


class MonitoringWorker(QThread):
    """
    Background worker for YouTube channel monitoring
    Runs periodic checks for new videos
    """
    
    # Signals
    video_detected = pyqtSignal(dict)  # Emits video info
    monitoring_started = pyqtSignal()
    monitoring_stopped = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, monitor: ChannelMonitor, check_interval: int = 300):
        """
        Initialize monitoring worker
        
        Args:
            monitor: ChannelMonitor instance
            check_interval: Time between checks in seconds (default 5 minutes)
        """
        super().__init__()
        self.monitor = monitor
        self.check_interval = check_interval
        self._is_running = False
        self._is_paused = False
        self._stop_requested = False
        self._mutex = QMutex()
        self._pause_condition = QWaitCondition()
        self._logger = logging.getLogger(__name__)
    
    def run(self):
        """Main monitoring loop"""
        self._is_running = True
        self._stop_requested = False
        self._logger.info("Monitoring worker started")
        self.monitoring_started.emit()
        publish(EventType.MONITORING_STARTED, source="monitoring_worker")
        
        try:
            while not self._stop_requested:
                # Check if paused
                self._mutex.lock()
                if self._is_paused:
                    self._logger.debug("Monitoring paused, waiting...")
                    self._pause_condition.wait(self._mutex)
                    self._mutex.unlock()
                    continue
                self._mutex.unlock()
                
                # Perform monitoring check
                try:
                    self._logger.info("Checking for new videos...")
                    new_videos = self.monitor.check_for_new_videos()
                    
                    if new_videos:
                        self._logger.info(f"Found {len(new_videos)} new video(s)")
                        for video in new_videos:
                            self.video_detected.emit(video)
                            publish(EventType.VIDEO_DETECTED, {
                                'video_id': video.get('video_id'),
                                'title': video.get('title'),
                                'url': video.get('url'),
                                'published_at': video.get('published_at')
                            }, source="monitoring_worker")
                    else:
                        self._logger.debug("No new videos found")
                
                except Exception as e:
                    error_msg = f"Error during monitoring check: {str(e)}"
                    self._logger.error(error_msg, exc_info=True)
                    self.error_occurred.emit(error_msg)
                    publish(EventType.ERROR_OCCURRED, {
                        'error': error_msg,
                        'component': 'monitoring_worker'
                    }, source="monitoring_worker")
                
                # Sleep until next check (interruptible)
                for _ in range(self.check_interval):
                    if self._stop_requested:
                        break
                    time.sleep(1)
        
        finally:
            self._is_running = False
            self._logger.info("Monitoring worker stopped")
            self.monitoring_stopped.emit()
            publish(EventType.MONITORING_STOPPED, source="monitoring_worker")
    
    def pause(self):
        """Pause monitoring"""
        self._mutex.lock()
        self._is_paused = True
        self._mutex.unlock()
        self._logger.info("Monitoring paused")
        publish(EventType.MONITORING_PAUSED, source="monitoring_worker")
    
    def resume(self):
        """Resume monitoring"""
        self._mutex.lock()
        self._is_paused = False
        self._pause_condition.wakeAll()
        self._mutex.unlock()
        self._logger.info("Monitoring resumed")
        publish(EventType.MONITORING_RESUMED, source="monitoring_worker")
    
    def stop(self):
        """Stop monitoring"""
        self._logger.info("Stop requested for monitoring worker")
        self._stop_requested = True
        
        # Wake up if paused
        self._mutex.lock()
        if self._is_paused:
            self._is_paused = False
            self._pause_condition.wakeAll()
        self._mutex.unlock()
    
    def is_paused(self) -> bool:
        """Check if monitoring is paused"""
        self._mutex.lock()
        paused = self._is_paused
        self._mutex.unlock()
        return paused


class DownloadWorker(QThread):
    """
    Background worker for video downloads
    Downloads video and thumbnail for a single video
    """
    
    # Signals
    download_started = pyqtSignal(str)  # video_id
    download_progress = pyqtSignal(str, dict)  # video_id, progress_info
    download_completed = pyqtSignal(str, dict)  # video_id, file_paths
    download_failed = pyqtSignal(str, str)  # video_id, error
    
    def __init__(self, downloader: VideoDownloader, video_info: Dict[str, Any], 
                 output_dir: str, db: DatabaseManager):
        """
        Initialize download worker
        
        Args:
            downloader: VideoDownloader instance
            video_info: Video information dictionary (must contain 'video_id')
            output_dir: Output directory for downloads
            db: Database manager for status updates
        """
        super().__init__()
        self.downloader = downloader
        self.video_info = video_info
        self.output_dir = output_dir
        self.db = db
        
        # Extract and validate video_id
        video_id = video_info.get('video_id')
        if not video_id or not isinstance(video_id, str):
            raise ValueError(f"Invalid or missing video_id in video_info: {video_id}")
        self.video_id: str = video_id
        
        self._logger = logging.getLogger(__name__)
        self._cancelled = False
    
    def run(self):
        """Execute download"""
        try:
            self._logger.info(f"Starting download for video: {self.video_id}")
            self.download_started.emit(self.video_id)
            publish(EventType.DOWNLOAD_STARTED, {
                'video_id': self.video_id,
                'title': self.video_info.get('title')
            }, source="download_worker")
            
            # Update database status
            self.db.update_video_status(self.video_id, 'downloading')
            
            # Progress callback
            def progress_callback(info):
                if not self._cancelled:
                    self.download_progress.emit(self.video_id, info)
                    publish(EventType.DOWNLOAD_PROGRESS, {
                        'video_id': self.video_id,
                        'progress': info
                    }, source="download_worker")
            
            # Download video (returns dict with video_path and thumbnail_path)
            result = self.downloader.download_video(
                self.video_id,
                progress_callback=progress_callback
            )
            
            if self._cancelled:
                self._logger.info(f"Download cancelled for video: {self.video_id}")
                return
            
            # Check if download was successful
            if not result.get('success', False):
                error_msg = result.get('error', 'Unknown error')
                self._logger.error(f"Download failed for video {self.video_id}: {error_msg}")
                self.db.update_video_error(self.video_id, f"Download failed: {error_msg}")
                self.db.update_video_status(self.video_id, 'error')
                self.download_failed.emit(self.video_id, error_msg)
                publish(EventType.DOWNLOAD_FAILED, {
                    'video_id': self.video_id,
                    'error': error_msg
                }, source="download_worker")
                return
            
            video_path = result.get('video_path')
            thumbnail_path = result.get('thumbnail_path')
            
            # Extract metadata from download result
            tags = result.get('tags', [])
            category_id = result.get('category_id', '22')
            
            # Validate paths exist
            if not video_path or not Path(video_path).exists():
                error_msg = "Video file not found after download"
                self._logger.error(f"{error_msg}: {self.video_id}")
                self.db.update_video_error(self.video_id, error_msg)
                self.db.update_video_status(self.video_id, 'error')
                self.download_failed.emit(self.video_id, error_msg)
                publish(EventType.DOWNLOAD_FAILED, {
                    'video_id': self.video_id,
                    'error': error_msg
                }, source="download_worker")
                return
            
            # Save metadata to database (tags and category_id)
            import json
            metadata = {
                'tags': tags,
                'category_id': category_id
            }
            
            # Update database
            self.db.update_video_files(
                self.video_id,
                video_path,
                thumbnail_path if thumbnail_path else ""
            )
            # Update status AND set downloaded_at timestamp
            self.db.update_video_status(
                self.video_id, 
                'downloaded',
                downloaded_at=datetime.now().isoformat()
            )
            # Update metadata
            self.db.update_video_metadata(self.video_id, json.dumps(metadata))
            
            result = {
                'video_path': video_path,
                'thumbnail_path': thumbnail_path,
                'tags': tags,
                'category_id': category_id
            }
            
            self._logger.info(f"Download completed for video: {self.video_id}")
            self.download_completed.emit(self.video_id, result)
            publish(EventType.DOWNLOAD_COMPLETED, {
                'video_id': self.video_id,
                'video_path': video_path,
                'thumbnail_path': thumbnail_path
            }, source="download_worker")
        
        except Exception as e:
            error_msg = f"Download failed: {str(e)}"
            self._logger.error(f"Download error for {self.video_id}: {error_msg}", exc_info=True)
            
            # Update database
            self.db.update_video_status(self.video_id, 'failed')
            self.db.update_video_error(self.video_id, error_msg)
            
            self.download_failed.emit(self.video_id, error_msg)
            publish(EventType.DOWNLOAD_FAILED, {
                'video_id': self.video_id,
                'error': error_msg
            }, source="download_worker")
    
    def cancel(self):
        """Cancel the download"""
        self._logger.info(f"Cancelling download for video: {self.video_id}")
        self._cancelled = True
        publish(EventType.DOWNLOAD_CANCELLED, {
            'video_id': self.video_id
        }, source="download_worker")


class UploadWorker(QThread):
    """
    Background worker for video uploads
    Uploads video and sets thumbnail
    """
    
    # Signals
    upload_started = pyqtSignal(str)  # video_id
    upload_progress = pyqtSignal(str, dict)  # video_id, progress_info
    upload_completed = pyqtSignal(str, str)  # video_id, uploaded_video_id
    upload_failed = pyqtSignal(str, str)  # video_id, error
    
    def __init__(self, uploader: VideoUploader, video_info: Dict[str, Any],
                 video_path: str, thumbnail_path: Optional[str], db: DatabaseManager):
        """
        Initialize upload worker
        
        Args:
            uploader: VideoUploader instance
            video_info: Video information dictionary (must contain 'video_id' and 'title')
            video_path: Path to video file
            thumbnail_path: Path to thumbnail file (optional)
            db: Database manager for status updates
        """
        super().__init__()
        self.uploader = uploader
        self.video_info = video_info
        self.video_path = video_path
        self.thumbnail_path = thumbnail_path
        self.db = db
        
        # Extract and validate video_id
        video_id = video_info.get('video_id')
        if not video_id or not isinstance(video_id, str):
            raise ValueError(f"Invalid or missing video_id in video_info: {video_id}")
        self.video_id: str = video_id
        
        self._logger = logging.getLogger(__name__)
        self._cancelled = False
    
    def run(self):
        """Execute upload"""
        try:
            self._logger.info(f"Starting upload for video: {self.video_id}")
            self.upload_started.emit(self.video_id)
            publish(EventType.UPLOAD_STARTED, {
                'video_id': self.video_id,
                'title': self.video_info.get('title')
            }, source="upload_worker")
            
            # Update database status
            self.db.update_video_status(self.video_id, 'uploading')
            
            # Progress callback
            def progress_callback(info):
                if not self._cancelled:
                    self.upload_progress.emit(self.video_id, info)
                    publish(EventType.UPLOAD_PROGRESS, {
                        'video_id': self.video_id,
                        'progress': info
                    }, source="upload_worker")
            
            # Upload video
            title = self.video_info.get('title')
            if not title or not isinstance(title, str):
                raise ValueError(f"Invalid or missing title in video_info: {title}")
            
            uploaded_video_id, upload_error = self.uploader.upload(
                self.video_path,
                title=title,
                description=self.video_info.get('description', ''),
                tags=self.video_info.get('tags', []),
                category_id=self.video_info.get('category_id', '22'),
                privacy_status=self.video_info.get('privacy_status', 'private'),
                progress_callback=progress_callback
            )
            
            if self._cancelled:
                self._logger.info(f"Upload cancelled for video: {self.video_id}")
                return
            
            # Check if upload was successful
            if not uploaded_video_id:
                error_msg = upload_error or "Upload failed: No video ID returned from YouTube API"
                self._logger.error(f"Upload failed for {self.video_id}: {error_msg}")
                
                # Update database with failure status and detailed error
                self.db.update_video_status(self.video_id, 'failed')
                self.db.update_video_error(self.video_id, error_msg)
                
                self.upload_failed.emit(self.video_id, error_msg)
                publish(EventType.UPLOAD_FAILED, {
                    'video_id': self.video_id,
                    'error': error_msg
                }, source="upload_worker")
                return
            
            # Set thumbnail if provided
            if self.thumbnail_path and uploaded_video_id:
                try:
                    self.uploader.set_thumbnail(uploaded_video_id, self.thumbnail_path)
                except Exception as e:
                    self._logger.warning(f"Failed to set thumbnail: {e}")
            
            # Update database with success status
            self.db.update_video_uploaded_id(self.video_id, uploaded_video_id)
            self.db.update_video_status(self.video_id, 'completed')
            self.db.update_video_timestamp(self.video_id, 'uploaded_at', datetime.now())
            
            self._logger.info(f"Upload completed successfully for video: {self.video_id} -> {uploaded_video_id}")
            self.upload_completed.emit(self.video_id, uploaded_video_id)
            publish(EventType.UPLOAD_COMPLETED, {
                'video_id': self.video_id,
                'uploaded_video_id': uploaded_video_id
            }, source="upload_worker")
        
        except Exception as e:
            error_msg = f"Upload failed: {str(e)}"
            self._logger.error(f"Upload error for {self.video_id}: {error_msg}", exc_info=True)
            
            # Update database
            self.db.update_video_status(self.video_id, 'failed')
            self.db.update_video_error(self.video_id, error_msg)
            
            self.upload_failed.emit(self.video_id, error_msg)
            publish(EventType.UPLOAD_FAILED, {
                'video_id': self.video_id,
                'error': error_msg
            }, source="upload_worker")
    
    def cancel(self):
        """Cancel the upload"""
        self._logger.info(f"Cancelling upload for video: {self.video_id}")
        self._cancelled = True
        publish(EventType.UPLOAD_CANCELLED, {
            'video_id': self.video_id
        }, source="upload_worker")
