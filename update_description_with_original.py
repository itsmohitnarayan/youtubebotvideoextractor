"""Update description of already uploaded video to include original description"""
import sys
from pathlib import Path
import sqlite3

# Add src directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from core.config import ConfigManager
from core.database import DatabaseManager
from youtube.api_client import YouTubeAPIClient
from youtube.uploader import VideoUploader

def main():
    print("\n" + "="*80)
    print("🔄 UPDATE VIDEO DESCRIPTION WITH ORIGINAL")
    print("="*80)
    
    # Load config
    config = ConfigManager()
    
    # Connect to database
    db_path = config.get('database.path', 'data/videos.db')
    db = DatabaseManager(db_path)
    
    # Get original description from database
    conn = sqlite3.connect('data/videos.db')
    cursor = conn.cursor()
    cursor.execute('SELECT source_description FROM videos WHERE source_video_id = ?', ('jKZQyAAA6V0',))
    row = cursor.fetchone()
    conn.close()
    
    original_description = row[0] if row and row[0] else ""
    
    print(f"\n📝 Original description length: {len(original_description)} characters")
    if original_description:
        print(f"   Preview: {original_description[:100]}...")
    
    # Initialize YouTube API client
    print(f"\n🔑 Initializing YouTube API client...")
    client_secrets_file = config.get('youtube.client_secrets_file', 'client_secrets.json')
    token_file = config.get('youtube.token_file', 'token.json')
    
    api_client = YouTubeAPIClient(client_secrets_file, token_file, db)
    uploader = VideoUploader(api_client)
    
    print("✅ YouTube client initialized")
    
    # Update video description
    video_id = "e14dhh_s3as"
    new_description = f"Re-uploaded from MuFiJuL GaminG\n\n{original_description}"
    
    print(f"\n📝 Updating video {video_id}...")
    print(f"   New description: Re-uploaded from MuFiJuL GaminG + original ({len(original_description)} chars)")
    
    try:
        success = uploader.update_metadata(
            video_id=video_id,
            description=new_description
        )
        
        if success:
            print(f"\n✅ Description updated successfully!")
            print(f"   Video: https://www.youtube.com/watch?v={video_id}")
            print(f"   Now includes: 'Re-uploaded from MuFiJuL GaminG' + original description")
        else:
            print(f"\n❌ Failed to update description")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
