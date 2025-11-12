"""
Unit Tests for Worker Threads
Tests MonitoringWorker, DownloadWorker, and UploadWorker basic functionality
Note: Qt thread signal testing is complex and timing-dependent, so we focus on
initialization, structure, and basic behavior rather than signal timing.
"""
import pytest
from unittest.mock import Mock, MagicMock
from PyQt5.QtCore import QCoreApplication
from datetime import datetime
import sys

from src.core.workers import MonitoringWorker, DownloadWorker, UploadWorker
from src.youtube.monitor import ChannelMonitor
from src.youtube.downloader import VideoDownloader
from src.youtube.uploader import VideoUploader
from src.core.database import DatabaseManager


@pytest.fixture
def qapp():
    """Create QApplication for testing Qt components"""
    if not QCoreApplication.instance():
        app = QCoreApplication(sys.argv)
    else:
        app = QCoreApplication.instance()
    yield app
    app.processEvents()


class TestMonitoringWorker:
    """Test suite for MonitoringWorker"""
    
    @pytest.fixture
    def mock_monitor(self):
        """Create mock ChannelMonitor"""
        monitor = Mock(spec=ChannelMonitor)
        monitor.check_for_new_videos = Mock(return_value=[])
        return monitor
    
    def test_worker_initialization(self, mock_monitor, qapp):
        """Test worker initializes correctly"""
        worker = MonitoringWorker(mock_monitor, check_interval=300)
        
        assert worker.monitor == mock_monitor
        assert worker.check_interval == 300
        assert worker._is_running is False
        assert worker._is_paused is False
        assert worker._stop_requested is False
        
        worker.deleteLater()
    
    def test_worker_signals_exist(self, mock_monitor, qapp):
        """Test that all required signals exist"""
        worker = MonitoringWorker(mock_monitor)
        
        assert hasattr(worker, 'video_detected')
        assert hasattr(worker, 'monitoring_started')
        assert hasattr(worker, 'monitoring_stopped')
        assert hasattr(worker, 'error_occurred')
        
        worker.deleteLater()
    
    def test_worker_pause_resume(self, mock_monitor, qapp):
        """Test pause/resume functionality"""
        worker = MonitoringWorker(mock_monitor)
        
        assert worker.is_paused() is False
        
        worker.pause()
        assert worker.is_paused() is True
        
        worker.resume()
        assert worker.is_paused() is False
        
        worker.deleteLater()
    
    def test_worker_methods_exist(self, mock_monitor, qapp):
        """Test that required methods exist"""
        worker = MonitoringWorker(mock_monitor)
        
        assert callable(worker.run)
        assert callable(worker.pause)
        assert callable(worker.resume)
        assert callable(worker.stop)
        assert callable(worker.is_paused)
        
        worker.deleteLater()


class TestDownloadWorker:
    """Test suite for DownloadWorker"""
    
    @pytest.fixture
    def mock_downloader(self):
        """Create mock VideoDownloader"""
        downloader = Mock(spec=VideoDownloader)
        downloader.download_video = Mock(return_value='/path/to/video.mp4')
        downloader.download_thumbnail = Mock(return_value='/path/to/thumb.jpg')
        return downloader
    
    @pytest.fixture
    def mock_db(self):
        """Create mock DatabaseManager"""
        db = Mock(spec=DatabaseManager)
        db.update_video_status = Mock(return_value=True)
        db.update_video_files = Mock(return_value=True)
        db.update_video_error = Mock(return_value=True)
        return db
    
    @pytest.fixture
    def video_info(self):
        """Sample video info"""
        return {
            'video_id': 'test123',
            'title': 'Test Video',
            'url': 'https://youtube.com/watch?v=test123',
            'description': 'Test description',
            'tags': ['test', 'video'],
            'category_id': '22',
            'published_at': '2025-11-10T10:00:00Z'
        }
    
    def test_worker_initialization(self, mock_downloader, mock_db, video_info, qapp):
        """Test worker initializes correctly"""
        worker = DownloadWorker(mock_downloader, video_info, '/output', mock_db)
        
        assert worker.downloader == mock_downloader
        assert worker.video_info == video_info
        assert worker.output_dir == '/output'
        assert worker.db == mock_db
        assert worker.video_id == 'test123'
        assert worker._cancelled is False
        
        worker.deleteLater()
    
    def test_worker_signals_exist(self, mock_downloader, mock_db, video_info, qapp):
        """Test that all required signals exist"""
        worker = DownloadWorker(mock_downloader, video_info, '/output', mock_db)
        
        assert hasattr(worker, 'download_started')
        assert hasattr(worker, 'download_progress')
        assert hasattr(worker, 'download_completed')
        assert hasattr(worker, 'download_failed')
        
        worker.deleteLater()
    
    def test_worker_cancel(self, mock_downloader, mock_db, video_info, qapp):
        """Test cancel functionality"""
        worker = DownloadWorker(mock_downloader, video_info, '/output', mock_db)
        
        assert worker._cancelled is False
        worker.cancel()
        assert worker._cancelled is True
        
        worker.deleteLater()
    
    def test_worker_methods_exist(self, mock_downloader, mock_db, video_info, qapp):
        """Test that required methods exist"""
        worker = DownloadWorker(mock_downloader, video_info, '/output', mock_db)
        
        assert callable(worker.run)
        assert callable(worker.cancel)
        
        worker.deleteLater()


class TestUploadWorker:
    """Test suite for UploadWorker"""
    
    @pytest.fixture
    def mock_uploader(self):
        """Create mock VideoUploader"""
        uploader = Mock(spec=VideoUploader)
        uploader.upload_video = Mock(return_value='uploaded123')
        uploader.set_thumbnail = Mock(return_value=True)
        return uploader
    
    @pytest.fixture
    def mock_db(self):
        """Create mock DatabaseManager"""
        db = Mock(spec=DatabaseManager)
        db.update_video_status = Mock(return_value=True)
        db.update_video_uploaded_id = Mock(return_value=True)
        db.update_video_timestamp = Mock(return_value=True)
        db.update_video_error = Mock(return_value=True)
        return db
    
    @pytest.fixture
    def video_info(self):
        """Sample video info"""
        return {
            'video_id': 'test123',
            'title': 'Test Video',
            'description': 'Test description',
            'tags': ['test', 'video'],
            'category_id': '22',
            'privacy_status': 'private'
        }
    
    def test_worker_initialization(self, mock_uploader, mock_db, video_info, qapp):
        """Test worker initializes correctly"""
        worker = UploadWorker(
            mock_uploader,
            video_info,
            '/path/to/video.mp4',
            '/path/to/thumb.jpg',
            mock_db
        )
        
        assert worker.uploader == mock_uploader
        assert worker.video_info == video_info
        assert worker.video_path == '/path/to/video.mp4'
        assert worker.thumbnail_path == '/path/to/thumb.jpg'
        assert worker.db == mock_db
        assert worker.video_id == 'test123'
        assert worker._cancelled is False
        
        worker.deleteLater()
    
    def test_worker_initialization_without_thumbnail(self, mock_uploader, mock_db, video_info, qapp):
        """Test worker initializes without thumbnail"""
        worker = UploadWorker(
            mock_uploader,
            video_info,
            '/path/to/video.mp4',
            None,  # No thumbnail
            mock_db
        )
        
        assert worker.thumbnail_path is None
        
        worker.deleteLater()
    
    def test_worker_signals_exist(self, mock_uploader, mock_db, video_info, qapp):
        """Test that all required signals exist"""
        worker = UploadWorker(
            mock_uploader,
            video_info,
            '/path/to/video.mp4',
            '/path/to/thumb.jpg',
            mock_db
        )
        
        assert hasattr(worker, 'upload_started')
        assert hasattr(worker, 'upload_progress')
        assert hasattr(worker, 'upload_completed')
        assert hasattr(worker, 'upload_failed')
        
        worker.deleteLater()
    
    def test_worker_cancel(self, mock_uploader, mock_db, video_info, qapp):
        """Test cancel functionality"""
        worker = UploadWorker(
            mock_uploader,
            video_info,
            '/path/to/video.mp4',
            '/path/to/thumb.jpg',
            mock_db
        )
        
        assert worker._cancelled is False
        worker.cancel()
        assert worker._cancelled is True
        
        worker.deleteLater()
    
    def test_worker_methods_exist(self, mock_uploader, mock_db, video_info, qapp):
        """Test that required methods exist"""
        worker = UploadWorker(
            mock_uploader,
            video_info,
            '/path/to/video.mp4',
            '/path/to/thumb.jpg',
            mock_db
        )
        
        assert callable(worker.run)
        assert callable(worker.cancel)
        
        worker.deleteLater()
    
    def test_video_info_attributes(self, mock_uploader, mock_db, video_info, qapp):
        """Test that video_info is properly stored"""
        worker = UploadWorker(
            mock_uploader,
            video_info,
            '/path/to/video.mp4',
            '/path/to/thumb.jpg',
            mock_db
        )
        
        assert worker.video_info['title'] == 'Test Video'
        assert worker.video_info['description'] == 'Test description'
        assert worker.video_info['tags'] == ['test', 'video']
        assert worker.video_info['category_id'] == '22'
        assert worker.video_info['privacy_status'] == 'private'
        
        worker.deleteLater()
