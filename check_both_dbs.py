"""Check both database files"""
import sqlite3
from pathlib import Path

databases = [
    'data/app.db',
    'data/videos.db'
]

for db_path in databases:
    if not Path(db_path).exists():
        print(f"\n❌ {db_path} does not exist")
        continue
        
    print("\n" + "="*80)
    print(f"📂 DATABASE: {db_path}")
    print("="*80)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]
    print(f"\n📊 Tables: {', '.join(tables)}")
    
    # Check videos table
    if 'videos' in tables:
        cursor.execute("SELECT COUNT(*) FROM videos")
        count = cursor.fetchone()[0]
        print(f"\n📹 Total videos in database: {count}")
        
        if count > 0:
            # Get status summary
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM videos
                GROUP BY status
            """)
            print("\n📊 Status breakdown:")
            for status, cnt in cursor.fetchall():
                print(f"   {status}: {cnt}")
            
            # Get recent videos
            print("\n📋 Recent videos:")
            cursor.execute("""
                SELECT 
                    source_video_id,
                    source_title,
                    status,
                    target_video_id,
                    uploaded_at,
                    error_message
                FROM videos
                ORDER BY created_at DESC
                LIMIT 5
            """)
            
            for i, row in enumerate(cursor.fetchall(), 1):
                source_id, title, status, target_id, uploaded_at, error = row
                print(f"\n   {i}. {title[:50] if title else 'N/A'}")
                print(f"      Source ID: {source_id}")
                print(f"      Status: {status}")
                if target_id:
                    print(f"      ✅ Target ID: {target_id}")
                    print(f"      🔗 URL: https://youtube.com/watch?v={target_id}")
                else:
                    print(f"      ❌ Target ID: NULL")
                if uploaded_at:
                    print(f"      ⏰ Uploaded: {uploaded_at}")
                if error:
                    print(f"      ⚠️ Error: {error[:100]}")
    
    conn.close()

print("\n" + "="*80)
