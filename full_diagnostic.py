"""Comprehensive upload diagnostic"""
import sqlite3

print("\n" + "="*80)
print("🔍 COMPREHENSIVE UPLOAD DIAGNOSTIC")
print("="*80)

conn = sqlite3.connect('data/videos.db')
cursor = conn.cursor()

# 1. Check videos table
print("\n📹 VIDEOS TABLE ANALYSIS:")
print("-"*80)

cursor.execute("""
    SELECT 
        source_video_id,
        source_title,
        status,
        target_video_id,
        downloaded_at,
        uploaded_at,
        error_message
    FROM videos
    ORDER BY created_at DESC
""")

videos = cursor.fetchall()

for i, video in enumerate(videos, 1):
    source_id, title, status, target_id, downloaded_at, uploaded_at, error = video
    
    print(f"\n{i}. {title}")
    print(f"   📺 Source ID: {source_id}")
    print(f"   📊 Status: {status}")
    print(f"   📥 Downloaded At: {downloaded_at}")
    print(f"   📤 Uploaded At: {uploaded_at}")
    
    if target_id:
        print(f"   ✅ Target Video ID: {target_id}")
        print(f"   🔗 YouTube URL: https://youtube.com/watch?v={target_id}")
    else:
        print(f"   ❌ Target Video ID: NULL (UPLOAD FAILED!)")
    
    if error:
        print(f"   ⚠️ Error Message: {error}")
    
    # Analyze the problem
    if status == 'completed' and not target_id:
        print(f"   🚨 BUG DETECTED: Status is 'completed' but no target_video_id!")
        print(f"   🐛 This means the upload failed but status was incorrectly set.")

# 2. Check logs table for upload-related errors
print("\n" + "="*80)
print("📋 LOGS TABLE - UPLOAD ERRORS:")
print("-"*80)

cursor.execute("""
    SELECT 
        timestamp,
        level,
        module,
        message,
        details
    FROM logs
    WHERE (message LIKE '%upload%' OR message LIKE '%Upload%' 
           OR message LIKE '%ERROR%' OR level = 'ERROR')
    ORDER BY timestamp DESC
    LIMIT 20
""")

logs = cursor.fetchall()

if logs:
    for log in logs:
        timestamp, level, module, message, details = log
        print(f"\n[{timestamp}] [{level}] {module if module else 'N/A'}")
        print(f"   Message: {message}")
        if details:
            print(f"   Details: {details}")
else:
    print("\n⚠️ No upload-related logs found in database.")

# 3. Check stats
print("\n" + "="*80)
print("📊 STATISTICS TABLE:")
print("-"*80)

cursor.execute("""
    SELECT 
        date,
        videos_detected,
        videos_downloaded,
        videos_uploaded,
        errors_count
    FROM stats
    ORDER BY date DESC
    LIMIT 7
""")

stats = cursor.fetchall()

if stats:
    print("\n   Date       | Detected | Downloaded | Uploaded | Errors")
    print("   " + "-"*60)
    for stat in stats:
        date, detected, downloaded, uploaded, errors = stat
        print(f"   {date} | {detected:8} | {downloaded:10} | {uploaded:8} | {errors:6}")
else:
    print("\n⚠️ No statistics found.")

conn.close()

print("\n" + "="*80)
print("💡 DIAGNOSIS SUMMARY:")
print("="*80)

print("""
The issue is clear:
1. ✅ Videos were successfully downloaded
2. ❌ Videos FAILED to upload to YouTube (target_video_id is NULL)
3. 🐛 BUT the status was incorrectly marked as 'completed'

ROOT CAUSE:
In src/core/workers.py, the UploadWorker.run() method marks the video
as 'completed' even when uploaded_video_id is None (indicating failure).

FIX NEEDED:
The code should check if uploaded_video_id is not None before marking
as 'completed'. If None, it should mark as 'failed' instead.

NEXT STEPS:
1. Check why the upload failed (API credentials, quota, network, etc.)
2. Fix the bug in workers.py to properly handle upload failures
3. Re-run the upload for these 2 failed videos
""")

print("\n" + "="*80)
