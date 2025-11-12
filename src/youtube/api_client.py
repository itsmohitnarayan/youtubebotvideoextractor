"""
YouTube API Client
Handles all YouTube Data API v3 interactions.
"""

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from typing import Optional, List, Dict, Any
from pathlib import Path
import json
import logging
from datetime import datetime, timedelta


# YouTube API scopes
SCOPES = [
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube.force-ssl'
]


class YouTubeAPIClient:
    """Manages YouTube API authentication and requests."""
    
    # API quota costs (units per operation)
    QUOTA_COSTS = {
        'channels.list': 1,
        'search.list': 100,
        'videos.list': 1,
        'videos.insert': 1600,
        'thumbnails.set': 50,
        'playlistItems.list': 1,
    }
    
    def __init__(self, credentials_file: str = "credentials.json", token_file: str = "token.json", db_manager=None):
        """
        Initialize YouTube API client.
        
        Args:
            credentials_file: Path to OAuth2 credentials JSON
            token_file: Path to store/load access token
            db_manager: DatabaseManager instance for quota persistence (optional)
        """
        self.credentials_file = Path(credentials_file)
        self.token_file = Path(token_file)
        self.logger = logging.getLogger(__name__)
        self.db_manager = db_manager
        
        self.credentials: Optional[Credentials] = None
        self.youtube: Any = None  # googleapiclient Resource object (no type stubs)
        self.quota_used_today = 0
        self.quota_limit = 10000  # Default daily quota
        
        # Load persisted quota if database available
        if self.db_manager:
            self.quota_used_today = self.db_manager.get_quota_usage()
            self.logger.info(f"Loaded quota usage from database: {self.quota_used_today}")
        
        self._authenticate()
    
    def _authenticate(self) -> None:
        """Authenticate with YouTube API using OAuth2."""
        # Load existing token if available
        if self.token_file.exists():
            try:
                self.credentials = Credentials.from_authorized_user_file(
                    str(self.token_file), SCOPES
                )
                self.logger.info("Loaded existing credentials")
            except Exception as e:
                self.logger.error(f"Error loading credentials: {e}")
        
        # Refresh or create new credentials
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                try:
                    self.credentials.refresh(Request())
                    self.logger.info("Refreshed expired credentials")
                except Exception as e:
                    self.logger.error(f"Error refreshing credentials: {e}")
                    self.credentials = None
            
            if not self.credentials:
                if not self.credentials_file.exists():
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_file}. "
                        "Please download OAuth2 credentials from Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_file), SCOPES
                )
                self.credentials = flow.run_local_server(port=0)  # type: ignore[assignment]
                self.logger.info("Created new credentials via OAuth flow")
            
            # Save credentials for future use
            self.token_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_file, 'w') as token:
                if self.credentials:
                    token.write(self.credentials.to_json())
            self.logger.info("Credentials saved successfully")  # Don't log file path
        
        # Build YouTube API client
        self.youtube = build('youtube', 'v3', credentials=self.credentials)
        self.logger.info("YouTube API client initialized")
    
    def check_quota(self, operation: str) -> bool:
        """
        Check if quota is available for operation.
        
        Args:
            operation: API operation name (e.g., 'videos.insert')
        
        Returns:
            True if quota available, False otherwise
        """
        cost = self.QUOTA_COSTS.get(operation, 1)
        
        if self.quota_used_today + cost > self.quota_limit * 0.95:
            self.logger.warning(
                f"Quota limit approaching: {self.quota_used_today}/{self.quota_limit}"
            )
            return False
        
        return True
    
    def track_quota(self, operation: str) -> None:
        """
        Track quota usage for an operation.
        
        Args:
            operation: API operation name
        """
        cost = self.QUOTA_COSTS.get(operation, 1)
        self.quota_used_today += cost
        
        # Persist to database
        if self.db_manager:
            self.db_manager.save_quota_usage(self.quota_used_today)
        
        usage_percent = (self.quota_used_today / self.quota_limit) * 100
        self.logger.info(
            f"Quota used: {self.quota_used_today}/{self.quota_limit} ({usage_percent:.1f}%)"
        )
        
        if usage_percent >= 80:
            self.logger.warning(f"Quota usage at {usage_percent:.1f}%")
    
    def reset_quota_counter(self) -> None:
        """Reset daily quota counter (call at midnight)."""
        self.quota_used_today = 0
        
        # Persist reset to database
        if self.db_manager:
            self.db_manager.save_quota_usage(0)
            # Clean up old quota records (keep last 7 days)
            self.db_manager.clear_old_quota_usage(7)
        
        self.logger.info("Quota counter reset")
    
    def get_channel_info(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """
        Get channel information.
        
        Args:
            channel_id: YouTube channel ID
        
        Returns:
            Channel info dictionary or None
        """
        if not self.check_quota('channels.list'):
            return None
        
        try:
            request = self.youtube.channels().list(
                part='snippet,contentDetails,statistics',
                id=channel_id
            )
            response = request.execute()
            self.track_quota('channels.list')
            
            if response.get('items'):
                return response['items'][0]
            
            self.logger.warning(f"Channel not found: {channel_id}")
            return None
            
        except HttpError as e:
            self.logger.error(f"API error getting channel info: {e}")
            return None
    
    def get_channel_uploads_playlist(self, channel_id: str) -> Optional[str]:
        """
        Get the uploads playlist ID for a channel.
        
        Args:
            channel_id: YouTube channel ID
        
        Returns:
            Uploads playlist ID or None
        """
        channel_info = self.get_channel_info(channel_id)
        
        if channel_info:
            return channel_info['contentDetails']['relatedPlaylists']['uploads']
        
        return None
    
    def get_recent_uploads(
        self,
        channel_id: str,
        max_results: int = 10,
        since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent uploads from a channel.
        
        Args:
            channel_id: YouTube channel ID
            max_results: Maximum number of videos to fetch
            since: Only get videos published after this datetime
        
        Returns:
            List of video info dictionaries
        """
        uploads_playlist_id = self.get_channel_uploads_playlist(channel_id)
        if not uploads_playlist_id:
            return []
        
        if not self.check_quota('playlistItems.list'):
            return []
        
        videos = []
        
        try:
            request = self.youtube.playlistItems().list(
                part='snippet,contentDetails',
                playlistId=uploads_playlist_id,
                maxResults=min(max_results, 50)
            )
            
            while request and len(videos) < max_results:
                response = request.execute()
                self.track_quota('playlistItems.list')
                
                for item in response.get('items', []):
                    snippet = item['snippet']
                    published_at = datetime.fromisoformat(
                        snippet['publishedAt'].replace('Z', '+00:00')
                    )
                    
                    # Filter by date if specified
                    if since and published_at < since:
                        continue
                    
                    video_info = {
                        'video_id': snippet['resourceId']['videoId'],
                        'title': snippet['title'],
                        'description': snippet['description'],
                        'published_at': published_at,
                        'thumbnail_url': snippet['thumbnails']['high']['url'],
                        'channel_id': snippet['channelId'],
                        'channel_title': snippet['channelTitle']
                    }
                    
                    videos.append(video_info)
                
                # Get next page
                request = self.youtube.playlistItems().list_next(request, response)
                
                if not request or len(videos) >= max_results:
                    break
            
            self.logger.info(f"Retrieved {len(videos)} recent uploads from {channel_id}")
            return videos[:max_results]
            
        except HttpError as e:
            self.logger.error(f"API error getting recent uploads: {e}")
            return []
    
    def get_video_details(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a video.
        
        Args:
            video_id: YouTube video ID
        
        Returns:
            Video details dictionary or None
        """
        if not self.check_quota('videos.list'):
            return None
        
        try:
            request = self.youtube.videos().list(
                part='snippet,contentDetails,statistics,status',
                id=video_id
            )
            response = request.execute()
            self.track_quota('videos.list')
            
            if response.get('items'):
                video = response['items'][0]
                
                return {
                    'video_id': video['id'],
                    'title': video['snippet']['title'],
                    'description': video['snippet']['description'],
                    'tags': video['snippet'].get('tags', []),
                    'category_id': video['snippet']['categoryId'],
                    'published_at': datetime.fromisoformat(
                        video['snippet']['publishedAt'].replace('Z', '+00:00')
                    ),
                    'thumbnail_url': video['snippet']['thumbnails']['high']['url'],
                    'duration': video['contentDetails']['duration'],
                    'privacy_status': video['status']['privacyStatus'],
                    'view_count': int(video['statistics'].get('viewCount', 0)),
                    'like_count': int(video['statistics'].get('likeCount', 0)),
                }
            
            self.logger.warning(f"Video not found: {video_id}")
            return None
            
        except HttpError as e:
            self.logger.error(f"API error getting video details: {e}")
            return None
    
    def search_videos(
        self,
        channel_id: str,
        query: Optional[str] = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for videos in a channel.
        
        Args:
            channel_id: YouTube channel ID
            query: Search query (optional)
            max_results: Maximum results to return
        
        Returns:
            List of video info dictionaries
        """
        if not self.check_quota('search.list'):
            return []
        
        try:
            request = self.youtube.search().list(
                part='snippet',
                channelId=channel_id,
                q=query,
                type='video',
                order='date',
                maxResults=min(max_results, 50)
            )
            
            response = request.execute()
            self.track_quota('search.list')
            
            videos = []
            for item in response.get('items', []):
                videos.append({
                    'video_id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'published_at': datetime.fromisoformat(
                        item['snippet']['publishedAt'].replace('Z', '+00:00')
                    ),
                    'thumbnail_url': item['snippet']['thumbnails']['high']['url']
                })
            
            self.logger.info(f"Search returned {len(videos)} videos")
            return videos
            
        except HttpError as e:
            self.logger.error(f"API error searching videos: {e}")
            return []
    
    def get_quota_usage(self) -> Dict[str, Any]:
        """
        Get current quota usage statistics.
        
        Returns:
            Dictionary with quota information
        """
        usage_percent = (self.quota_used_today / self.quota_limit) * 100
        
        return {
            'used': self.quota_used_today,
            'limit': self.quota_limit,
            'remaining': self.quota_limit - self.quota_used_today,
            'percent': usage_percent,
            'status': 'warning' if usage_percent >= 80 else 'ok'
        }
