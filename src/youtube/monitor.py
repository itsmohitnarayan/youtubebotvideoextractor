"""
Channel Monitor
Monitors YouTube channel for new video uploads.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Callable, List, Dict, Any
import logging
import time


class ChannelMonitor:
    """Monitors a YouTube channel for new videos."""
    
    def __init__(
        self,
        api_client,
        database,
        source_channel_id: str,
        check_interval_minutes: int = 5,
        lookback_hours: int = 24
    ):
        """
        Initialize channel monitor.
        
        Args:
            api_client: YouTubeAPIClient instance
            database: DatabaseManager instance
            source_channel_id: YouTube channel ID to monitor
            check_interval_minutes: Minutes between checks (default: 5)
            lookback_hours: Hours to look back on first check (default: 24)
        """
        self.api_client = api_client
        self.database = database
        self.source_channel_id = source_channel_id
        self.check_interval_minutes = check_interval_minutes
        self.lookback_hours = lookback_hours
        
        self.logger = logging.getLogger(__name__)
        self.is_monitoring = False
        self.last_check_time = None
        self.new_video_callback = None
        
        # Cache of processed video IDs (to avoid duplicates)
        self.processed_video_ids = set()
        self._load_processed_videos()
    
    def _load_processed_videos(self) -> None:
        """Load already processed video IDs from database."""
        try:
            videos = self.database.get_all_videos()
            self.processed_video_ids = {v['source_video_id'] for v in videos}
            self.logger.info(
                f"Loaded {len(self.processed_video_ids)} processed video IDs"
            )
        except Exception as e:
            self.logger.error(f"Error loading processed videos: {e}")
            self.processed_video_ids = set()
    
    def set_new_video_callback(self, callback: Callable) -> None:
        """
        Set callback function for new video detection.
        
        Args:
            callback: Function to call when new video is found
                     Signature: callback(video_info: Dict) -> None
        """
        self.new_video_callback = callback
        self.logger.info("New video callback registered")
    
    def check_for_new_videos(self) -> List[Dict[str, Any]]:
        """
        Check for new videos since last check.
        
        Returns:
            List of new video information dictionaries
        """
        try:
            # Calculate time window (use timezone-aware datetime)
            if self.last_check_time:
                since_datetime = self.last_check_time
            else:
                # First check: look back configured hours (timezone-aware)
                since_datetime = datetime.now(timezone.utc) - timedelta(hours=self.lookback_hours)
            
            # Get recent uploads from channel
            recent_videos = self.api_client.get_recent_uploads(
                channel_id=self.source_channel_id,
                max_results=50,
                since=since_datetime
            )
            
            # Filter out already processed videos
            new_videos = []
            for video in recent_videos:
                try:
                    video_id = video['id']['videoId'] if 'id' in video else video.get('video_id')
                    
                    if video_id and video_id not in self.processed_video_ids:
                        # Get full video details
                        video_details = self.api_client.get_video_details(video_id)
                        
                        if video_details:
                            # Video details are returned at root level, not under 'snippet'
                            new_videos.append(video_details)
                            self.processed_video_ids.add(video_id)
                            
                            # Add to database
                            self.database.add_video({
                                'video_id': video_id,
                                'title': video_details.get('title', 'Unknown Title'),
                                'description': video_details.get('description', ''),  # Keep original description
                                'published_at': str(video_details.get('published_at', '')),
                                'thumbnail_url': video_details.get('thumbnail_url', ''),
                                'status': 'queued'
                            })
                            
                            self.logger.info(f"New video detected: {video_details.get('title', video_id)}")
                except KeyError as e:
                    self.logger.error(f"Missing key in video data: {e}. Video: {video}")
                except Exception as e:
                    self.logger.error(f"Error processing video: {e}", exc_info=True)
            
            # Update last check time (timezone-aware)
            self.last_check_time = datetime.now(timezone.utc)
            
            # Trigger callbacks for each new video
            if new_videos and self.new_video_callback:
                for video in new_videos:
                    try:
                        self.new_video_callback(video)
                    except Exception as e:
                        self.logger.error(f"Error in new video callback: {e}")
            
            return new_videos
            
        except Exception as e:
            self.logger.error(f"Error checking for new videos: {e}")
            return []
    
    def start_monitoring(self) -> None:
        """Start monitoring channel (blocking call)."""
        self.is_monitoring = True
        self.logger.info(
            f"Started monitoring channel {self.source_channel_id} "
            f"(check interval: {self.check_interval_minutes} minutes)"
        )
        
        while self.is_monitoring:
            try:
                # Check for new videos
                new_videos = self.check_for_new_videos()
                
                if new_videos:
                    self.logger.info(f"Found {len(new_videos)} new video(s)")
                else:
                    self.logger.debug("No new videos found")
                
                # Wait for next check
                time.sleep(self.check_interval_minutes * 60)
                
            except KeyboardInterrupt:
                self.logger.info("Monitoring stopped by user")
                self.stop_monitoring()
                break
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                # Continue monitoring despite errors
                time.sleep(60)  # Wait 1 minute before retrying
    
    def stop_monitoring(self) -> None:
        """Stop monitoring channel."""
        self.is_monitoring = False
        self.logger.info("Monitoring stopped")
    
    def get_channel_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the monitored channel.
        
        Returns:
            Channel information dictionary or None
        """
        try:
            return self.api_client.get_channel_info(self.source_channel_id)
        except Exception as e:
            self.logger.error(f"Error getting channel info: {e}")
            return None
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """
        Get monitoring statistics.
        
        Returns:
            Dictionary with monitoring stats
        """
        return {
            'is_monitoring': self.is_monitoring,
            'source_channel_id': self.source_channel_id,
            'check_interval_minutes': self.check_interval_minutes,
            'last_check_time': self.last_check_time.isoformat() if self.last_check_time else None,
            'processed_videos_count': len(self.processed_video_ids),
            'has_callback': self.new_video_callback is not None
        }
    
    def clear_processed_videos_cache(self) -> None:
        """Clear the cache of processed video IDs."""
        self.processed_video_ids.clear()
        self._load_processed_videos()
        self.logger.info("Cleared processed videos cache")
    
    def is_video_processed(self, video_id: str) -> bool:
        """
        Check if a video has already been processed.
        
        Args:
            video_id: YouTube video ID
        
        Returns:
            True if video was processed, False otherwise
        """
        return video_id in self.processed_video_ids
    
    def mark_video_as_processed(self, video_id: str) -> None:
        """
        Manually mark a video as processed.
        
        Args:
            video_id: YouTube video ID
        """
        self.processed_video_ids.add(video_id)
        self.logger.info(f"Marked video {video_id} as processed")
