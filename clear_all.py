"""Clear database and downloads for fresh testing"""
import sqlite3
import shutil
from pathlib import Path

print("\n" + "="*80)
print("🧹 CLEARING DATABASE AND DOWNLOADS")
print("="*80)

# Clear database
print("\n📊 Clearing database...")
conn = sqlite3.connect('data/videos.db')
cursor = conn.cursor()

# Delete all videos
cursor.execute("DELETE FROM videos")
cursor.execute("DELETE FROM logs")
cursor.execute("DELETE FROM stats")

# Reset sequences
cursor.execute("DELETE FROM sqlite_sequence")

conn.commit()
print("✅ Database cleared!")

# Show counts
cursor.execute("SELECT COUNT(*) FROM videos")
video_count = cursor.fetchone()[0]
print(f"   Videos in database: {video_count}")

conn.close()

# Clear downloads folder
print("\n📁 Clearing downloads folder...")
downloads_dir = Path('downloads')

if downloads_dir.exists():
    deleted_count = 0
    for session_dir in downloads_dir.glob('session_*'):
        if session_dir.is_dir():
            shutil.rmtree(session_dir)
            deleted_count += 1
            print(f"   Deleted: {session_dir.name}")
    
    print(f"✅ Cleared {deleted_count} session(s)")
else:
    print("   Downloads folder doesn't exist")

# Clear logs
print("\n📝 Clearing logs...")
logs_dir = Path('logs')
if logs_dir.exists():
    for log_file in logs_dir.glob('*.log'):
        log_file.unlink()
        print(f"   Deleted: {log_file.name}")
    print("✅ Logs cleared!")

print("\n" + "="*80)
print("✨ FRESH START READY!")
print("="*80)
print("\nEverything is clean. You can now:")
print("  1. Start the application: .\\venv\\Scripts\\python.exe run.py")
print("  2. It will automatically detect and process new videos")
print("  3. All metadata, tags, and thumbnails will be preserved")
print("  4. Description will be: 'Re-uploaded from MuFiJuL GaminG' + original")
print("\n" + "="*80 + "\n")
