"""
Main Application Controller
Coordinates all components and manages application lifecycle
"""
import sys
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer, Qt

from core.config import ConfigManager
from core.database import DatabaseManager
from core.logger import setup_logger
from core.events import EventType, Event, get_event_bus, subscribe
from core.workers import MonitoringWorker, DownloadWorker, UploadWorker
from core.queue_manager import VideoProcessingQueue, VideoPriority
from core.scheduler import TaskScheduler
from youtube.api_client import YouTubeAPIClient
from youtube.monitor import ChannelMonitor
from youtube.downloader import VideoDownloader
from youtube.uploader import VideoUploader
from gui.system_tray import SystemTrayIcon
from gui.main_window import MainWindow
from gui.settings_dialog import SettingsDialog
from utils.autostart import AutoStartManager


class ApplicationController:
    """
    Main application controller
    Manages all components and coordinates the video processing pipeline
    """
    
    def __init__(self):
        """Initialize application controller"""
        self.app: Optional[QApplication] = None
        self.config: Optional[ConfigManager] = None
        self.db: Optional[DatabaseManager] = None
        self.logger: Optional[logging.Logger] = None
        self.event_bus = get_event_bus()
        
        # YouTube components
        self.youtube_client: Optional[YouTubeAPIClient] = None
        self.monitor: Optional[ChannelMonitor] = None
        self.downloader: Optional[VideoDownloader] = None
        self.uploader: Optional[VideoUploader] = None
        
        # GUI components
        self.tray_icon: Optional[SystemTrayIcon] = None
        self.main_window: Optional[MainWindow] = None
        
        # Workers
        self.monitoring_worker: Optional[MonitoringWorker] = None
        self.active_downloads: dict = {}  # video_id -> DownloadWorker
        self.active_uploads: dict = {}    # video_id -> UploadWorker
        
        # Processing queue
        self.processing_queue: Optional[VideoProcessingQueue] = None
        
        # Scheduler
        self.scheduler: Optional[TaskScheduler] = None
        
        # Auto-start manager
        self.autostart_manager: Optional[AutoStartManager] = None
        
        # Timers
        self.queue_processor_timer: Optional[QTimer] = None
        
    def initialize(self) -> bool:
        """
        Initialize all application components
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Enable high DPI scaling
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
            
            # Initialize Qt application
            self.app = QApplication(sys.argv)
            self.app.setApplicationName("YouTube Bot Video Extractor")
            self.app.setOrganizationName("YTBot")
            self.app.setQuitOnLastWindowClosed(False)  # Keep running in tray
            
            # Load configuration
            self.config = ConfigManager()
            
            # Setup logging
            log_file = self.config.get('logging.file', 'logs/app.log')
            log_level = self.config.get('logging.level', 'INFO')
            setup_logger(log_file, log_level)
            self.logger = logging.getLogger(__name__)
            self.logger.info("=" * 60)
            self.logger.info("Application starting...")
            
            # Initialize database
            db_path = self.config.get('database.path', 'data/videos.db')
            self.db = DatabaseManager(db_path)
            
            # Initialize processing queue
            max_concurrent = self.config.get('processing.max_concurrent', 3)
            self.processing_queue = VideoProcessingQueue(max_concurrent)
            
            # Initialize YouTube components
            self._initialize_youtube_components()
            
            # Initialize scheduler
            self._initialize_scheduler()
            
            # Initialize GUI
            self._initialize_gui()
            
            # Initialize auto-start manager
            self.autostart_manager = AutoStartManager()
            
            # Subscribe to events
            self._subscribe_to_events()
            
            # Load queued videos from database into queue
            self._load_queued_videos()
            
            # Start queue processor
            self._start_queue_processor()
            
            self.logger.info("Application initialized successfully")
            return True
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to initialize application: {e}", exc_info=True)
            else:
                print(f"FATAL: Failed to initialize application: {e}")
            return False
    
    def _initialize_youtube_components(self):
        """Initialize YouTube API and related components"""
        try:
            # Initialize YouTube API client
            client_secrets_file = self.config.get('youtube.client_secrets_file', 'client_secrets.json')
            token_file = self.config.get('youtube.token_file', 'data/token.pickle')
            
            self.youtube_client = YouTubeAPIClient(client_secrets_file, token_file, self.db)
            
            # Initialize monitor
            target_channel_id = self.config.get('target_channel.channel_id', '')
            check_interval = self.config.get('monitoring.check_interval_minutes', 5)
            lookback_hours = self.config.get('monitoring.lookback_hours', 24)
            self.monitor = ChannelMonitor(
                self.youtube_client,
                self.db,
                target_channel_id,
                check_interval,
                lookback_hours
            )
            
            # Initialize downloader
            download_dir = self.config.get('download.output_directory', 'downloads')
            self.downloader = VideoDownloader(download_dir)
            
            # Initialize uploader
            self.uploader = VideoUploader(self.youtube_client)
            
            self.logger.info("YouTube components initialized")
        
        except Exception as e:
            self.logger.error(f"Failed to initialize YouTube components: {e}", exc_info=True)
            raise
    
    def _initialize_scheduler(self):
        """Initialize scheduler and schedule quota reset"""
        try:
            self.scheduler = TaskScheduler()
            self.scheduler.start()
            
            # Schedule daily quota reset at midnight
            self.scheduler.add_cron_job(
                job_id='quota_reset',
                func=self._reset_api_quota,
                hour=0,
                minute=0
            )
            
            self.logger.info("Scheduler initialized with quota reset job at midnight")
        
        except Exception as e:
            self.logger.error(f"Failed to initialize scheduler: {e}", exc_info=True)
            raise
    
    def _reset_api_quota(self):
        """Reset YouTube API quota counter (called at midnight)"""
        try:
            if self.youtube_client:
                self.youtube_client.reset_quota_counter()
                self.logger.info("API quota reset completed successfully")
        except Exception as e:
            self.logger.error(f"Error resetting API quota: {e}", exc_info=True)
    
    def _initialize_gui(self):
        """Initialize GUI components"""
        try:
            # Create main window (hidden initially)
            self.main_window = MainWindow()
            
            # Create system tray
            self.tray_icon = SystemTrayIcon(self.app)
            
            # Connect tray icon signals
            self.tray_icon.show_dashboard_requested.connect(self._on_show_dashboard)
            self.tray_icon.pause_resume_requested.connect(self._on_pause_resume_monitoring)
            self.tray_icon.check_now_requested.connect(self._on_check_now)
            self.tray_icon.settings_requested.connect(self._on_show_settings)
            self.tray_icon.logs_requested.connect(self._on_show_logs)
            self.tray_icon.exit_requested.connect(self._on_exit)
            
            # Connect main window signals
            self.main_window.pause_clicked.connect(self._on_pause_resume_monitoring)
            self.main_window.resume_clicked.connect(self._on_pause_resume_monitoring)
            self.main_window.check_now_clicked.connect(self._on_check_now)
            self.main_window.settings_clicked.connect(self._on_show_settings)
            
            # Show tray icon
            self.tray_icon.show()
            self.tray_icon.set_status('idle')
            
            # Update main window with channel info
            channel_id = self.config.get('target_channel.channel_id', '')
            channel_name = self.config.get('target_channel.channel_name', 'Not configured')
            if channel_id:
                self.main_window.set_channel_info(channel_name, channel_id)
            
            # Update initial statistics
            self._update_dashboard_stats()
            
            # Load recent videos into GUI
            self._load_recent_videos()
            
            self.logger.info("GUI components initialized")
        
        except Exception as e:
            self.logger.error(f"Failed to initialize GUI: {e}", exc_info=True)
            raise
    
    def _subscribe_to_events(self):
        """Subscribe to application events"""
        # Video detection
        subscribe(EventType.VIDEO_DETECTED, self._on_video_detected)
        
        # Download events
        subscribe(EventType.DOWNLOAD_COMPLETED, self._on_download_completed)
        subscribe(EventType.DOWNLOAD_FAILED, self._on_download_failed)
        
        # Upload events
        subscribe(EventType.UPLOAD_COMPLETED, self._on_upload_completed)
        subscribe(EventType.UPLOAD_FAILED, self._on_upload_failed)
        
        # Status events
        subscribe(EventType.MONITORING_STARTED, self._on_monitoring_status_changed)
        subscribe(EventType.MONITORING_STOPPED, self._on_monitoring_status_changed)
        subscribe(EventType.MONITORING_PAUSED, self._on_monitoring_status_changed)
        subscribe(EventType.MONITORING_RESUMED, self._on_monitoring_status_changed)
        
        self.logger.info("Subscribed to application events")
    
    def _update_dashboard_stats(self):
        """Update dashboard statistics from database"""
        try:
            # Query database for stats
            stats = self.db.get_statistics()
            
            # Update GUI if available
            if self.main_window:
                self.main_window.update_statistics(stats)
        except Exception as e:
            self.logger.error(f"Error updating dashboard stats: {e}")
    
    def _load_recent_videos(self):
        """Load recent videos from database into GUI"""
        try:
            # Get recent videos from database
            recent_videos = self.db.get_recent_videos(limit=50)
            
            # Add each video to the GUI
            if self.main_window and recent_videos:
                for video in recent_videos:
                    self.main_window.add_recent_video(
                        video.get('source_title', 'Unknown'),
                        video.get('status', 'unknown'),
                        video.get('created_at', '')
                    )
                self.logger.info(f"Loaded {len(recent_videos)} recent videos into GUI")
        except Exception as e:
            self.logger.error(f"Error loading recent videos: {e}")
    
    def _load_queued_videos(self):
        """Load queued videos from database into processing queue"""
        try:
            queued_videos = self.db.get_queued_videos()
            
            if queued_videos:
                self.logger.info(f"Loading {len(queued_videos)} queued videos into processing queue")
                
                for video in queued_videos:
                    # Load metadata from database (contains tags and category_id)
                    metadata = {}
                    if video.get('metadata'):
                        try:
                            import json
                            metadata = json.loads(video.get('metadata'))
                        except json.JSONDecodeError:
                            pass
                    
                    # Convert database record to video_info format
                    video_info = {
                        'video_id': video.get('source_video_id'),
                        'title': video.get('source_title'),  # Keep original title
                        'description': video.get('source_description', ''),  # Keep original description (will be prepended later)
                        'published_at': video.get('source_published_at'),
                        'thumbnail_url': video.get('source_thumbnail_url'),
                        'tags': metadata.get('tags', []),  # Use tags from metadata
                        'category_id': metadata.get('category_id', '20'),  # Gaming category as safe default
                    }
                    
                    # Add to queue with normal priority
                    self.processing_queue.add_task(video_info, VideoPriority.NORMAL)
                    self.logger.info(f"Added to queue: {video_info['video_id']} - {video_info['title']}")
                
                self.logger.info(f"Successfully loaded {len(queued_videos)} videos into queue")
            else:
                self.logger.info("No queued videos found in database")
        except Exception as e:
            self.logger.error(f"Error loading queued videos: {e}")
    
    def _start_queue_processor(self):
        """Start the queue processor timer"""
        self.queue_processor_timer = QTimer()
        self.queue_processor_timer.timeout.connect(self._process_queue)
        self.queue_processor_timer.start(2000)  # Check every 2 seconds
        self.logger.info("Queue processor started")
    
    def _process_queue(self):
        """Process the video queue (one download at a time to avoid file locking issues)"""
        # Check if there's already an active download
        if len(self.active_downloads) > 0:
            self.logger.debug("Download already in progress, skipping queue processing")
            return
        
        # Get next task from queue
        task = self.processing_queue.get_next_task(timeout=0.1)
        
        if task:
            # Double-check not already processing (race condition protection)
            if task.video_id in self.active_downloads:
                self.logger.warning(f"Task {task.video_id} already being processed, skipping")
                return
            
            self.logger.info(f"Processing task: {task}")
            
            # Create and start download worker
            download_worker = DownloadWorker(
                self.downloader,
                task.video_info,
                self.config.get('download.output_directory', 'downloads'),
                self.db
            )
            
            # Track worker BEFORE starting (prevents race condition)
            self.active_downloads[task.video_id] = download_worker
            
            # Connect signals
            download_worker.download_completed.connect(
                lambda vid, paths: self._on_worker_download_completed(vid, paths, task)
            )
            download_worker.download_failed.connect(
                lambda vid, error: self._on_worker_download_failed(vid, error, task)
            )
            
            # Start download
            download_worker.start()
    
    def _on_video_detected(self, event: Event):
        """Handle video detection event"""
        video_info = event.data
        video_id = video_info.get('video_id')
        
        self.logger.info(f"Video detected: {video_id} - {video_info.get('title')}")
        
        # Video is already added to database by monitor.py
        # No need to add again here
        
        # Add to processing queue
        priority = VideoPriority.HIGH  # New videos are high priority
        self.processing_queue.add_task(video_info, priority)
        
        # Show notification
        if self.tray_icon:
            self.tray_icon.show_info(
                "New Video Detected",
                f"Title: {video_info.get('title', 'Unknown')}"
            )
        
        # Update GUI
        if self.main_window:
            self.main_window.add_recent_video(
                video_info.get('title', 'Unknown'),
                'queued',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
        
        # Update stats
        self._update_dashboard_stats()
    
    def _on_worker_download_completed(self, video_id: str, file_paths: dict, task):
        """Handle download completion from worker"""
        self.logger.info(f"Download completed: {video_id}")
        
        # Remove from active downloads and clean up worker
        if video_id in self.active_downloads:
            worker = self.active_downloads.pop(video_id)
            worker.wait(1000)  # Wait up to 1 second for thread to finish
            worker.deleteLater()
        
        # Mark as completed in queue
        self.processing_queue.mark_completed(video_id)
        
        # Update video_info with metadata from download (tags, category_id)
        if 'tags' in file_paths:
            task.video_info['tags'] = file_paths['tags']
        if 'category_id' in file_paths:
            task.video_info['category_id'] = file_paths['category_id']
        
        # Add upload config settings to video_info
        upload_config = self.config.get('upload', {})
        task.video_info.setdefault('privacy_status', upload_config.get('privacy_status', 'public'))
        task.video_info.setdefault('made_for_kids', upload_config.get('made_for_kids', False))
        
        # Prepend custom message to original description
        original_description = task.video_info.get('description', '')
        task.video_info['description'] = f"Re-uploaded from MuFiJuL GaminG\n\n{original_description}"
        
        # Double-check not already uploading (race condition protection)
        if video_id in self.active_uploads:
            self.logger.warning(f"Video {video_id} already being uploaded, skipping")
            return
        
        # Start upload
        upload_worker = UploadWorker(
            self.uploader,
            task.video_info,
            file_paths.get('video_path'),
            file_paths.get('thumbnail_path'),
            self.db
        )
        
        # Track worker BEFORE starting (prevents race condition)
        self.active_uploads[video_id] = upload_worker
        
        # Connect signals
        upload_worker.upload_completed.connect(self._on_worker_upload_completed)
        upload_worker.upload_failed.connect(
            lambda vid, error: self._on_worker_upload_failed(vid, error, task)
        )
        
        # Start upload
        upload_worker.start()
        
        # Update stats
        self._update_dashboard_stats()
    
    def _on_worker_download_failed(self, video_id: str, error: str, task):
        """Handle download failure from worker"""
        self.logger.error(f"Download failed: {video_id} - {error}")
        
        # Remove from active downloads and clean up worker
        if video_id in self.active_downloads:
            worker = self.active_downloads.pop(video_id)
            worker.wait(1000)  # Wait up to 1 second for thread to finish
            worker.deleteLater()
        
        # Mark as failed in queue (will retry if possible)
        self.processing_queue.mark_failed(video_id, error)
        
        # Show notification
        if self.tray_icon:
            self.tray_icon.show_error(
                "Download Failed",
                f"Video: {task.video_info.get('title', 'Unknown')}\nError: {error}"
            )
    
    def _on_download_completed(self, event: Event):
        """Handle download completed event"""
        # Already handled in worker callback
        pass
    
    def _on_download_failed(self, event: Event):
        """Handle download failed event"""
        # Already handled in worker callback
        pass
    
    def _on_worker_upload_completed(self, video_id: str, uploaded_video_id: str):
        """Handle upload completion from worker"""
        self.logger.info(f"Upload completed: {video_id} -> {uploaded_video_id}")
        
        # Remove from active uploads and clean up worker
        if video_id in self.active_uploads:
            worker = self.active_uploads.pop(video_id)
            worker.wait(1000)  # Wait up to 1 second for thread to finish
            worker.deleteLater()
        
        # Show notification
        if self.tray_icon:
            video_info = self.db.get_video(video_id)
            self.tray_icon.show_info(
                "Upload Complete",
                f"Video: {video_info.get('title', 'Unknown')}\nID: {uploaded_video_id}"
            )
        
        # Update stats
        self._update_dashboard_stats()
    
    def _on_worker_upload_failed(self, video_id: str, error: str, task):
        """Handle upload failure from worker"""
        self.logger.error(f"Upload failed: {video_id} - {error}")
        
        # Remove from active uploads and clean up worker
        if video_id in self.active_uploads:
            worker = self.active_uploads.pop(video_id)
            worker.wait(1000)  # Wait up to 1 second for thread to finish
            worker.deleteLater()
        
        # Show notification
        if self.tray_icon:
            self.tray_icon.show_error(
                "Upload Failed",
                f"Video: {task.video_info.get('title', 'Unknown')}\nError: {error}"
            )
        
        # Update stats
        self._update_dashboard_stats()
    
    def _on_upload_completed(self, event: Event):
        """Handle upload completed event"""
        # Already handled in worker callback
        pass
    
    def _on_upload_failed(self, event: Event):
        """Handle upload failed event"""
        # Already handled in worker callback
        pass
    
    def _on_monitoring_status_changed(self, event: Event):
        """Handle monitoring status changes"""
        status_map = {
            EventType.MONITORING_STARTED: 'monitoring',
            EventType.MONITORING_STOPPED: 'idle',
            EventType.MONITORING_PAUSED: 'paused',
            EventType.MONITORING_RESUMED: 'monitoring'
        }
        
        status = status_map.get(event.type, 'idle')
        
        if self.tray_icon:
            self.tray_icon.set_status(status)
        
        if self.main_window:
            is_monitoring = status in ['monitoring']
            self.main_window.set_monitoring_state(is_monitoring)
    
    def _on_show_dashboard(self):
        """Show the main dashboard window"""
        if self.main_window:
            self.main_window.show()
            self.main_window.activateWindow()
            self.main_window.raise_()
    
    def _on_pause_resume_monitoring(self):
        """Toggle monitoring pause/resume"""
        if self.monitoring_worker and self.monitoring_worker.isRunning():
            if self.monitoring_worker.is_paused():
                self.monitoring_worker.resume()
            else:
                self.monitoring_worker.pause()
        else:
            # Start monitoring
            self.start_monitoring()
    
    def _on_check_now(self):
        """Trigger immediate monitoring check"""
        if self.monitor:
            try:
                new_videos = self.monitor.check_for_new_videos()
                if new_videos:
                    self.logger.info(f"Manual check found {len(new_videos)} video(s)")
                else:
                    self.logger.info("Manual check found no new videos")
                    if self.tray_icon:
                        self.tray_icon.show_info(
                            "Check Complete",
                            "No new videos found"
                        )
            except Exception as e:
                self.logger.error(f"Manual check failed: {e}", exc_info=True)
                if self.tray_icon:
                    self.tray_icon.show_error(
                        "Check Failed",
                        str(e)
                    )
    
    def _on_show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self.config, parent=self.main_window)
        if dialog.exec_():
            # Settings saved, reload configuration
            self.config.load()
            self.logger.info("Settings updated")
    
    def _on_show_logs(self):
        """Show logs in main window"""
        self._on_show_dashboard()
        # Switch to logs tab (would need to implement in MainWindow)
    
    def _on_exit(self):
        """Exit the application"""
        self.shutdown()
        self.app.quit()
    
    def start_monitoring(self):
        """Start the monitoring worker"""
        if self.monitoring_worker and self.monitoring_worker.isRunning():
            self.logger.warning("Monitoring already running")
            return
        
        check_interval = self.config.get('monitoring.check_interval', 300)
        self.monitoring_worker = MonitoringWorker(self.monitor, check_interval)
        
        # Connect signals
        self.monitoring_worker.video_detected.connect(
            lambda video: get_event_bus().publish(
                EventType.VIDEO_DETECTED,
                video,
                source="monitoring_worker"
            )
        )
        
        self.monitoring_worker.start()
        self.logger.info("Monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring worker"""
        if self.monitoring_worker and self.monitoring_worker.isRunning():
            self.monitoring_worker.stop()
            self.monitoring_worker.wait()
            self.monitoring_worker = None
            self.logger.info("Monitoring stopped")
    
    def run(self) -> int:
        """
        Run the application
        
        Returns:
            Exit code
        """
        # Publish app started event
        get_event_bus().publish(EventType.APP_STARTED, source="app_controller")
        
        # Start monitoring if configured
        if self.config.get('monitoring.auto_start', True):
            self.start_monitoring()
        
        # Enter Qt event loop
        return self.app.exec_()
    
    def shutdown(self):
        """Shutdown the application gracefully"""
        self.logger.info("Shutting down application...")
        
        # Publish app shutdown event
        get_event_bus().publish(EventType.APP_SHUTDOWN, source="app_controller")
        
        # Stop monitoring
        self.stop_monitoring()
        
        # Stop queue processor
        if self.queue_processor_timer:
            self.queue_processor_timer.stop()
        
        # Stop scheduler
        if self.scheduler:
            self.scheduler.shutdown()
        
        # Cancel active downloads
        for video_id, worker in list(self.active_downloads.items()):
            worker.cancel()
            worker.wait()
        
        # Cancel active uploads
        for video_id, worker in list(self.active_uploads.items()):
            worker.cancel()
            worker.wait()
        
        # Close database
        if self.db:
            self.db.close()
        
        self.logger.info("Application shutdown complete")


def main():
    """Main entry point"""
    controller = ApplicationController()
    
    if not controller.initialize():
        sys.exit(1)
    
    sys.exit(controller.run())


if __name__ == '__main__':
    main()
