import sqlite3

conn = sqlite3.connect('data/videos.db')
cursor = conn.cursor()

cursor.execute('SELECT source_video_id, source_title, status, target_video_id, error_message FROM videos ORDER BY created_at DESC')
rows = cursor.fetchall()

print('\n' + '='*80)
print('📹 VIDEOS IN DATABASE')
print('='*80)

for i, row in enumerate(rows, 1):
    video_id, title, status, uploaded_id, error = row
    print(f'\n{i}. Video ID: {video_id}')
    print(f'   Title: {title[:70] if title else "N/A"}')
    print(f'   Status: {status}')
    print(f'   Uploaded ID: {uploaded_id if uploaded_id else "Not uploaded yet"}')
    if error:
        print(f'   Error: {error[:100]}...')

print('\n' + '='*80)
conn.close()
