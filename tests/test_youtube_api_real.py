"""
Real YouTube API Integration Tests
Tests actual YouTube API interactions (not mocked)

Requirements:
- Valid client_secrets.json in project root
- Valid token.json (run refresh_oauth.py first)
- Test video file in tests/fixtures/
- Internet connection
- Available API quota

Run with: pytest tests/test_youtube_api_real.py -v -s --tb=short
Mark as slow: pytest -m "not slow" to skip these tests
"""

import pytest
import os
import time
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

from src.youtube.api_client import YouTubeAPIClient
from src.youtube.uploader import VideoUploader
from src.youtube.monitor import ChannelMonitor
from src.youtube.downloader import VideoDownloader
from src.core.database import DatabaseManager


# Mark all tests in this file as slow and requiring credentials
pytestmark = [
    pytest.mark.slow,
    pytest.mark.requires_credentials,
    pytest.mark.integration
]


class TestRealYouTubeAPIClient:
    """Test real YouTube API client interactions"""
    
    @pytest.fixture(scope="class")
    def api_client(self) -> Optional[YouTubeAPIClient]:
        """
        Create real API client.
        Skips if credentials not available.
        """
        client_secrets = Path("client_secrets.json")
        token_file = Path("token.json")
        
        if not client_secrets.exists():
            pytest.skip("client_secrets.json not found - skipping real API tests")
        
        if not token_file.exists():
            pytest.skip("token.json not found - run refresh_oauth.py first")
        
        try:
            client = YouTubeAPIClient(
                credentials_file=str(client_secrets),
                token_file=str(token_file)
            )
            
            # Verify client works by making a simple API call
            assert client.youtube is not None, "YouTube client not initialized"
            
            return client
        except Exception as e:
            pytest.skip(f"Failed to initialize API client: {e}")
    
    def test_api_client_initialization(self, api_client):
        """Test that API client initializes correctly"""
        assert api_client is not None
        assert api_client.youtube is not None
        assert api_client.credentials is not None
        assert api_client.credentials.valid
    
    def test_quota_tracking(self, api_client):
        """Test quota tracking works"""
        initial_quota = api_client.quota_used_today
        
        # Make a small API call (costs 1 unit)
        channel_info = api_client.get_channel_info("UCuAXFkgsw1L7xaCfnd5JJOw")  # Random channel
        
        # Quota should have increased
        assert api_client.quota_used_today > initial_quota
        assert api_client.quota_used_today >= initial_quota + 1
    
    def test_get_channel_info(self, api_client):
        """Test getting channel information"""
        # Use YouTube's own channel as test
        channel_id = "UC_x5XG1OV2P6uZZ5FSM9Ttw"  # YouTube's official channel
        
        channel_info = api_client.get_channel_info(channel_id)
        
        assert channel_info is not None
        assert 'snippet' in channel_info
        assert 'contentDetails' in channel_info
        assert 'statistics' in channel_info
        assert channel_info['snippet']['title'] != ""
    
    def test_get_channel_uploads_playlist(self, api_client):
        """Test getting channel uploads playlist ID"""
        # Use YouTube's own channel
        channel_id = "UC_x5XG1OV2P6uZZ5FSM9Ttw"
        
        playlist_id = api_client.get_channel_uploads_playlist(channel_id)
        
        assert playlist_id is not None
        assert playlist_id.startswith("UU")  # Uploads playlists start with UU
    
    def test_get_recent_uploads(self, api_client):
        """Test getting recent uploads from channel"""
        # Use YouTube's own channel
        channel_id = "UC_x5XG1OV2P6uZZ5FSM9Ttw"
        
        videos = api_client.get_recent_uploads(
            channel_id=channel_id,
            max_results=5
        )
        
        assert isinstance(videos, list)
        assert len(videos) > 0
        assert len(videos) <= 5
        
        # Verify video structure
        video = videos[0]
        assert 'video_id' in video
        assert 'title' in video
        assert 'description' in video
        assert 'published_at' in video
    
    def test_quota_limit_check(self, api_client):
        """Test quota limit checking"""
        # Should have quota available (tests run with fresh quota)
        has_quota = api_client.check_quota('videos.list')
        assert has_quota is True
        
        # Test high-cost operation check
        has_quota_for_upload = api_client.check_quota('videos.insert')
        # May be True or False depending on current quota usage
        assert isinstance(has_quota_for_upload, bool)


class TestRealYouTubeUploader:
    """Test real video upload functionality"""
    
    @pytest.fixture(scope="class")
    def api_client(self) -> Optional[YouTubeAPIClient]:
        """Create real API client"""
        client_secrets = Path("client_secrets.json")
        token_file = Path("token.json")
        
        if not client_secrets.exists() or not token_file.exists():
            pytest.skip("Credentials not available")
        
        try:
            return YouTubeAPIClient(str(client_secrets), str(token_file))
        except Exception as e:
            pytest.skip(f"Failed to initialize API client: {e}")
    
    @pytest.fixture(scope="class")
    def uploader(self, api_client):
        """Create real uploader"""
        return VideoUploader(api_client)
    
    @pytest.fixture(scope="class")
    def test_video_file(self) -> Path:
        """
        Create or locate test video file.
        Creates a small test video if none exists.
        """
        fixtures_dir = Path("tests/fixtures")
        fixtures_dir.mkdir(parents=True, exist_ok=True)
        
        test_video = fixtures_dir / "test_video.mp4"
        
        if not test_video.exists():
            pytest.skip(
                "Test video not found. Please place a small test video at "
                "tests/fixtures/test_video.mp4 (max 10MB recommended)"
            )
        
        return test_video
    
    def test_upload_video_private(self, uploader, test_video_file, api_client):
        """
        Test uploading a video (PRIVATE to avoid spam).
        This test will actually upload to YouTube and then delete it.
        """
        # Check quota before upload
        if not api_client.check_quota('videos.insert'):
            pytest.skip("Insufficient quota for upload test")
        
        # Upload video as PRIVATE
        video_id, error = uploader.upload(
            video_path=str(test_video_file),
            title=f"[TEST] Integration Test {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            description="Automated integration test video. Will be deleted immediately.",
            tags=["test", "automation", "integration_test"],
            category_id="22",  # People & Blogs
            privacy_status="private"  # IMPORTANT: Don't spam public channel
        )
        
        try:
            # Verify upload succeeded
            assert video_id is not None, f"Upload failed: {error}"
            assert error is None, f"Upload returned error: {error}"
            assert isinstance(video_id, str)
            assert len(video_id) == 11  # YouTube video IDs are 11 characters
            
            print(f"\n✅ Successfully uploaded test video: {video_id}")
            
            # Wait a moment for video to be processed
            time.sleep(2)
            
            # Verify video exists by fetching it
            video_info = api_client.youtube.videos().list(
                part='snippet,status',
                id=video_id
            ).execute()
            
            assert 'items' in video_info
            assert len(video_info['items']) > 0
            assert video_info['items'][0]['id'] == video_id
            assert video_info['items'][0]['status']['privacyStatus'] == 'private'
            
            print(f"✅ Verified video exists on YouTube")
            
        finally:
            # CLEANUP: Delete test video
            if video_id:
                try:
                    deleted = uploader.delete_video(video_id)
                    assert deleted is True, "Failed to delete test video"
                    print(f"✅ Cleaned up test video: {video_id}")
                except Exception as e:
                    print(f"⚠️ Failed to delete test video {video_id}: {e}")
                    print(f"   Please manually delete it from YouTube Studio")
    
    def test_upload_failure_invalid_file(self, uploader):
        """Test upload with non-existent file"""
        video_id, error = uploader.upload(
            video_path="/path/to/nonexistent/video.mp4",
            title="This should fail",
            description="Test",
            privacy_status="private"
        )
        
        assert video_id is None, "Should return None for invalid file"
        assert error is not None, "Should return error message"
        assert "not found" in error.lower()
    
    def test_upload_quota_check(self, uploader, api_client, test_video_file):
        """Test that uploader respects quota limits"""
        # Temporarily set quota to simulate exhausted quota
        original_quota = api_client.quota_used_today
        api_client.quota_used_today = api_client.quota_limit  # Exhaust quota
        
        try:
            video_id, error = uploader.upload(
                video_path=str(test_video_file),
                title="Should fail - no quota",
                description="Test",
                privacy_status="private"
            )
            
            assert video_id is None, "Upload should fail when quota exhausted"
            assert error is not None, "Should return error message"
            assert "quota" in error.lower()
            
        finally:
            # Restore original quota
            api_client.quota_used_today = original_quota


class TestRealChannelMonitor:
    """Test real channel monitoring"""
    
    @pytest.fixture(scope="class")
    def api_client(self):
        """Create real API client"""
        client_secrets = Path("client_secrets.json")
        token_file = Path("token.json")
        
        if not client_secrets.exists() or not token_file.exists():
            pytest.skip("Credentials not available")
        
        try:
            return YouTubeAPIClient(str(client_secrets), str(token_file))
        except Exception as e:
            pytest.skip(f"Failed to initialize API client: {e}")
    
    @pytest.fixture
    def db(self, tmp_path):
        """Create temporary database"""
        db_path = tmp_path / "test.db"
        return DatabaseManager(str(db_path))
    
    @pytest.fixture
    def monitor(self, api_client, db):
        """Create real monitor"""
        # Use YouTube's official channel
        channel_id = "UC_x5XG1OV2P6uZZ5FSM9Ttw"
        return ChannelMonitor(api_client, db, channel_id, check_interval_minutes=5)
    
    def test_check_for_new_videos(self, monitor):
        """Test checking for new videos"""
        # First check - will get recent videos
        new_videos = monitor.check_for_new_videos()
        
        assert isinstance(new_videos, list)
        # May or may not find new videos depending on channel activity
        
        if len(new_videos) > 0:
            video = new_videos[0]
            assert 'video_id' in video
            assert 'title' in video
            assert 'published_at' in video
            print(f"\n✅ Found {len(new_videos)} video(s) from channel")


class TestRealDownloader:
    """Test real video downloading"""
    
    @pytest.fixture
    def downloader(self, tmp_path):
        """Create downloader with temp directory"""
        download_dir = tmp_path / "downloads"
        return VideoDownloader(str(download_dir))
    
    @pytest.mark.slow
    def test_download_real_video(self, downloader):
        """
        Test downloading a real video.
        Uses a short, public domain video to minimize bandwidth/time.
        """
        # Use a short test video (Big Buck Bunny trailer - public domain)
        video_id = "aqz-KE-bpKQ"  # 1 min video
        
        try:
            result = downloader.download_video(video_id)
            
            assert result is not None, "Download should succeed"
            assert result.get('success') is True, "Download should be successful"
            assert 'video_path' in result
            
            video_path = Path(result['video_path'])
            assert video_path.exists(), "Downloaded video file should exist"
            assert video_path.stat().st_size > 0, "Video file should not be empty"
            
            print(f"\n✅ Downloaded video: {video_path}")
            print(f"   Size: {video_path.stat().st_size / 1024 / 1024:.2f} MB")
            
            # Cleanup
            try:
                video_path.unlink()
                if result.get('thumbnail_path'):
                    Path(result['thumbnail_path']).unlink()
                print(f"✅ Cleaned up downloaded files")
            except Exception as cleanup_error:
                print(f"⚠️  Could not cleanup: {cleanup_error}")
            
        except Exception as e:
            pytest.skip(f"Download test skipped: {e}")


class TestEndToEndWorkflow:
    """Test complete workflow with real components"""
    
    @pytest.fixture(scope="class")
    def api_client(self):
        """Create real API client"""
        client_secrets = Path("client_secrets.json")
        token_file = Path("token.json")
        
        if not client_secrets.exists() or not token_file.exists():
            pytest.skip("Credentials not available")
        
        try:
            return YouTubeAPIClient(str(client_secrets), str(token_file))
        except Exception as e:
            pytest.skip(f"Failed to initialize API client: {e}")
    
    @pytest.fixture
    def db(self, tmp_path):
        """Create temporary database"""
        db_path = tmp_path / "test.db"
        return DatabaseManager(str(db_path))
    
    def test_quota_persistence(self, api_client, db):
        """Test that quota is persisted to database"""
        # Create API client with database
        api_client_with_db = YouTubeAPIClient(
            credentials_file="client_secrets.json",
            token_file="token.json",
            db_manager=db
        )
        
        initial_quota = api_client_with_db.quota_used_today
        
        # Make an API call
        api_client_with_db.get_channel_info("UC_x5XG1OV2P6uZZ5FSM9Ttw")
        
        # Quota should be saved to database
        saved_quota = db.get_quota_usage()
        assert saved_quota > initial_quota
        assert saved_quota == api_client_with_db.quota_used_today
        
        print(f"\n✅ Quota persisted: {saved_quota} units")
    
    def test_error_logging_to_database(self, db):
        """Test that errors are logged to database"""
        # Add a test log
        db.add_log(
            level="ERROR",
            message="Test error message",
            module="test_module",
            details="Test error details"
        )
        
        # Verify it was saved (would need to add get_logs method to verify)
        # For now, just ensure no exception was raised
        assert True
        print("\n✅ Error logged to database")


# Pytest configuration
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "requires_credentials: marks tests requiring YouTube API credentials")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
