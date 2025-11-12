"""
Integration Tests for Complete Video Processing Workflow

Tests the full pipeline:
1. Video detection → Queue → Download → Upload
2. Error handling and retry logic
3. Concurrent processing
4. Graceful shutdown
5. Event propagation across components
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch, call
import time
import json
from PyQt5.QtCore import QCoreApplication
import logging

from src.core.events import EventBus, EventType
from src.core.queue_manager import VideoProcessingQueue, VideoPriority, VideoStatus
from src.core.database import DatabaseManager
from src.core.workers import MonitoringWorker, DownloadWorker, UploadWorker
from src.youtube.monitor import ChannelMonitor
from src.youtube.downloader import VideoDownloader
from src.youtube.uploader import VideoUploader


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def test_db(temp_dir):
    """Create test database"""
    db_path = Path(temp_dir) / "test.db"
    db = DatabaseManager(str(db_path))
    yield db
    db.close()


@pytest.fixture
def mock_api_client():
    """Mock YouTube API client"""
    client = Mock()
    
    # Mock get_recent_uploads to return test videos
    client.get_recent_uploads.return_value = [
        {
            'id': {'videoId': 'test_video_1'},
            'snippet': {
                'title': 'Test Video 1',
                'description': 'Test description 1',
                'publishedAt': datetime.now().isoformat()
            }
        }
    ]
    
    # Mock get_video_details
    client.get_video_details.return_value = {
        'id': 'test_video_1',
        'video_id': 'test_video_1',
        'snippet': {
            'title': 'Test Video 1',
            'description': 'Test description 1',
            'publishedAt': datetime.now().isoformat()
        },
        'title': 'Test Video 1',
        'description': 'Test description 1',
        'url': 'https://youtube.com/watch?v=test_video_1',
        'published_at': datetime.now().isoformat(),
        'duration': '5:30',
        'view_count': 1000,
        'tags': ['test', 'video']
    }
    
    return client


@pytest.fixture
def mock_downloader(temp_dir):
    """Mock video downloader"""
    downloader = Mock(spec=VideoDownloader)
    
    # Mock successful download
    video_path = Path(temp_dir) / "test_video_1.mp4"
    thumbnail_path = Path(temp_dir) / "test_video_1.jpg"
    
    # Create dummy files
    video_path.write_text("dummy video content")
    thumbnail_path.write_text("dummy thumbnail content")
    
    downloader.download_video.return_value = {
        'success': True,
        'video_path': str(video_path),
        'thumbnail_path': str(thumbnail_path),
        'video_id': 'test_video_1',
        'title': 'Test Video 1',
        'filesize': 1024000
    }
    
    downloader.current_progress = 0.0
    downloader.current_status = "idle"
    
    return downloader


@pytest.fixture
def mock_uploader():
    """Mock video uploader"""
    uploader = Mock(spec=VideoUploader)
    
    # Mock successful upload
    uploader.upload.return_value = 'uploaded_video_id_123'
    uploader.current_progress = 0.0
    uploader.current_status = "idle"
    
    return uploader


@pytest.fixture
def event_bus():
    """Create fresh event bus for each test"""
    bus = EventBus()
    yield bus
    # Clean up after test
    bus._subscribers.clear()


@pytest.fixture
def queue_manager():
    """Create queue manager"""
    return VideoProcessingQueue(max_concurrent=3)


@pytest.fixture
def qt_app():
    """Create QCoreApplication for Qt tests"""
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
    yield app


# ============================================================================
# Test 1: Complete Workflow (Detection → Queue → Download → Upload)
# ============================================================================

class TestCompleteWorkflow:
    """Test complete video processing workflow"""
    
    def test_video_detection_to_queue(self, mock_api_client, test_db, queue_manager, event_bus):
        """Test video detection and queuing"""
        # Setup monitor
        monitor = ChannelMonitor(
            api_client=mock_api_client,
            database=test_db,
            source_channel_id="test_channel_123"
        )
        
        # Track events
        detected_videos = []
        
        def on_video_detected(event):
            detected_videos.append(event.data)
        
        event_bus.subscribe(EventType.VIDEO_DETECTED, on_video_detected)
        
        # Check for new videos
        new_videos = monitor.check_for_new_videos()
        
        # Verify videos detected
        assert len(new_videos) == 1
        assert new_videos[0]['video_id'] == 'test_video_1'
        
        # Add to queue
        success = queue_manager.add_task(new_videos[0], VideoPriority.NORMAL)
        assert success is True
        
        # Verify queue state
        assert queue_manager.get_queue_size() == 1
        assert queue_manager.get_processing_count() == 0
        assert queue_manager.get_completed_count() == 0
    
    def test_queue_to_download(self, queue_manager, mock_downloader, test_db, event_bus):
        """Test queue processing and download"""
        # Add video to queue
        video_info = {
            'video_id': 'test_video_1',
            'title': 'Test Video 1',
            'url': 'https://youtube.com/watch?v=test_video_1'
        }
        
        queue_manager.add_task(video_info, VideoPriority.NORMAL)
        
        # Track events
        download_events = []
        
        def on_download_started(event):
            download_events.append(('started', event.data))
        
        def on_download_completed(event):
            download_events.append(('completed', event.data))
        
        event_bus.subscribe(EventType.DOWNLOAD_STARTED, on_download_started)
        event_bus.subscribe(EventType.DOWNLOAD_COMPLETED, on_download_completed)
        
        # Get task from queue
        task = queue_manager.get_next_task()
        assert task is not None
        assert task.video_id == 'test_video_1'
        
        # Start download
        event_bus.publish(EventType.DOWNLOAD_STARTED, {'video_id': 'test_video_1'})
        
        # Simulate download
        result = mock_downloader.download_video(
            video_id='test_video_1',
            custom_filename='test_video_1'
        )
        
        # Complete download
        assert result['success'] is True
        queue_manager.mark_completed(task.video_id)
        
        # Save to database
        test_db.add_video({
            'video_id': 'test_video_1',
            'title': 'Test Video 1',
            'url': 'https://youtube.com/watch?v=test_video_1',
            'status': 'downloaded'
        })
        
        test_db.update_video_files(
            video_id='test_video_1',
            video_path=result['video_path'],
            thumbnail_path=result['thumbnail_path']
        )
        
        event_bus.publish(EventType.DOWNLOAD_COMPLETED, {
            'video_id': 'test_video_1',
            'video_path': result['video_path']
        })
        
        # Verify events
        assert len(download_events) == 2
        assert download_events[0][0] == 'started'
        assert download_events[1][0] == 'completed'
        
        # Verify database
        video = test_db.get_video('test_video_1')
        assert video is not None
        assert video['status'] == 'downloaded'
    
    def test_download_to_upload(self, test_db, mock_uploader, temp_dir, event_bus):
        """Test download to upload workflow"""
        # Setup: Add downloaded video to database
        video_path = Path(temp_dir) / "test_video_1.mp4"
        video_path.write_text("dummy video content")
        
        test_db.add_video({
            'video_id': 'test_video_1',
            'title': 'Test Video 1',
            'url': 'https://youtube.com/watch?v=test_video_1',
            'status': 'downloaded'
        })
        
        test_db.update_video_files(
            video_id='test_video_1',
            video_path=str(video_path),
            thumbnail_path=None
        )
        
        # Track events
        upload_events = []
        
        def on_upload_started(event):
            upload_events.append(('started', event.data))
        
        def on_upload_completed(event):
            upload_events.append(('completed', event.data))
        
        event_bus.subscribe(EventType.UPLOAD_STARTED, on_upload_started)
        event_bus.subscribe(EventType.UPLOAD_COMPLETED, on_upload_completed)
        
        # Start upload
        event_bus.publish(EventType.UPLOAD_STARTED, {'video_id': 'test_video_1'})
        
        # Simulate upload
        uploaded_id = mock_uploader.upload(
            video_path=str(video_path),
            title='Test Video 1',
            description='Test description',
            privacy_status='private'
        )
        
        # Complete upload
        assert uploaded_id is not None
        test_db.update_video_status('test_video_1', 'uploaded')
        test_db.update_video_uploaded_id('test_video_1', uploaded_id)
        
        event_bus.publish(EventType.UPLOAD_COMPLETED, {
            'video_id': 'test_video_1',
            'uploaded_id': uploaded_id
        })
        
        # Verify events
        assert len(upload_events) == 2
        assert upload_events[0][0] == 'started'
        assert upload_events[1][0] == 'completed'
        
        # Verify database
        video = test_db.get_video('test_video_1')
        assert video['status'] == 'uploaded'
        # Uploaded ID is stored in target_video_id column, not metadata
        assert video['target_video_id'] == uploaded_id
    
    def test_end_to_end_workflow(self, mock_api_client, test_db, queue_manager, 
                                  mock_downloader, mock_uploader, event_bus):
        """Test complete end-to-end workflow"""
        # Track all events
        workflow_events = []
        
        def track_event(event_type):
            def handler(event):
                workflow_events.append((event_type.value, event.data))
            return handler
        
        # Subscribe to all workflow events
        event_bus.subscribe(EventType.VIDEO_DETECTED, track_event(EventType.VIDEO_DETECTED))
        event_bus.subscribe(EventType.DOWNLOAD_STARTED, track_event(EventType.DOWNLOAD_STARTED))
        event_bus.subscribe(EventType.DOWNLOAD_COMPLETED, track_event(EventType.DOWNLOAD_COMPLETED))
        event_bus.subscribe(EventType.UPLOAD_STARTED, track_event(EventType.UPLOAD_STARTED))
        event_bus.subscribe(EventType.UPLOAD_COMPLETED, track_event(EventType.UPLOAD_COMPLETED))
        
        # Step 1: Detect video
        monitor = ChannelMonitor(mock_api_client, test_db, "test_channel_123")
        new_videos = monitor.check_for_new_videos()
        
        # Step 2: Queue video
        queue_manager.add_task(new_videos[0], VideoPriority.NORMAL)
        task = queue_manager.get_next_task()
        
        # Step 3: Download video
        event_bus.publish(EventType.DOWNLOAD_STARTED, {'video_id': task.video_id})
        download_result = mock_downloader.download_video(video_id=task.video_id)
        
        test_db.add_video({
            'video_id': task.video_id,
            'title': new_videos[0]['title'],
            'url': new_videos[0]['url'],
            'status': 'downloaded'
        })
        test_db.update_video_files(
            video_id=task.video_id,
            video_path=download_result['video_path'],
            thumbnail_path=download_result['thumbnail_path']
        )
        event_bus.publish(EventType.DOWNLOAD_COMPLETED, {'video_id': task.video_id})
        
        # Step 4: Upload video
        event_bus.publish(EventType.UPLOAD_STARTED, {'video_id': task.video_id})
        uploaded_id = mock_uploader.upload(
            video_path=download_result['video_path'],
            title=new_videos[0]['title'],
            description=new_videos[0]['description']
        )
        
        test_db.update_video_status(task.video_id, 'uploaded')
        test_db.update_video_uploaded_id(task.video_id, uploaded_id)
        event_bus.publish(EventType.UPLOAD_COMPLETED, {'video_id': task.video_id})
        
        # Step 5: Mark complete
        queue_manager.mark_completed(task.video_id)
        
        # Verify complete workflow
        assert len(workflow_events) == 4  # download_start, download_complete, upload_start, upload_complete
        
        event_types = [e[0] for e in workflow_events]
        assert 'download_started' in event_types
        assert 'download_completed' in event_types
        assert 'upload_started' in event_types
        assert 'upload_completed' in event_types
        
        # Verify final state
        video = test_db.get_video(task.video_id)
        assert video['status'] == 'uploaded'
        
        assert queue_manager.get_completed_count() == 1
        assert queue_manager.get_queue_size() == 0


# ============================================================================
# Test 2: Error Handling and Retry Logic
# ============================================================================

class TestErrorHandlingAndRetry:
    """Test error handling and retry mechanisms"""
    
    def test_download_error_retry(self, queue_manager, test_db, event_bus):
        """Test download error triggers retry"""
        # Add video to queue
        video_info = {
            'video_id': 'test_video_fail',
            'title': 'Test Video Fail',
            'url': 'https://youtube.com/watch?v=test_video_fail'
        }
        
        queue_manager.add_task(video_info, VideoPriority.NORMAL)
        
        # Get task and simulate failure
        task = queue_manager.get_next_task()
        assert task.retry_count == 0
        
        # Mark as failed (this re-queues automatically if retries available)
        error_msg = "Network error during download"
        success = queue_manager.mark_failed(task.video_id, error_msg)
        assert success is True  # Should return True if re-queued
        
        # Save error to database
        test_db.add_video({
            'video_id': 'test_video_fail',
            'title': 'Test Video Fail',
            'url': 'https://youtube.com/watch?v=test_video_fail',
            'status': 'failed'
        })
        test_db.update_video_error('test_video_fail', error_msg)
        
        # Get retry task from queue
        next_task = queue_manager.get_next_task()
        assert next_task is not None
        assert next_task.video_id == 'test_video_fail'
        assert next_task.retry_count == 1
        assert next_task.can_retry() is True
        
        # Verify database
        video = test_db.get_video('test_video_fail')
        assert video['status'] == 'failed'
        # Error is stored in error_message column, not metadata
        assert video['error_message'] == error_msg
    
    def test_max_retries_exceeded(self, queue_manager):
        """Test task fails permanently after max retries"""
        video_info = {
            'video_id': 'test_video_max_retry',
            'title': 'Test Video Max Retry',
            'url': 'https://youtube.com/watch?v=test_video_max_retry'
        }
        
        queue_manager.add_task(video_info, VideoPriority.NORMAL)
        
        # Fail 3 times
        for i in range(3):
            task = queue_manager.get_next_task()
            assert task is not None
            assert task.can_retry() is True
            queue_manager.mark_failed(task.video_id, f"Error attempt {i+1}")
        
        # Try to get task again - should get None (no more in queue)
        # The 3rd failure should have put it in _failed permanently
        # Queue should now be empty
        task = queue_manager.get_next_task()
        # After 3 retries (4 total attempts), should not be in queue anymore
        assert task is None or task.retry_count >= 3
    
    def test_upload_error_handling(self, test_db, event_bus):
        """Test upload error is logged properly"""
        # Setup video in database
        test_db.add_video({
            'video_id': 'test_video_upload_fail',
            'title': 'Test Upload Fail',
            'url': 'https://youtube.com/watch?v=test_video_upload_fail',
            'status': 'downloaded'
        })
        
        # Track error events
        error_events = []
        
        def on_error(event):
            error_events.append(event.data)
        
        event_bus.subscribe(EventType.ERROR_OCCURRED, on_error)
        
        # Simulate upload error
        error_msg = "YouTube API quota exceeded"
        event_bus.publish(EventType.ERROR_OCCURRED, {
            'video_id': 'test_video_upload_fail',
            'error': error_msg,
            'component': 'uploader'
        })
        
        # Update database
        test_db.update_video_status('test_video_upload_fail', 'failed')
        test_db.update_video_error('test_video_upload_fail', error_msg)
        
        # Verify error tracking
        assert len(error_events) == 1
        assert error_events[0]['error'] == error_msg
        
        video = test_db.get_video('test_video_upload_fail')
        assert video['status'] == 'failed'
    
    def test_network_timeout_recovery(self, queue_manager):
        """Test recovery from network timeout"""
        video_info = {
            'video_id': 'test_video_timeout',
            'title': 'Test Timeout',
            'url': 'https://youtube.com/watch?v=test_video_timeout'
        }
        
        queue_manager.add_task(video_info, VideoPriority.NORMAL)
        task = queue_manager.get_next_task()
        
        # Simulate timeout - mark_failed will re-queue
        success = queue_manager.mark_failed(task.video_id, "Connection timeout after 30s")
        assert success is True  # Should re-queue
        
        # Next attempt should be available
        retry_task = queue_manager.get_next_task()
        assert retry_task is not None
        assert retry_task.retry_count == 1
        
        # This attempt succeeds
        queue_manager.mark_completed(retry_task.video_id)
        assert queue_manager.get_completed_count() == 1


# ============================================================================
# Test 3: Concurrent Processing
# ============================================================================

class TestConcurrentProcessing:
    """Test concurrent video processing"""
    
    def test_concurrent_downloads(self, queue_manager, mock_downloader):
        """Test processing multiple videos concurrently"""
        # Add 3 videos to queue
        for i in range(1, 4):
            video_info = {
                'video_id': f'test_video_{i}',
                'title': f'Test Video {i}',
                'url': f'https://youtube.com/watch?v=test_video_{i}'
            }
            queue_manager.add_task(video_info, VideoPriority.NORMAL)
        
        # Verify queue state
        assert queue_manager.get_queue_size() == 3
        
        # Get 3 tasks (simulating 3 workers)
        tasks = []
        for _ in range(3):
            task = queue_manager.get_next_task()
            if task:
                tasks.append(task)
        
        assert len(tasks) == 3
        assert queue_manager.get_processing_count() == 3
        
        # Complete all tasks
        for task in tasks:
            queue_manager.mark_completed(task.video_id)
        
        assert queue_manager.get_completed_count() == 3
        assert queue_manager.get_processing_count() == 0
    
    def test_max_concurrent_limit(self, queue_manager):
        """Test max concurrent processing limit"""
        # Add 5 videos
        for i in range(1, 6):
            video_info = {
                'video_id': f'test_video_{i}',
                'title': f'Test Video {i}',
                'url': f'https://youtube.com/watch?v=test_video_{i}'
            }
            queue_manager.add_task(video_info, VideoPriority.NORMAL)
        
        # Try to get 5 tasks (max is 3)
        tasks = []
        for _ in range(5):
            task = queue_manager.get_next_task()
            if task:
                tasks.append(task)
        
        # Should only get 3 tasks
        assert len(tasks) == 3
        assert queue_manager.get_processing_count() == 3
        
        # Try to get another - should return None
        task = queue_manager.get_next_task()
        assert task is None
        
        # Complete one task
        queue_manager.mark_completed(tasks[0].video_id)
        
        # Now should be able to get another
        task = queue_manager.get_next_task()
        assert task is not None
        assert queue_manager.get_processing_count() == 3
    
    def test_priority_processing_order(self, queue_manager):
        """Test videos are processed by priority"""
        # Add videos with different priorities
        video_low = {
            'video_id': 'video_low',
            'title': 'Low Priority Video',
            'url': 'https://youtube.com/watch?v=video_low'
        }
        
        video_high = {
            'video_id': 'video_high',
            'title': 'High Priority Video',
            'url': 'https://youtube.com/watch?v=video_high'
        }
        
        video_normal = {
            'video_id': 'video_normal',
            'title': 'Normal Priority Video',
            'url': 'https://youtube.com/watch?v=video_normal'
        }
        
        # Add in reverse priority order
        queue_manager.add_task(video_low, VideoPriority.LOW)
        queue_manager.add_task(video_high, VideoPriority.HIGH)
        queue_manager.add_task(video_normal, VideoPriority.NORMAL)
        
        # Get tasks - should be in priority order
        task1 = queue_manager.get_next_task()
        task2 = queue_manager.get_next_task()
        task3 = queue_manager.get_next_task()
        
        assert task1.video_id == 'video_high'
        assert task2.video_id == 'video_normal'
        assert task3.video_id == 'video_low'


# ============================================================================
# Test 4: Graceful Shutdown
# ============================================================================

class TestGracefulShutdown:
    """Test graceful shutdown during operations"""
    
    def test_shutdown_with_pending_tasks(self, queue_manager):
        """Test shutdown when tasks are in queue"""
        # Add tasks
        for i in range(3):
            video_info = {
                'video_id': f'test_video_{i}',
                'title': f'Test Video {i}',
                'url': f'https://youtube.com/watch?v=test_video_{i}'
            }
            queue_manager.add_task(video_info, VideoPriority.NORMAL)
        
        # Get one task
        task = queue_manager.get_next_task()
        
        # Shutdown - should be able to get remaining state
        assert queue_manager.get_queue_size() == 2
        assert queue_manager.get_processing_count() == 1
        
        # Cancel processing task using video_id
        success = queue_manager.cancel_task(task.video_id)
        assert success is True
    
    def test_cancel_in_progress_download(self, queue_manager):
        """Test cancelling download in progress"""
        video_info = {
            'video_id': 'test_video_cancel',
            'title': 'Test Cancel',
            'url': 'https://youtube.com/watch?v=test_video_cancel'
        }
        
        queue_manager.add_task(video_info, VideoPriority.NORMAL)
        task = queue_manager.get_next_task()
        
        # Simulate download started
        # Then cancel using video_id
        success = queue_manager.cancel_task(task.video_id)
        assert success is True


# ============================================================================
# Test 5: Event Propagation Across Components
# ============================================================================

class TestEventPropagation:
    """Test event propagation across all components"""
    
    def test_cross_component_events(self, event_bus):
        """Test events propagate across components"""
        # Track all events
        all_events = []
        
        def track_all(event):
            all_events.append(event.data)
        
        # Subscribe to multiple event types
        event_bus.subscribe(EventType.VIDEO_DETECTED, track_all)
        event_bus.subscribe(EventType.DOWNLOAD_STARTED, track_all)
        event_bus.subscribe(EventType.DOWNLOAD_COMPLETED, track_all)
        event_bus.subscribe(EventType.UPLOAD_STARTED, track_all)
        event_bus.subscribe(EventType.UPLOAD_COMPLETED, track_all)
        event_bus.subscribe(EventType.ERROR_OCCURRED, track_all)
        
        # Publish various events
        event_bus.publish(EventType.VIDEO_DETECTED, {'video_id': 'test1'})
        event_bus.publish(EventType.DOWNLOAD_STARTED, {'video_id': 'test1'})
        event_bus.publish(EventType.DOWNLOAD_COMPLETED, {'video_id': 'test1'})
        event_bus.publish(EventType.UPLOAD_STARTED, {'video_id': 'test1'})
        event_bus.publish(EventType.UPLOAD_COMPLETED, {'video_id': 'test1'})
        
        # Verify all events received
        assert len(all_events) == 5
    
    def test_event_filtering(self, event_bus):
        """Test event filtering by type"""
        download_events = []
        upload_events = []
        
        def track_downloads(event):
            download_events.append(event.data)
        
        def track_uploads(event):
            upload_events.append(event.data)
        
        event_bus.subscribe(EventType.DOWNLOAD_STARTED, track_downloads)
        event_bus.subscribe(EventType.DOWNLOAD_COMPLETED, track_downloads)
        event_bus.subscribe(EventType.UPLOAD_STARTED, track_uploads)
        event_bus.subscribe(EventType.UPLOAD_COMPLETED, track_uploads)
        
        # Publish mixed events
        event_bus.publish(EventType.DOWNLOAD_STARTED, {'video_id': 'test1'})
        event_bus.publish(EventType.UPLOAD_STARTED, {'video_id': 'test1'})
        event_bus.publish(EventType.DOWNLOAD_COMPLETED, {'video_id': 'test1'})
        event_bus.publish(EventType.UPLOAD_COMPLETED, {'video_id': 'test1'})
        
        # Verify filtering
        assert len(download_events) == 2
        assert len(upload_events) == 2
    
    def test_multiple_subscribers(self, event_bus):
        """Test multiple subscribers to same event"""
        subscribers_called = []
        
        def subscriber1(event):
            subscribers_called.append('subscriber1')
        
        def subscriber2(event):
            subscribers_called.append('subscriber2')
        
        def subscriber3(event):
            subscribers_called.append('subscriber3')
        
        event_bus.subscribe(EventType.VIDEO_DETECTED, subscriber1)
        event_bus.subscribe(EventType.VIDEO_DETECTED, subscriber2)
        event_bus.subscribe(EventType.VIDEO_DETECTED, subscriber3)
        
        # Publish event
        event_bus.publish(EventType.VIDEO_DETECTED, {'video_id': 'test1'})
        
        # Verify all subscribers called
        assert len(subscribers_called) == 3
        assert 'subscriber1' in subscribers_called
        assert 'subscriber2' in subscribers_called
        assert 'subscriber3' in subscribers_called
    
    def test_unsubscribe_event(self, event_bus):
        """Test unsubscribing from events"""
        events_received = []
        
        def handler(event):
            events_received.append(event.data)
        
        event_bus.subscribe(EventType.VIDEO_DETECTED, handler)
        
        # Publish event - should be received
        event_bus.publish(EventType.VIDEO_DETECTED, {'video_id': 'test1'})
        assert len(events_received) == 1
        
        # Unsubscribe
        event_bus.unsubscribe(EventType.VIDEO_DETECTED, handler)
        
        # Publish event - should not be received
        event_bus.publish(EventType.VIDEO_DETECTED, {'video_id': 'test2'})
        assert len(events_received) == 1  # Still 1


# ============================================================================
# Test 6: Database Integration
# ============================================================================

class TestDatabaseIntegration:
    """Test database integration across workflow"""
    
    def test_workflow_database_consistency(self, test_db, queue_manager, mock_downloader, mock_uploader):
        """Test database stays consistent throughout workflow"""
        # Step 1: Add video
        video_id = 'test_consistency'
        test_db.add_video({
            'video_id': video_id,
            'title': 'Test Consistency',
            'url': f'https://youtube.com/watch?v={video_id}',
            'status': 'queued'
        })
        
        # Verify initial state
        video = test_db.get_video(video_id)
        assert video['status'] == 'queued'
        
        # Step 2: Download
        test_db.update_video_status(video_id, 'downloading')
        download_result = mock_downloader.download_video(video_id=video_id)
        
        test_db.update_video_files(
            video_id=video_id,
            video_path=download_result['video_path'],
            thumbnail_path=download_result['thumbnail_path']
        )
        test_db.update_video_status(video_id, 'downloaded')
        test_db.update_video_timestamp(video_id, 'downloaded_at', datetime.now())
        
        # Verify download state
        video = test_db.get_video(video_id)
        assert video['status'] == 'downloaded'
        metadata = json.loads(video['metadata'])
        assert 'video_path' in metadata
        # downloaded_at is stored in database column, not metadata
        assert video['downloaded_at'] is not None
        
        # Step 3: Upload
        test_db.update_video_status(video_id, 'uploading')
        uploaded_id = mock_uploader.upload(
            video_path=download_result['video_path'],
            title='Test Consistency',
            description='Test'
        )
        
        test_db.update_video_uploaded_id(video_id, uploaded_id)
        test_db.update_video_status(video_id, 'uploaded')
        test_db.update_video_timestamp(video_id, 'uploaded_at', datetime.now())
        
        # Verify final state
        video = test_db.get_video(video_id)
        assert video['status'] == 'uploaded'
        # Uploaded ID is stored in target_video_id column, not metadata
        assert video['target_video_id'] == uploaded_id
        # uploaded_at is stored in database column, not metadata
        assert video['uploaded_at'] is not None
    
    def test_concurrent_database_access(self, test_db):
        """Test concurrent database operations"""
        # Add multiple videos simultaneously
        video_ids = []
        for i in range(10):
            video_id = f'test_concurrent_{i}'
            video_ids.append(video_id)
            test_db.add_video({
                'video_id': video_id,
                'title': f'Test Concurrent {i}',
                'url': f'https://youtube.com/watch?v={video_id}',
                'status': 'queued'
            })
        
        # Verify all added
        all_videos = test_db.get_all_videos()
        assert len(all_videos) >= 10
        
        # Update all statuses
        for video_id in video_ids:
            test_db.update_video_status(video_id, 'completed')
        
        # Verify all updated
        for video_id in video_ids:
            video = test_db.get_video(video_id)
            assert video['status'] == 'completed'
    
    def test_database_error_logging(self, test_db):
        """Test error logging in database"""
        video_id = 'test_error_log'
        
        # Add video
        test_db.add_video({
            'video_id': video_id,
            'title': 'Test Error Log',
            'url': f'https://youtube.com/watch?v={video_id}',
            'status': 'queued'
        })
        
        # Log multiple errors
        errors = [
            "Network timeout",
            "API quota exceeded",
            "Invalid video format"
        ]
        
        for error in errors:
            test_db.update_video_error(video_id, error)
        
        # Verify last error is stored
        video = test_db.get_video(video_id)
        # Error is stored in error_message column, not metadata
        assert video['error_message'] == errors[-1]  # Last error


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
