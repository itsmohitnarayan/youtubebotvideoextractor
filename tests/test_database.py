"""
Test suite for database manager.
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.database import DatabaseManager


class TestDatabaseManager:
    """Tests for DatabaseManager class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup - wait a bit for Windows to release file handles
        import time
        time.sleep(0.1)
        try:
            shutil.rmtree(temp_dir)
        except PermissionError:
            # If still locked, try again after a longer wait
            time.sleep(0.5)
            try:
                shutil.rmtree(temp_dir)
            except:
                pass  # Ignore if still can't delete
    
    @pytest.fixture
    def db_manager(self, temp_dir):
        """Create DatabaseManager instance with temp database."""
        db_path = Path(temp_dir) / "test.db"
        manager = DatabaseManager(db_path=str(db_path))
        yield manager
        # Explicitly close connection before cleanup
        manager.close()
    
    @pytest.fixture
    def sample_video_data(self):
        """Sample video data for testing."""
        return {
            "video_id": "dQw4w9WgXcQ",
            "title": "Test Video Title",
            "description": "Test video description",
            "published_at": "2025-11-10T10:00:00Z",
            "thumbnail_url": "https://example.com/thumb.jpg",
            "status": "pending",
            "metadata": {"duration": 240, "views": 1000}
        }
    
    def test_init_database(self, db_manager):
        """Test database initialization."""
        assert db_manager.connection is not None
        assert db_manager.db_path.exists()
        
        # Verify tables exist
        cursor = db_manager.connection.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [row[0] for row in cursor.fetchall()]
        
        assert "videos" in tables
        assert "logs" in tables
        assert "stats" in tables
        assert "settings" in tables
    
    def test_add_video(self, db_manager, sample_video_data):
        """Test adding video record."""
        video_id = db_manager.add_video(sample_video_data)
        
        assert video_id is not None
        assert video_id > 0
        
        # Verify video was added
        video = db_manager.get_video(sample_video_data["video_id"])
        assert video is not None
        assert video["source_video_id"] == sample_video_data["video_id"]
        assert video["source_title"] == sample_video_data["title"]
    
    def test_add_duplicate_video(self, db_manager, sample_video_data):
        """Test adding duplicate video returns None."""
        # Add first time
        video_id1 = db_manager.add_video(sample_video_data)
        assert video_id1 is not None
        
        # Try to add again
        video_id2 = db_manager.add_video(sample_video_data)
        assert video_id2 is None
    
    def test_is_video_processed(self, db_manager, sample_video_data):
        """Test duplicate detection (O(1) lookup)."""
        # Not processed yet
        assert db_manager.is_video_processed("dQw4w9WgXcQ") is False
        
        # Add video
        db_manager.add_video(sample_video_data)
        
        # Now it's processed
        assert db_manager.is_video_processed("dQw4w9WgXcQ") is True
    
    def test_get_video(self, db_manager, sample_video_data):
        """Test retrieving video by ID."""
        # Add video
        db_manager.add_video(sample_video_data)
        
        # Retrieve it
        video = db_manager.get_video(sample_video_data["video_id"])
        
        assert video is not None
        assert video["source_video_id"] == sample_video_data["video_id"]
        assert video["source_title"] == sample_video_data["title"]
        assert video["source_description"] == sample_video_data["description"]
        assert video["status"] == "pending"
    
    def test_get_nonexistent_video(self, db_manager):
        """Test retrieving non-existent video returns None."""
        video = db_manager.get_video("nonexistent_id")
        assert video is None
    
    def test_update_video_status(self, db_manager, sample_video_data):
        """Test updating video status."""
        # Add video
        db_manager.add_video(sample_video_data)
        
        # Update status
        result = db_manager.update_video_status(
            sample_video_data["video_id"],
            "downloading"
        )
        assert result is True
        
        # Verify update
        video = db_manager.get_video(sample_video_data["video_id"])
        assert video["status"] == "downloading"
    
    def test_update_video_status_with_fields(self, db_manager, sample_video_data):
        """Test updating video status with additional fields."""
        # Add video
        db_manager.add_video(sample_video_data)
        
        # Update with additional fields
        result = db_manager.update_video_status(
            sample_video_data["video_id"],
            "completed",
            target_video_id="ABC123",
            target_url="https://youtube.com/watch?v=ABC123"
        )
        assert result is True
        
        # Verify updates
        video = db_manager.get_video(sample_video_data["video_id"])
        assert video["status"] == "completed"
        assert video["target_video_id"] == "ABC123"
        assert video["target_url"] == "https://youtube.com/watch?v=ABC123"
    
    def test_update_nonexistent_video(self, db_manager):
        """Test updating non-existent video returns False."""
        result = db_manager.update_video_status("nonexistent", "completed")
        assert result is False
    
    def test_get_recent_videos(self, db_manager):
        """Test retrieving recent videos."""
        # Add multiple videos with small delays to ensure different timestamps
        import time
        for i in range(5):
            video_data = {
                "video_id": f"video_{i}",
                "title": f"Video {i}",
                "status": "pending"
            }
            db_manager.add_video(video_data)
            time.sleep(0.01)  # Small delay to ensure different timestamps
        
        # Get recent videos (limit 3)
        recent = db_manager.get_recent_videos(limit=3)
        
        assert len(recent) == 3
        # Should be in reverse chronological order (most recent first)
        assert recent[0]["source_video_id"] == "video_4"
        assert recent[1]["source_video_id"] == "video_3"
        assert recent[2]["source_video_id"] == "video_2"
    
    def test_get_stats_today(self, db_manager):
        """Test retrieving today's statistics."""
        stats = db_manager.get_stats_today()
        
        assert "videos_detected" in stats
        assert "videos_downloaded" in stats
        assert "videos_uploaded" in stats
        assert "errors_count" in stats
        
        # Default values
        assert stats["videos_detected"] == 0
        assert stats["videos_downloaded"] == 0
    
    def test_increment_stat(self, db_manager):
        """Test incrementing statistics."""
        # Increment detected videos
        db_manager.increment_stat("videos_detected", 1)
        db_manager.increment_stat("videos_detected", 2)
        
        stats = db_manager.get_stats_today()
        assert stats["videos_detected"] == 3
        
        # Increment downloaded videos
        db_manager.increment_stat("videos_downloaded", 1)
        stats = db_manager.get_stats_today()
        assert stats["videos_downloaded"] == 1
    
    def test_add_log(self, db_manager):
        """Test adding log entry."""
        db_manager.add_log(
            level="INFO",
            message="Test log message",
            module="test_module",
            details="Additional details",
            video_id="test_video_id"
        )
        
        # Verify log was added
        cursor = db_manager.connection.cursor()
        cursor.execute("SELECT * FROM logs WHERE message = ?", ("Test log message",))
        log = cursor.fetchone()
        
        assert log is not None
        assert log["level"] == "INFO"
        assert log["module"] == "test_module"
    
    def test_database_persistence(self, temp_dir):
        """Test database persists after closing."""
        db_path = Path(temp_dir) / "persistent.db"
        
        # Create database and add video
        db1 = DatabaseManager(db_path=str(db_path))
        db1.add_video({
            "video_id": "persist_test",
            "title": "Persistence Test",
            "status": "pending"
        })
        db1.close()
        
        # Reopen database and verify data exists
        db2 = DatabaseManager(db_path=str(db_path))
        video = db2.get_video("persist_test")
        
        assert video is not None
        assert video["source_title"] == "Persistence Test"
        db2.close()
    
    def test_video_status_transitions(self, db_manager, sample_video_data):
        """Test complete video status workflow."""
        # Add video (pending)
        db_manager.add_video(sample_video_data)
        video = db_manager.get_video(sample_video_data["video_id"])
        assert video["status"] == "pending"
        
        # Start downloading
        db_manager.update_video_status(
            sample_video_data["video_id"],
            "downloading",
            downloaded_at=datetime.now().isoformat()
        )
        video = db_manager.get_video(sample_video_data["video_id"])
        assert video["status"] == "downloading"
        assert video["downloaded_at"] is not None
        
        # Complete download
        db_manager.update_video_status(
            sample_video_data["video_id"],
            "downloaded"
        )
        
        # Start uploading
        db_manager.update_video_status(
            sample_video_data["video_id"],
            "uploading"
        )
        video = db_manager.get_video(sample_video_data["video_id"])
        assert video["status"] == "uploading"
        
        # Complete
        db_manager.update_video_status(
            sample_video_data["video_id"],
            "completed",
            uploaded_at=datetime.now().isoformat(),
            target_video_id="XYZ789"
        )
        video = db_manager.get_video(sample_video_data["video_id"])
        assert video["status"] == "completed"
        assert video["uploaded_at"] is not None
        assert video["target_video_id"] == "XYZ789"
    
    def test_error_handling_invalid_status(self, db_manager, sample_video_data):
        """Test updating video with error status."""
        db_manager.add_video(sample_video_data)
        
        db_manager.update_video_status(
            sample_video_data["video_id"],
            "failed",
            error_message="Download failed: Network timeout"
        )
        
        video = db_manager.get_video(sample_video_data["video_id"])
        assert video["status"] == "failed"
        assert "Network timeout" in video["error_message"]
    
    def test_update_video_files(self, db_manager, sample_video_data):
        """Test updating video file paths."""
        db_manager.add_video(sample_video_data)
        
        success = db_manager.update_video_files(
            sample_video_data["video_id"],
            "/path/to/video.mp4",
            "/path/to/thumbnail.jpg"
        )
        
        assert success is True
        
        video = db_manager.get_video(sample_video_data["video_id"])
        metadata = video.get("metadata")
        if isinstance(metadata, str):
            import json
            metadata = json.loads(metadata)
        
        assert metadata["video_path"] == "/path/to/video.mp4"
        assert metadata["thumbnail_path"] == "/path/to/thumbnail.jpg"
    
    def test_update_video_files_without_thumbnail(self, db_manager, sample_video_data):
        """Test updating video files without thumbnail."""
        db_manager.add_video(sample_video_data)
        
        success = db_manager.update_video_files(
            sample_video_data["video_id"],
            "/path/to/video.mp4"
        )
        
        assert success is True
        
        video = db_manager.get_video(sample_video_data["video_id"])
        metadata = video.get("metadata")
        if isinstance(metadata, str):
            import json
            metadata = json.loads(metadata)
        
        assert metadata["video_path"] == "/path/to/video.mp4"
        assert "thumbnail_path" not in metadata
    
    def test_update_video_error(self, db_manager, sample_video_data):
        """Test updating video error message."""
        db_manager.add_video(sample_video_data)
        
        error_msg = "Upload failed: Quota exceeded"
        success = db_manager.update_video_error(
            sample_video_data["video_id"],
            error_msg
        )
        
        assert success is True
        
        video = db_manager.get_video(sample_video_data["video_id"])
        assert video["error_message"] == error_msg
    
    def test_update_video_uploaded_id(self, db_manager, sample_video_data):
        """Test updating uploaded video ID."""
        db_manager.add_video(sample_video_data)
        
        uploaded_id = "xyz789"
        success = db_manager.update_video_uploaded_id(
            sample_video_data["video_id"],
            uploaded_id
        )
        
        assert success is True
        
        video = db_manager.get_video(sample_video_data["video_id"])
        assert video["target_video_id"] == uploaded_id
        assert video["target_url"] == f"https://youtube.com/watch?v={uploaded_id}"
    
    def test_update_video_timestamp(self, db_manager, sample_video_data):
        """Test updating video timestamp."""
        db_manager.add_video(sample_video_data)
        
        timestamp = datetime(2025, 11, 10, 15, 30, 0)
        success = db_manager.update_video_timestamp(
            sample_video_data["video_id"],
            "downloaded_at",
            timestamp
        )
        
        assert success is True
        
        video = db_manager.get_video(sample_video_data["video_id"])
        assert video["downloaded_at"] == timestamp.isoformat()
    
    def test_update_video_timestamp_invalid_field(self, db_manager, sample_video_data):
        """Test updating with invalid timestamp field."""
        db_manager.add_video(sample_video_data)
        
        timestamp = datetime.now()
        success = db_manager.update_video_timestamp(
            sample_video_data["video_id"],
            "invalid_field",  # Not in allowed list
            timestamp
        )
        
        assert success is False
    
    def test_update_nonexistent_video_files(self, db_manager):
        """Test updating files for non-existent video."""
        success = db_manager.update_video_files(
            "nonexistent123",
            "/path/to/video.mp4"
        )
        
        assert success is False
    
    def test_update_nonexistent_video_error(self, db_manager):
        """Test updating error for non-existent video."""
        success = db_manager.update_video_error(
            "nonexistent123",
            "Some error"
        )
        
        assert success is False

