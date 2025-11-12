"""Manual upload script to test video upload with refreshed OAuth"""
import sys
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from core.config import ConfigManager
from core.database import DatabaseManager
from youtube.api_client import YouTubeAPIClient
from youtube.uploader import VideoUploader
import sqlite3

def main():
    print("\n" + "="*80)
    print("🎥 MANUAL VIDEO UPLOAD TEST")
    print("="*80)
    
    # Load config
    config = ConfigManager()
    
    # Connect to database
    db_path = config.get('database.path', 'data/videos.db')
    db = DatabaseManager(db_path)
    
    # Get failed videos
    conn = sqlite3.connect('data/videos.db')
    cursor = conn.cursor()
    cursor.execute('SELECT source_video_id, source_title, status FROM videos WHERE status = "failed"')
    failed_videos = cursor.fetchall()
    conn.close()
    
    print(f"\n📋 Found {len(failed_videos)} failed videos")
    
    if not failed_videos:
        print("✅ No failed videos to retry")
        return
    
    # Show videos
    for i, (video_id, title, status) in enumerate(failed_videos, 1):
        print(f"\n{i}. {video_id}")
        print(f"   Title: {title[:70] if title else 'N/A'}")
    
    # Check for downloaded files
    video_id = None
    video_title = None
    video_file = None
    downloads_dir = Path('downloads')
    
    print(f"\n🔍 Looking for downloaded files...")
    
    # Check each failed video for downloaded file
    for vid_id, title, status in failed_videos:
        for session_dir in downloads_dir.glob('session_*'):
            for ext in ['.mp4', '.mkv', '.webm']:
                test_file = session_dir / f"{vid_id}{ext}"
                if test_file.exists():
                    video_id = vid_id
                    video_title = title
                    video_file = test_file
                    print(f"✅ Found: {video_file}")
                    print(f"   Size: {video_file.stat().st_size / (1024*1024):.1f} MB")
                    print(f"   Video ID: {video_id}")
                    break
            if video_file:
                break
        if video_file:
            break
    
    if not video_file:
        print(f"❌ No downloaded file found for any failed video")
        print(f"   Checked in: {downloads_dir}")
        return
    
    # Initialize YouTube API client
    print(f"\n🔑 Initializing YouTube API client...")
    client_secrets_file = config.get('youtube.client_secrets_file', 'client_secrets.json')
    token_file = config.get('youtube.token_file', 'token.json')
    
    api_client = YouTubeAPIClient(client_secrets_file, token_file, db)
    uploader = VideoUploader(api_client)
    
    print("✅ YouTube client initialized")
    
    # Attempt upload
    print(f"\n📤 Uploading video: {(video_title or 'Unknown')[:50]}...")
    print(f"   File: {video_file.name}")
    
    # Get metadata from the video file using yt-dlp info
    print(f"\n🔍 Extracting metadata from downloaded video...")
    
    # Check for .info.json file
    info_json_path = video_file.with_suffix('.info.json')
    tags = []
    category_id = '20'  # Gaming category (safe default)
    
    if info_json_path.exists():
        import json
        with open(info_json_path, 'r', encoding='utf-8') as f:
            info = json.load(f)
            tags = info.get('tags', [])
            categories = info.get('categories', [])
            if categories and len(categories) > 0:
                category_id = str(categories[0])
            original_description = info.get('description', '')
            print(f"✅ Found metadata: {len(tags)} tags, category: {category_id}")
    else:
        print(f"⚠️  No .info.json file found, using defaults")
        # Try to get description from database
        original_description = ''
        conn = sqlite3.connect('data/videos.db')
        cursor = conn.cursor()
        cursor.execute('SELECT source_description FROM videos WHERE source_video_id = ?', (video_id,))
        row = cursor.fetchone()
        if row and row[0]:
            original_description = row[0]
        conn.close()
    
    # Prepend custom message to original description
    final_description = f"Re-uploaded from MuFiJuL GaminG\n\n{original_description}"
    
    try:
        result = uploader.upload(
            video_path=str(video_file),
            title=video_title or "Untitled",
            description=final_description,
            tags=tags,  # Use original tags
            category_id=category_id,  # Use original category
            privacy_status="public"
        )
        
        # Result is tuple: (video_id, error_message)
        uploaded_id, error_message = result
        
        if uploaded_id:
            print(f"\n✅ Upload successful!")
            print(f"   Video ID: {uploaded_id}")
            print(f"   URL: https://www.youtube.com/watch?v={uploaded_id}")
            
            # Update database
            if video_id:
                db.update_video_uploaded_id(str(video_id), uploaded_id)
                print(f"✅ Database updated")
            
        else:
            print(f"\n❌ Upload failed: {error_message}")
            
    except Exception as e:
        print(f"\n❌ Upload error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
