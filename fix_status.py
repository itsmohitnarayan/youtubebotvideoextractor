"""Fix the status of successfully uploaded video"""
import sqlite3

conn = sqlite3.connect('data/videos.db')
cursor = conn.cursor()

# Update the successfully uploaded video status
cursor.execute("""
    UPDATE videos 
    SET status = 'completed', 
        uploaded_at = datetime('now'),
        error_message = NULL
    WHERE source_video_id = 'jKZQyAAA6V0'
""")

conn.commit()

print("\n✅ Fixed video status!")
print(f"   Updated: jKZQyAAA6V0 -> Status: completed")

# Verify
cursor.execute("SELECT source_video_id, status, target_video_id FROM videos WHERE source_video_id = 'jKZQyAAA6V0'")
row = cursor.fetchone()
print(f"   Verified: {row[0]} - Status: {row[1]} - Uploaded: {row[2]}")

conn.close()
