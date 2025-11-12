"""
Video Uploader
Handles video uploading to YouTube using YouTube Data API v3.
"""

from pathlib import Path
from typing import Optional, Dict, Any, Callable
import logging
import time
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError


class VideoUploader:
    """Handles video uploads to YouTube."""
    
    def __init__(self, api_client):
        """
        Initialize video uploader.
        
        Args:
            api_client: YouTubeAPIClient instance
        """
        self.api_client = api_client
        self.logger = logging.getLogger(__name__)
    
    def upload(
        self,
        video_path: str,
        title: str,
        description: str = "",
        tags: Optional[list] = None,
        category_id: str = "22",
        privacy_status: str = "public",
        progress_callback: Optional[Callable] = None,
        retry_count: int = 0,
        max_retries: int = 3
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Upload video to YouTube with retry logic.
        
        Args:
            video_path: Path to video file
            title: Video title (max 100 chars)
            description: Video description (max 5000 chars)
            tags: List of tags (max 500 chars total)
            category_id: YouTube category ID (default: 22 = People & Blogs)
            privacy_status: Privacy status (public, private, unlisted)
            progress_callback: Optional callback for upload progress
            retry_count: Current retry attempt (internal use)
            max_retries: Maximum number of retry attempts (default: 3)
        
        Returns:
            Tuple of (video_id, error_message). If successful, error_message is None.
            If failed, video_id is None and error_message contains the error.
        """
        video_file = Path(video_path)
        
        if not video_file.exists():
            error_msg = f"Video file not found: {video_path}"
            self.logger.error(error_msg)
            return None, error_msg
        
        # Truncate title to 100 chars
        title = title[:100]
        
        # Truncate description to 5000 chars
        description = description[:5000]
        
        # Truncate tags if total length exceeds 500 chars
        if tags:
            total_tag_length = sum(len(tag) for tag in tags)
            if total_tag_length > 500:
                truncated_tags = []
                current_length = 0
                for tag in tags:
                    if current_length + len(tag) <= 500:
                        truncated_tags.append(tag)
                        current_length += len(tag)
                    else:
                        break
                tags = truncated_tags
        
        # Prepare video metadata
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags or [],
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False,
            }
        }
        
        try:
            # Check quota before upload
            if not self.api_client.check_quota(1600):
                error_msg = "Insufficient YouTube API quota for video upload"
                self.logger.error(error_msg)
                return None, error_msg
            
            # Prepare media file
            media = MediaFileUpload(
                str(video_file),
                chunksize=1024*1024,  # 1MB chunks
                resumable=True
            )
            
            self.logger.info(f"Starting upload: {title}")
            
            # Initialize upload request
            request = self.api_client.youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )
            
            # Track quota (method looks up cost internally)
            self.api_client.track_quota('videos.insert')
            
            # Execute resumable upload
            response = None
            while response is None:
                status, response = request.next_chunk()
                
                if status and progress_callback:
                    progress_info = {
                        'bytes_uploaded': status.resumable_progress,
                        'total_bytes': status.total_size,
                        'progress': (status.resumable_progress / status.total_size) * 100
                    }
                    progress_callback(progress_info)
            
            video_id = response.get('id')
            self.logger.info(f"Upload completed: {video_id}")
            
            return video_id, None
            
        except HttpError as e:
            error_msg = f"YouTube API HTTP error: {e.resp.status} - {e.content.decode('utf-8') if e.content else 'No details'}"
            self.logger.error(f"Upload error (attempt {retry_count + 1}/{max_retries + 1}): {error_msg}")
            
            # Retry on transient errors (5xx server errors, rate limiting)
            status_code = e.resp.status
            should_retry = status_code >= 500 or status_code == 429  # Server errors or rate limit
            
            if should_retry and retry_count < max_retries:
                delay = 2 ** (retry_count + 1)  # Exponential backoff: 2, 4, 8 seconds
                self.logger.warning(f"Retrying upload in {delay} seconds... (attempt {retry_count + 2}/{max_retries + 1})")
                time.sleep(delay)
                
                return self.upload(
                    video_path=video_path,
                    title=title,
                    description=description,
                    tags=tags,
                    category_id=category_id,
                    privacy_status=privacy_status,
                    progress_callback=progress_callback,
                    retry_count=retry_count + 1,
                    max_retries=max_retries
                )
            
            return None, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error during upload: {type(e).__name__}: {str(e)}"
            self.logger.error(f"Upload exception (attempt {retry_count + 1}/{max_retries + 1}): {error_msg}", exc_info=True)
            
            # Retry on unexpected errors (network issues, etc.)
            if retry_count < max_retries:
                delay = 2 ** (retry_count + 1)
                self.logger.warning(f"Retrying upload in {delay} seconds... (attempt {retry_count + 2}/{max_retries + 1})")
                time.sleep(delay)
                
                return self.upload(
                    video_path=video_path,
                    title=title,
                    description=description,
                    tags=tags,
                    category_id=category_id,
                    privacy_status=privacy_status,
                    progress_callback=progress_callback,
                    retry_count=retry_count + 1,
                    max_retries=max_retries
                )
            
            return None, error_msg
    
    def set_thumbnail(
        self,
        video_id: str,
        thumbnail_path: str
    ) -> bool:
        """
        Set custom thumbnail for uploaded video.
        
        Args:
            video_id: YouTube video ID
            thumbnail_path: Path to thumbnail image
        
        Returns:
            True if successful, False otherwise
        """
        thumbnail_file = Path(thumbnail_path)
        
        if not thumbnail_file.exists():
            self.logger.error(f"Thumbnail file not found: {thumbnail_path}")
            return False
        
        try:
            request = self.api_client.youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            )
            
            response = request.execute()
            
            # Track quota (method looks up cost internally)
            self.api_client.track_quota('thumbnails.set')
            
            self.logger.info(f"Successfully set thumbnail for video {video_id}")
            return True
            
        except HttpError as e:
            self.logger.error(f"HTTP error setting thumbnail: {e}")
            return False
            
        except Exception as e:
            self.logger.error(f"Unexpected error setting thumbnail: {e}")
            return False
    
    def update_metadata(
        self,
        video_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[list] = None,
        category_id: Optional[str] = None,
        privacy_status: Optional[str] = None
    ) -> bool:
        """
        Update video metadata.
        
        Args:
            video_id: YouTube video ID
            title: New title (optional)
            description: New description (optional)
            tags: New tags (optional)
            category_id: New category ID (optional)
            privacy_status: New privacy status (optional)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current video details
            request = self.api_client.youtube.videos().list(
                part='snippet,status',
                id=video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                self.logger.error(f"Video not found: {video_id}")
                return False
            
            video = response['items'][0]
            
            # Update fields
            if title:
                video['snippet']['title'] = title[:100]
            if description:
                video['snippet']['description'] = description[:5000]
            if tags is not None:
                video['snippet']['tags'] = tags
            if category_id:
                video['snippet']['categoryId'] = category_id
            if privacy_status:
                video['status']['privacyStatus'] = privacy_status
            
            # Prepare update body
            body = {
                'id': video_id,
                'snippet': video['snippet'],
                'status': video['status']
            }
            
            # Execute update
            request = self.api_client.youtube.videos().update(
                part='snippet,status',
                body=body
            )
            
            response = request.execute()
            
            # Track quota (method looks up cost internally)
            self.api_client.track_quota('videos.update')
            
            self.logger.info(f"Successfully updated metadata for video {video_id}")
            return True
            
        except HttpError as e:
            self.logger.error(f"HTTP error updating metadata: {e}")
            return False
            
        except Exception as e:
            self.logger.error(f"Unexpected error updating metadata: {e}")
            return False
    
    def delete_video(self, video_id: str) -> bool:
        """
        Delete video from YouTube.
        
        Args:
            video_id: YouTube video ID
        
        Returns:
            True if successful, False otherwise
        """
        try:
            request = self.api_client.youtube.videos().delete(
                id=video_id
            )
            
            request.execute()
            
            # Track quota (method looks up cost internally)
            self.api_client.track_quota('videos.delete')
            
            self.logger.info(f"Successfully deleted video {video_id}")
            return True
            
        except HttpError as e:
            self.logger.error(f"HTTP error deleting video: {e}")
            return False
            
        except Exception as e:
            self.logger.error(f"Unexpected error deleting video: {e}")
            return False
