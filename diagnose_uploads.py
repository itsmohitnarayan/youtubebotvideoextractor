"""Diagnostic script to check upload status"""
import sqlite3
from datetime import datetime

conn = sqlite3.connect('data/app.db')
cursor = conn.cursor()

print("\n" + "="*80)
print("🔍 UPLOAD DIAGNOSTIC REPORT")
print("="*80)

# Get video statistics
cursor.execute("""
    SELECT 
        status,
        COUNT(*) as count
    FROM videos
    GROUP BY status
""")
status_counts = cursor.fetchall()

print("\n📊 VIDEO STATUS SUMMARY:")
for status, count in status_counts:
    print(f"   {status}: {count}")

# Get detailed info on uploaded videos
print("\n" + "="*80)
print("📹 DETAILED UPLOAD STATUS:")
print("="*80)

cursor.execute("""
    SELECT 
        source_video_id,
        source_title,
        status,
        target_video_id,
        uploaded_at,
        error_message,
        created_at
    FROM videos
    ORDER BY created_at DESC
    LIMIT 10
""")

videos = cursor.fetchall()

for i, video in enumerate(videos, 1):
    source_id, title, status, target_id, uploaded_at, error, created_at = video
    
    print(f"\n{i}. {title[:60] if title else 'N/A'}")
    print(f"   Source ID: {source_id}")
    print(f"   Status: {status}")
    print(f"   Created: {created_at}")
    
    if target_id:
        print(f"   ✅ Uploaded Video ID: {target_id}")
        print(f"   🔗 YouTube URL: https://youtube.com/watch?v={target_id}")
        print(f"   ⏰ Uploaded At: {uploaded_at}")
    else:
        print(f"   ❌ Target Video ID: NULL (Upload failed or incomplete!)")
        print(f"   ⏰ Upload Attempted: {uploaded_at if uploaded_at else 'Never'}")
    
    if error:
        print(f"   ⚠️ Error: {error}")

# Check for videos marked as uploaded but no target_video_id
print("\n" + "="*80)
print("⚠️ SUSPICIOUS ENTRIES (Status='uploaded' but no target_video_id):")
print("="*80)

cursor.execute("""
    SELECT 
        source_video_id,
        source_title,
        status,
        uploaded_at
    FROM videos
    WHERE status IN ('uploaded', 'completed')
    AND target_video_id IS NULL
""")

suspicious = cursor.fetchall()

if suspicious:
    print(f"\n🚨 Found {len(suspicious)} suspicious entries:")
    for video in suspicious:
        print(f"\n   Video: {video[1][:60] if video[1] else 'N/A'}")
        print(f"   Source ID: {video[0]}")
        print(f"   Status: {video[2]}")
        print(f"   Uploaded At: {video[3]}")
else:
    print("\n✅ No suspicious entries found.")

# Check logs for upload errors
print("\n" + "="*80)
print("📋 RECENT UPLOAD-RELATED LOGS:")
print("="*80)

cursor.execute("""
    SELECT 
        timestamp,
        level,
        message,
        details
    FROM logs
    WHERE message LIKE '%upload%'
    OR message LIKE '%Upload%'
    ORDER BY timestamp DESC
    LIMIT 15
""")

logs = cursor.fetchall()

if logs:
    for log in logs:
        timestamp, level, message, details = log
        print(f"\n[{timestamp}] [{level}] {message}")
        if details:
            print(f"   Details: {details[:200]}")
else:
    print("\n⚠️ No upload-related logs found.")

conn.close()

print("\n" + "="*80)
print("✅ DIAGNOSTIC COMPLETE")
print("="*80 + "\n")
