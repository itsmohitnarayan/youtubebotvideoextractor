"""Quick database viewer"""
import sqlite3

conn = sqlite3.connect('data/videos.db')
cursor = conn.cursor()

print("=" * 60)
print("DATABASE: videos.db")
print("=" * 60)

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print(f"\nTables ({len(tables)}):")
for table in tables:
    table_name = table[0]
    print(f"\n📊 {table_name}")
    
    # Get table structure
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    print("   Columns:")
    for col in columns:
        col_id, col_name, col_type, not_null, default, pk = col
        pk_mark = " [PRIMARY KEY]" if pk else ""
        print(f"     - {col_name}: {col_type}{pk_mark}")
    
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"   Rows: {count}")

print("\n" + "=" * 60)
conn.close()
