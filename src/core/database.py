"""
Database Manager
Handles SQLite database operations for video tracking and logging.
"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json
import threading


class DatabaseManager:
    """Manages SQLite database for application state and history."""
    
    DATABASE_VERSION = 1
    
    def __init__(self, db_path: str = "data/app.db"):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.connection: Optional[sqlite3.Connection] = None
        self._lock = threading.Lock()  # Thread-safe database operations
        self._connect()
        self._init_database()
    
    def _connect(self) -> None:
        """Establish database connection."""
        try:
            self.connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,
                timeout=30.0,  # Wait up to 30 seconds for locks
                isolation_level='DEFERRED'  # Better concurrency
            )
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            # Enable WAL mode for better concurrent access
            self.connection.execute("PRAGMA journal_mode=WAL")
            self.connection.execute("PRAGMA synchronous=NORMAL")
            print(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            raise
    
    def _init_database(self) -> None:
        """Initialize database schema."""
        if not self.connection:
            return
        
        cursor = self.connection.cursor()
        
        # Videos table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_video_id TEXT UNIQUE NOT NULL,
                source_title TEXT,
                source_description TEXT,
                source_published_at DATETIME,
                source_thumbnail_url TEXT,
                downloaded_at DATETIME,
                uploaded_at DATETIME,
                target_video_id TEXT,
                target_url TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                error_message TEXT,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index on source_video_id for fast lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_source_video_id 
            ON videos(source_video_id)
        """)
        
        # Create index on status for filtering
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status 
            ON videos(status)
        """)
        
        # Logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                level TEXT NOT NULL,
                module TEXT,
                message TEXT NOT NULL,
                details TEXT,
                video_id TEXT,
                FOREIGN KEY (video_id) REFERENCES videos(source_video_id)
            )
        """)
        
        # Statistics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE NOT NULL,
                videos_detected INTEGER DEFAULT 0,
                videos_downloaded INTEGER DEFAULT 0,
                videos_uploaded INTEGER DEFAULT 0,
                errors_count INTEGER DEFAULT 0,
                total_size_mb REAL DEFAULT 0.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Settings table for runtime configuration
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.connection.commit()
        print("Database schema initialized")
    
    def add_video(self, video_data: Dict[str, Any]) -> Optional[int]:
        """
        Add a new video record.
        
        Args:
            video_data: Dictionary containing video information
        
        Returns:
            Video ID if successful, None otherwise
        """
        if not self.connection:
            return None
        
        try:
            with self._lock:  # Thread-safe database access
                cursor = self.connection.cursor()
                cursor.execute("""
                    INSERT INTO videos (
                        source_video_id, source_title, source_description,
                        source_published_at, source_thumbnail_url, status, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    video_data.get('video_id'),
                    video_data.get('title'),
                    video_data.get('description'),
                    video_data.get('published_at'),
                    video_data.get('thumbnail_url'),
                    video_data.get('status', 'pending'),
                    json.dumps(video_data.get('metadata', {}))
                ))
                
                self.connection.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            print(f"Video already exists: {video_data.get('video_id')}")
            return None
        except sqlite3.Error as e:
            print(f"Error adding video: {e}")
            return None
    
    def update_video_status(
        self,
        video_id: str,
        status: str,
        **kwargs
    ) -> bool:
        """
        Update video status and additional fields.
        
        Args:
            video_id: Source video ID
            status: New status (pending, downloading, uploading, completed, failed)
            **kwargs: Additional fields to update
        
        Returns:
            True if successful, False otherwise
        """
        if not self.connection:
            return False
        
        try:
            with self._lock:  # Thread-safe database access
                # Build dynamic UPDATE query
                fields = ['status = ?', 'updated_at = CURRENT_TIMESTAMP']
                values = [status]
                
                for key, value in kwargs.items():
                    fields.append(f"{key} = ?")
                    values.append(value)
                
                values.append(video_id)
                
                query = f"""
                    UPDATE videos 
                    SET {', '.join(fields)}
                    WHERE source_video_id = ?
                """
                
                cursor = self.connection.cursor()
                cursor.execute(query, values)
                self.connection.commit()
                
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating video status: {e}")
            try:
                self.connection.rollback()
            except:
                pass
            return False
        except Exception as e:
            print(f"Unexpected error updating video status: {type(e).__name__}: {e}")
            try:
                self.connection.rollback()
            except:
                pass
            return False
            return False
    
    def is_video_processed(self, video_id: str) -> bool:
        """
        Check if video has been processed (O(1) with index).
        
        Args:
            video_id: Source video ID
        
        Returns:
            True if video exists in database, False otherwise
        """
        if not self.connection:
            return False
        
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT 1 FROM videos WHERE source_video_id = ? LIMIT 1",
            (video_id,)
        )
        
        return cursor.fetchone() is not None
    
    def get_video(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Get video record by source video ID.
        
        Args:
            video_id: Source video ID
        
        Returns:
            Video data as dictionary or None
        """
        if not self.connection:
            return None
        
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT * FROM videos WHERE source_video_id = ?",
            (video_id,)
        )
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_recent_videos(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent videos ordered by creation date.
        
        Args:
            limit: Maximum number of videos to return
        
        Returns:
            List of video dictionaries
        """
        if not self.connection:
            return []
        
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT * FROM videos ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_all_videos(self) -> List[Dict[str, Any]]:
        """
        Get all videos from database.
        
        Returns:
            List of all video dictionaries
        """
        if not self.connection:
            return []
        
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM videos ORDER BY id DESC")
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_queued_videos(self) -> List[Dict[str, Any]]:
        """
        Get all videos with 'queued' status from database.
        
        Returns:
            List of queued video dictionaries
        """
        if not self.connection:
            return []
        
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM videos 
            WHERE status = 'queued' 
            ORDER BY created_at ASC
        """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_stats_today(self) -> Dict[str, int | float]:
        """
        Get today's statistics.
        
        Returns:
            Dictionary with today's stats
        """
        if not self.connection:
            return {}
        
        today = datetime.now().date().isoformat()
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT * FROM stats WHERE date = ?",
            (today,)
        )
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        
        # Return default stats if no record exists
        return {
            'videos_detected': 0,
            'videos_downloaded': 0,
            'videos_uploaded': 0,
            'errors_count': 0,
            'total_size_mb': 0.0
        }
    
    def increment_stat(self, stat_name: str, amount: int = 1) -> None:
        """
        Increment a statistic for today.
        
        Args:
            stat_name: Name of the statistic field
            amount: Amount to increment by
        """
        if not self.connection:
            return
        
        with self._lock:
            today = datetime.now().date().isoformat()
            cursor = self.connection.cursor()
            
            # Insert or update
            cursor.execute(f"""
                INSERT INTO stats (date, {stat_name})
                VALUES (?, ?)
                ON CONFLICT(date) DO UPDATE SET
                    {stat_name} = {stat_name} + ?,
                    updated_at = CURRENT_TIMESTAMP
        """, (today, amount, amount))
        
        self.connection.commit()
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get statistics for the GUI dashboard.
        Counts videos by status from the database.
        
        Returns:
            Dictionary with 'detected', 'downloaded', 'uploaded', 'errors' counts
        """
        if not self.connection:
            return {'detected': 0, 'downloaded': 0, 'uploaded': 0, 'errors': 0}
        
        cursor = self.connection.cursor()
        
        # Count total videos (detected)
        cursor.execute("SELECT COUNT(*) FROM videos")
        detected = cursor.fetchone()[0]
        
        # Count downloaded videos
        cursor.execute("SELECT COUNT(*) FROM videos WHERE downloaded_at IS NOT NULL")
        downloaded = cursor.fetchone()[0]
        
        # Count uploaded videos
        cursor.execute("SELECT COUNT(*) FROM videos WHERE uploaded_at IS NOT NULL")
        uploaded = cursor.fetchone()[0]
        
        # Count errors (videos with error_message)
        cursor.execute("SELECT COUNT(*) FROM videos WHERE error_message IS NOT NULL")
        errors = cursor.fetchone()[0]
        
        return {
            'detected': detected,
            'downloaded': downloaded,
            'uploaded': uploaded,
            'errors': errors
        }
    
    def update_video_files(
        self,
        video_id: str,
        video_path: str,
        thumbnail_path: Optional[str] = None
    ) -> bool:
        """
        Update video file paths after download.
        
        Args:
            video_id: Source video ID
            video_path: Path to downloaded video file
            thumbnail_path: Path to downloaded thumbnail file (optional)
        
        Returns:
            True if successful, False otherwise
        """
        if not self.connection:
            return False
        
        try:
            with self._lock:  # Thread-safe database access
                cursor = self.connection.cursor()
                
                # Store paths in metadata JSON
                cursor.execute(
                    "SELECT metadata FROM videos WHERE source_video_id = ?",
                    (video_id,)
                )
                row = cursor.fetchone()
                
                metadata = {}
                if row and row[0]:
                    try:
                        metadata = json.loads(row[0])
                    except json.JSONDecodeError:
                        pass
                
                metadata['video_path'] = video_path
                if thumbnail_path:
                    metadata['thumbnail_path'] = thumbnail_path
                
                cursor.execute("""
                    UPDATE videos 
                    SET metadata = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE source_video_id = ?
                """, (json.dumps(metadata), video_id))
                
                self.connection.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating video files: {e}")
            return False
    
    def update_video_error(self, video_id: str, error_message: str) -> bool:
        """
        Update video error message.
        
        Args:
            video_id: Source video ID
            error_message: Error message to store
        
        Returns:
            True if successful, False otherwise
        """
        if not self.connection:
            return False
        
        try:
            with self._lock:
                cursor = self.connection.cursor()
                cursor.execute("""
                    UPDATE videos 
                    SET error_message = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE source_video_id = ?
                """, (error_message, video_id))
                self.connection.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating video error: {e}")
            return False
    
    def update_video_metadata(self, video_id: str, metadata_json: str) -> bool:
        """
        Update or merge video metadata.
        
        Args:
            video_id: Source video ID
            metadata_json: JSON string with metadata to merge
        
        Returns:
            True if successful, False otherwise
        """
        if not self.connection:
            return False
        
        try:
            with self._lock:
                cursor = self.connection.cursor()
                
                # Get existing metadata
                cursor.execute(
                    "SELECT metadata FROM videos WHERE source_video_id = ?",
                    (video_id,)
                )
                row = cursor.fetchone()
                
                existing_metadata = {}
                if row and row[0]:
                    try:
                        existing_metadata = json.loads(row[0])
                    except json.JSONDecodeError:
                        pass
                
                # Merge new metadata
                new_metadata = json.loads(metadata_json)
                existing_metadata.update(new_metadata)
                
                # Update database
                cursor.execute("""
                    UPDATE videos 
                    SET metadata = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE source_video_id = ?
                """, (json.dumps(existing_metadata), video_id))
                
                self.connection.commit()
                return cursor.rowcount > 0
        except (sqlite3.Error, json.JSONDecodeError) as e:
            print(f"Error updating video metadata: {e}")
            return False
    
    def update_video_uploaded_id(self, video_id: str, uploaded_video_id: str) -> bool:
        """
        Update uploaded video ID after successful upload.
        
        Args:
            video_id: Source video ID
            uploaded_video_id: YouTube video ID of uploaded video
        
        Returns:
            True if successful, False otherwise
        """
        if not self.connection:
            return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE videos 
                SET target_video_id = ?, 
                    target_url = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE source_video_id = ?
            """, (
                uploaded_video_id,
                f"https://youtube.com/watch?v={uploaded_video_id}",
                video_id
            ))
            
            self.connection.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating uploaded video ID: {e}")
            return False
    
    def update_video_timestamp(
        self,
        video_id: str,
        timestamp_field: str,
        timestamp: datetime
    ) -> bool:
        """
        Update a timestamp field for a video.
        
        Args:
            video_id: Source video ID
            timestamp_field: Name of timestamp field (e.g., 'downloaded_at', 'uploaded_at')
            timestamp: Timestamp value
        
        Returns:
            True if successful, False otherwise
        """
        if not self.connection:
            return False
        
        # Validate field name to prevent SQL injection
        allowed_fields = ['downloaded_at', 'uploaded_at', 'created_at', 'updated_at']
        if timestamp_field not in allowed_fields:
            print(f"Invalid timestamp field: {timestamp_field}")
            return False
        
        try:
            cursor = self.connection.cursor()
            query = f"""
                UPDATE videos 
                SET {timestamp_field} = ?, updated_at = CURRENT_TIMESTAMP
                WHERE source_video_id = ?
            """
            cursor.execute(query, (timestamp.isoformat(), video_id))
            
            self.connection.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating video timestamp: {e}")
            return False
    
    def add_log(
        self,
        level: str,
        message: str,
        module: Optional[str] = None,
        details: Optional[str] = None,
        video_id: Optional[str] = None
    ) -> None:
        """
        Add log entry to database.
        
        Args:
            level: Log level (INFO, WARNING, ERROR, etc.)
            message: Log message
            module: Module name
            details: Additional details
            video_id: Related video ID
        """
        if not self.connection:
            return
        
        with self._lock:
            try:
                cursor = self.connection.cursor()
                cursor.execute("""
                    INSERT INTO logs (level, module, message, details, video_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (level, module, message, details, video_id))
                
                self.connection.commit()
            except sqlite3.Error as e:
                print(f"Error adding log: {e}")
    
    def save_quota_usage(self, quota_used: int, date: Optional[str] = None) -> None:
        """
        Save API quota usage to database.
        
        Args:
            quota_used: Amount of quota used
            date: Date string (YYYY-MM-DD), defaults to today
        """
        if not self.connection:
            return
        
        if date is None:
            date = datetime.now().date().isoformat()
        
        with self._lock:
            try:
                cursor = self.connection.cursor()
                cursor.execute("""
                    INSERT INTO settings (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(key) DO UPDATE SET
                        value = ?,
                        updated_at = CURRENT_TIMESTAMP
                """, (f"quota_used_{date}", str(quota_used), str(quota_used)))
                
                self.connection.commit()
            except sqlite3.Error as e:
                print(f"Error saving quota usage: {e}")
    
    def get_quota_usage(self, date: Optional[str] = None) -> int:
        """
        Get API quota usage from database.
        
        Args:
            date: Date string (YYYY-MM-DD), defaults to today
        
        Returns:
            Quota used for the specified date
        """
        if not self.connection:
            return 0
        
        if date is None:
            date = datetime.now().date().isoformat()
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT value FROM settings WHERE key = ?
            """, (f"quota_used_{date}",))
            
            row = cursor.fetchone()
            if row:
                return int(row['value'])
            
            return 0
        except (sqlite3.Error, ValueError) as e:
            print(f"Error getting quota usage: {e}")
            return 0
    
    def clear_old_quota_usage(self, days_to_keep: int = 7) -> None:
        """
        Clear old quota usage records.
        
        Args:
            days_to_keep: Number of days of quota data to keep
        """
        if not self.connection:
            return
        
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).date().isoformat()
        
        with self._lock:
            try:
                cursor = self.connection.cursor()
                cursor.execute("""
                    DELETE FROM settings
                    WHERE key LIKE 'quota_used_%'
                    AND key < ?
                """, (f"quota_used_{cutoff_date}",))
                
                self.connection.commit()
            except sqlite3.Error as e:
                print(f"Error clearing old quota usage: {e}")
    
    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed")
