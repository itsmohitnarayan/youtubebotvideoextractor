"""
Database Manager
Handles SQLite database operations for video tracking and logging.
"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import json


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
        self._connect()
        self._init_database()
    
    def _connect(self) -> None:
        """Establish database connection."""
        try:
            self.connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False
            )
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
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
            "SELECT * FROM videos ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_stats_today(self) -> Dict[str, int]:
        """
        Get today's statistics.
        
        Returns:
            Dictionary with today's stats
        """
        if not self.connection:
            return {}
        
        today = datetime.now().date()
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
        
        today = datetime.now().date()
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
    
    def add_log(
        self,
        level: str,
        message: str,
        module: str = None,
        details: str = None,
        video_id: str = None
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
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO logs (level, module, message, details, video_id)
                VALUES (?, ?, ?, ?, ?)
            """, (level, module, message, details, video_id))
            
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Error adding log: {e}")
    
    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed")
