"""Fix corrupted database entries and check upload configuration"""
import sqlite3
from pathlib import Path

print("\n" + "="*80)
print("🔧 FIXING DATABASE + CHECKING UPLOAD CONFIGURATION")
print("="*80)

# Fix database
conn = sqlite3.connect('data/videos.db')
cursor = conn.cursor()

print("\n1️⃣ Fixing corrupted database entries...")
print("-"*80)

# Find videos marked as completed but with NULL target_video_id
cursor.execute("""
    SELECT source_video_id, source_title, status
    FROM videos
    WHERE status = 'completed'
    AND target_video_id IS NULL
""")

corrupted = cursor.fetchall()

if corrupted:
    print(f"\n🔍 Found {len(corrupted)} corrupted entries:")
    for video in corrupted:
        source_id, title, status = video
        print(f"   - {title[:60]}")
        print(f"     Source ID: {source_id}")
    
    # Update status to 'failed'
    cursor.execute("""
        UPDATE videos
        SET status = 'failed',
            error_message = 'Upload failed: No video ID returned from YouTube API (status was incorrectly marked as completed)'
        WHERE status = 'completed'
        AND target_video_id IS NULL
    """)
    
    conn.commit()
    print(f"\n✅ Updated {cursor.rowcount} videos to 'failed' status")
else:
    print("\n✅ No corrupted entries found")

# Check current video status
print("\n2️⃣ Current video status summary:")
print("-"*80)

cursor.execute("""
    SELECT status, COUNT(*) as count
    FROM videos
    GROUP BY status
""")

for status, count in cursor.fetchall():
    print(f"   {status}: {count}")

conn.close()

# Check upload configuration
print("\n3️⃣ Checking upload configuration:")
print("-"*80)

# Check if OAuth token exists
token_file = Path('token.json')
if token_file.exists():
    print(f"   ✅ OAuth token file exists: {token_file}")
    print(f"      Size: {token_file.stat().st_size} bytes")
    print(f"      Modified: {token_file.stat().st_mtime}")
else:
    print(f"   ❌ OAuth token file NOT found: {token_file}")
    print(f"      This is likely why uploads are failing!")

# Check client secrets
client_secrets = Path('client_secrets.json')
if client_secrets.exists():
    print(f"   ✅ Client secrets file exists: {client_secrets}")
else:
    print(f"   ❌ Client secrets file NOT found: {client_secrets}")

# Check config
config_file = Path('config.json')
if config_file.exists():
    print(f"   ✅ Config file exists: {config_file}")
    
    import json
    try:
        with open(config_file) as f:
            config = json.load(f)
        
        # Check upload settings
        upload_settings = config.get('upload', {})
        print(f"\n   Upload settings:")
        print(f"      Privacy: {upload_settings.get('privacy_status', 'NOT SET')}")
        print(f"      Category: {upload_settings.get('category_id', 'NOT SET')}")
        
    except Exception as e:
        print(f"   ⚠️ Error reading config: {e}")
else:
    print(f"   ❌ Config file NOT found: {config_file}")

print("\n4️⃣ Recommendations:")
print("-"*80)

print("""
To fix the upload issue:

1. Verify YouTube API credentials:
   - Check that client_secrets.json has valid credentials
   - Run: python refresh_oauth.py to re-authenticate

2. Check API quota:
   - Go to: https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas
   - Ensure you have not exceeded daily quota (10,000 units)

3. Test upload manually:
   - Run the application and monitor logs
   - Check src/youtube/uploader.py for any error handling issues

4. Re-upload failed videos:
   - The 2 failed videos are now marked as 'failed'
   - The application should detect and retry them automatically
   - Or you can manually reset their status to 'pending'
""")

print("\n" + "="*80)
print("✅ DATABASE FIX COMPLETE")
print("="*80 + "\n")
