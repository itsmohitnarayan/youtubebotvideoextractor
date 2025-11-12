"""
YouTube Integration Example
Demonstrates how Phase 2 modules work together.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from youtube.api_client import YouTubeAPIClient
from youtube.downloader import VideoDownloader
from youtube.uploader import VideoUploader
from youtube.monitor import ChannelMonitor
from core.database import DatabaseManager
from core.logger import setup_logger


def example_1_basic_download_upload():
    """Example 1: Download a video and upload it."""
    print("\n=== Example 1: Basic Download & Upload ===\n")
    
    # Setup
    logger = setup_logger("youtube_example", "logs/example.log")
    api_client = YouTubeAPIClient(
        credentials_file="config/client_secrets.json",
        token_file="config/token.pickle"
    )
    downloader = VideoDownloader(output_dir="downloads")
    uploader = VideoUploader(api_client)
    
    # Download video
    video_id = "dQw4w9WgXcQ"  # Example video ID
    print(f"Downloading video: {video_id}")
    
    result = downloader.download_video(
        video_id=video_id,
        quality='720p',
        download_thumbnail=True
    )
    
    if result['success']:
        print(f"✅ Downloaded: {result['title']}")
        print(f"   Video: {result['video_path']}")
        print(f"   Thumbnail: {result['thumbnail_path']}")
        print(f"   Size: {result['filesize'] / 1024 / 1024:.1f} MB")
        
        # Upload to target channel
        print("\nUploading to target channel...")
        
        uploaded_video_id = uploader.upload(
            video_path=result['video_path'],
            title=result['title'],
            description="Replicated video from source channel",
            tags=["replicated", "automated"],
            category_id="22",
            privacy_status="private",
            thumbnail_path=result['thumbnail_path']
        )
        
        if uploaded_video_id:
            print(f"✅ Uploaded successfully! Video ID: {uploaded_video_id}")
        else:
            print("❌ Upload failed")
    else:
        print(f"❌ Download failed: {result['error']}")


def example_2_channel_monitoring():
    """Example 2: Monitor a channel for new videos."""
    print("\n=== Example 2: Channel Monitoring ===\n")
    
    # Setup
    logger = setup_logger("monitoring_example", "logs/monitoring.log")
    api_client = YouTubeAPIClient(
        credentials_file="config/client_secrets.json",
        token_file="config/token.pickle"
    )
    database = DatabaseManager("data/videos.db")
    
    # Create monitor
    source_channel_id = "UC_x5XG1OV2P6uZZ5FSM9Ttw"  # Example channel
    monitor = ChannelMonitor(
        api_client=api_client,
        database=database,
        source_channel_id=source_channel_id,
        check_interval_minutes=5
    )
    
    # Get channel info
    channel_info = monitor.get_channel_info()
    if channel_info:
        print(f"Monitoring channel: {channel_info['snippet']['title']}")
        print(f"Subscribers: {channel_info['statistics']['subscriberCount']}")
        print(f"Videos: {channel_info['statistics']['videoCount']}\n")
    
    # Set up new video callback
    def on_new_video(video_info):
        print(f"\n🔔 New video detected!")
        print(f"   Title: {video_info['snippet']['title']}")
        print(f"   Published: {video_info['snippet']['publishedAt']}")
        print(f"   Video ID: {video_info['id']}")
        
        # Here you would trigger download & upload
        # For now, just log it
        print("   → Would trigger download & upload process")
    
    monitor.set_new_video_callback(on_new_video)
    
    # Check for new videos (one-time check)
    print("Checking for new videos...")
    new_videos = monitor.check_for_new_videos()
    print(f"Found {len(new_videos)} new video(s)")
    
    # To start continuous monitoring (blocking):
    # monitor.start_monitoring()


def example_3_metadata_extraction():
    """Example 3: Extract video metadata without downloading."""
    print("\n=== Example 3: Metadata Extraction ===\n")
    
    downloader = VideoDownloader(output_dir="downloads")
    
    video_id = "dQw4w9WgXcQ"
    print(f"Extracting metadata for: {video_id}\n")
    
    metadata = downloader.extract_metadata(video_id)
    
    if metadata:
        print(f"Title: {metadata['title']}")
        print(f"Uploader: {metadata['uploader']}")
        print(f"Duration: {metadata['duration']} seconds")
        print(f"Views: {metadata['view_count']:,}")
        print(f"Likes: {metadata['like_count']:,}")
        print(f"Tags: {', '.join(metadata['tags'][:5])}...")
        print(f"Resolution: {metadata['resolution']}")
        print(f"FPS: {metadata['fps']}")
    else:
        print("❌ Failed to extract metadata")


def example_4_quota_management():
    """Example 4: Check and track API quota usage."""
    print("\n=== Example 4: Quota Management ===\n")
    
    api_client = YouTubeAPIClient(
        credentials_file="config/client_secrets.json",
        token_file="config/token.pickle"
    )
    
    # Check current quota
    quota_info = api_client.get_quota_usage()
    print(f"Quota used: {quota_info['used']:,} / {quota_info['limit']:,} units")
    print(f"Remaining: {quota_info['remaining']:,} units")
    print(f"Percentage: {quota_info['percentage']:.1f}%")
    
    if quota_info['percentage'] > 95:
        print("⚠️  WARNING: Quota usage above 95%!")
    
    # Check if we can perform an upload (costs 1600 units)
    can_upload = api_client.check_quota(1600)
    print(f"\nCan upload video? {'✅ Yes' if can_upload else '❌ No (insufficient quota)'}")
    
    # Check if we can search (costs 100 units)
    can_search = api_client.check_quota(100)
    print(f"Can search channel? {'✅ Yes' if can_search else '❌ No (insufficient quota)'}")


def example_5_complete_replication_flow():
    """Example 5: Complete video replication workflow."""
    print("\n=== Example 5: Complete Replication Flow ===\n")
    
    # This demonstrates the full workflow:
    # Monitor → Detect → Download → Upload → Track
    
    logger = setup_logger("replication", "logs/replication.log")
    api_client = YouTubeAPIClient(
        credentials_file="config/client_secrets.json",
        token_file="config/token.pickle"
    )
    database = DatabaseManager("data/videos.db")
    downloader = VideoDownloader(output_dir="downloads")
    uploader = VideoUploader(api_client)
    
    source_channel_id = "UC_x5XG1OV2P6uZZ5FSM9Ttw"
    
    # Create monitor with replication callback
    monitor = ChannelMonitor(
        api_client=api_client,
        database=database,
        source_channel_id=source_channel_id,
        check_interval_minutes=15
    )
    
    def replicate_video(video_info):
        """Complete replication workflow."""
        video_id = video_info['id']
        title = video_info['snippet']['title']
        
        print(f"\n{'='*60}")
        print(f"Replicating: {title}")
        print(f"{'='*60}")
        
        # Step 1: Download
        print("\n[1/4] Downloading video...")
        download_result = downloader.download_video(
            video_id=video_id,
            quality='best',
            download_thumbnail=True
        )
        
        if not download_result['success']:
            print(f"❌ Download failed: {download_result['error']}")
            database.update_video_status(video_id, "download_failed")
            return
        
        print(f"✅ Downloaded ({download_result['filesize'] / 1024 / 1024:.1f} MB)")
        database.update_video_status(video_id, "downloaded")
        
        # Step 2: Upload
        print("\n[2/4] Uploading to target channel...")
        uploaded_id = uploader.upload(
            video_path=download_result['video_path'],
            title=title,
            description=video_info['snippet']['description'],
            tags=video_info['snippet'].get('tags', []),
            category_id=video_info['snippet']['categoryId'],
            privacy_status='private',  # Start as private
            thumbnail_path=download_result['thumbnail_path']
        )
        
        if not uploaded_id:
            print("❌ Upload failed")
            database.update_video_status(video_id, "upload_failed")
            return
        
        print(f"✅ Uploaded (Video ID: {uploaded_id})")
        
        # Step 3: Update database
        print("\n[3/4] Updating database...")
        database.update_video(
            video_id=video_id,
            replicated_video_id=uploaded_id,
            download_path=download_result['video_path'],
            status="completed"
        )
        print("✅ Database updated")
        
        # Step 4: Cleanup
        print("\n[4/4] Cleaning up temporary files...")
        downloader.cleanup_temp_files()
        print("✅ Cleanup complete")
        
        print(f"\n{'='*60}")
        print(f"✅ Replication complete!")
        print(f"   Original: {video_id}")
        print(f"   Replicated: {uploaded_id}")
        print(f"{'='*60}\n")
    
    # Set callback and check for new videos
    monitor.set_new_video_callback(replicate_video)
    
    print("Starting single check for new videos...")
    new_videos = monitor.check_for_new_videos()
    
    if new_videos:
        print(f"\nProcessed {len(new_videos)} new video(s)")
    else:
        print("\nNo new videos found")
    
    # To start continuous monitoring:
    # print("\nStarting continuous monitoring (Ctrl+C to stop)...")
    # monitor.start_monitoring()


if __name__ == "__main__":
    print("YouTube Integration Examples")
    print("=" * 60)
    
    # Run examples
    # Uncomment the ones you want to test
    
    # example_1_basic_download_upload()
    # example_2_channel_monitoring()
    # example_3_metadata_extraction()
    # example_4_quota_management()
    # example_5_complete_replication_flow()
    
    print("\n" + "=" * 60)
    print("Note: Update credentials and channel IDs before running")
    print("=" * 60)
