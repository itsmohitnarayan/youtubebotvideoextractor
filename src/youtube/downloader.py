"""
Video Downloader
Handles video downloading using yt-dlp.
"""

import yt_dlp
from pathlib import Path
from typing import Optional, Dict, Any, Callable, List
from datetime import datetime
import logging
import json
import time


class VideoDownloader:
    """Downloads YouTube videos using yt-dlp."""
    
    def __init__(self, output_dir: str = "downloads"):
        """
        Initialize video downloader.
        
        Args:
            output_dir: Directory to save downloaded videos
        """
        self.base_output_dir = Path(output_dir)
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a timestamped session folder for this download session
        session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = self.base_output_dir / f"session_{session_timestamp}"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Download session folder created: {self.output_dir}")
        
        self.current_progress = 0.0
        self.current_status = "idle"
    
    def _progress_hook(self, d: Dict[str, Any]) -> None:
        """
        Progress callback for yt-dlp.
        
        Args:
            d: Progress dictionary from yt-dlp
        """
        if d['status'] == 'downloading':
            if 'downloaded_bytes' in d and 'total_bytes' in d:
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                self.current_progress = percent
                self.current_status = "downloading"
                
                # Log every 10%
                if int(percent) % 10 == 0:
                    speed = d.get('speed', 0)
                    eta = d.get('eta', 0)
                    self.logger.info(
                        f"Download progress: {percent:.1f}% "
                        f"(Speed: {speed/1024/1024:.1f} MB/s, ETA: {eta}s)"
                    )
        
        elif d['status'] == 'finished':
            self.current_progress = 100.0
            self.current_status = "finished"
            self.logger.info(f"Download finished: {d.get('filename', 'unknown')}")
        
        elif d['status'] == 'error':
            self.current_status = "error"
            self.logger.error(f"Download error: {d.get('error', 'unknown error')}")
    
    def download_video(
        self,
        video_id: str,
        custom_filename: Optional[str] = None,
        quality: str = 'best',
        download_thumbnail: bool = True,
        progress_callback: Optional[Callable] = None,
        retry_count: int = 0,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Download video and optionally thumbnail with retry logic.
        
        Args:
            video_id: YouTube video ID
            custom_filename: Custom output filename (without extension)
            quality: Video quality ('best', '1080p', '720p', '480p')
            download_thumbnail: Whether to download thumbnail
            progress_callback: Optional progress callback function
            retry_count: Current retry attempt (internal use)
            max_retries: Maximum number of retry attempts (default: 3)
        
        Returns:
            Dictionary with download results
        """
        self.current_progress = 0.0
        self.current_status = "starting"
        
        # Prepare output template
        if custom_filename:
            output_template = str(self.output_dir / f"{custom_filename}.%(ext)s")
        else:
            output_template = str(self.output_dir / f"{video_id}.%(ext)s")
        
        # Clean up any incomplete downloads (.part files) to avoid resume errors
        for part_file in self.output_dir.glob(f"{video_id}*.part"):
            try:
                part_file.unlink()
                self.logger.info(f"Deleted incomplete download: {part_file}")
            except Exception as e:
                self.logger.warning(f"Could not delete .part file: {e}")
        
        # Format selection based on quality
        format_map = {
            'best': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            '1080p': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]',
            '720p': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]',
            '480p': 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]',
        }
        
        # yt-dlp options
        ydl_opts = {
            'format': format_map.get(quality, format_map['best']),
            'outtmpl': output_template,
            'writethumbnail': download_thumbnail,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'quiet': False,
            'no_warnings': False,
            'progress_hooks': [progress_callback] if progress_callback else [self._progress_hook],
            'merge_output_format': 'mp4',
            'ffmpeg_location': r'C:\Users\MOHIT\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0-full_build\bin',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }] if download_thumbnail else [],
            'concurrent_fragment_downloads': 1,  # Prevent concurrent fragment downloads causing file locks
            'noprogress': False,
            'nopart': False,  # Allow .part files but we clean them up before starting
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # type: ignore[arg-type]
                # Download video
                url = f"https://www.youtube.com/watch?v={video_id}"
                info = ydl.extract_info(url, download=True)
                
                # Get downloaded file path
                if custom_filename:
                    video_path = self.output_dir / f"{custom_filename}.mp4"
                else:
                    video_path = self.output_dir / f"{video_id}.mp4"
                
                # Get thumbnail path if downloaded
                thumbnail_path = None
                if download_thumbnail:
                    # yt-dlp downloads thumbnail with video ID
                    possible_thumbs = list(self.output_dir.glob(f"{video_id}.*"))
                    for thumb in possible_thumbs:
                        if thumb.suffix in ['.jpg', '.jpeg', '.png', '.webp']:
                            thumbnail_path = thumb
                            break
                
                result = {
                    'success': True,
                    'video_id': video_id,
                    'video_path': str(video_path),
                    'thumbnail_path': str(thumbnail_path) if thumbnail_path else None,
                    'title': info.get('title', ''),
                    'description': info.get('description', ''),
                    'tags': info.get('tags', []),
                    'category_id': '20',  # Gaming category (safe default for this channel)
                    'duration': info.get('duration', 0),
                    'filesize': video_path.stat().st_size if video_path.exists() else 0,
                    'format': info.get('format', ''),
                    'resolution': f"{info.get('width', 0)}x{info.get('height', 0)}",
                    'channel': info.get('channel', ''),
                    'channel_id': info.get('channel_id', ''),
                    'upload_date': info.get('upload_date', ''),
                }
                
                self.logger.info(
                    f"Successfully downloaded: {result['title']} "
                    f"({result['filesize'] / 1024 / 1024:.1f} MB)"
                )
                
                return result
                
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error downloading video {video_id} (attempt {retry_count + 1}/{max_retries + 1}): {error_msg}")
            
            # Retry logic with exponential backoff
            if retry_count < max_retries:
                # Exponential backoff: 2, 4, 8 seconds
                delay = 2 ** (retry_count + 1)
                self.logger.warning(f"Retrying download in {delay} seconds... (attempt {retry_count + 2}/{max_retries + 1})")
                time.sleep(delay)
                
                # Retry the download
                return self.download_video(
                    video_id=video_id,
                    custom_filename=custom_filename,
                    quality=quality,
                    download_thumbnail=download_thumbnail,
                    progress_callback=progress_callback,
                    retry_count=retry_count + 1,
                    max_retries=max_retries
                )
            else:
                # Max retries exceeded
                self.logger.error(f"Download failed after {max_retries + 1} attempts")
                return {
                    'success': False,
                    'video_id': video_id,
                    'error': f"Download failed after {max_retries + 1} attempts: {error_msg}"
                }
    
    def extract_metadata(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Extract video metadata without downloading.
        
        Args:
            video_id: YouTube video ID
        
        Returns:
            Dictionary with video metadata or None
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'ffmpeg_location': r'C:\Users\MOHIT\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0-full_build\bin',
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # type: ignore[arg-type]
                url = f"https://www.youtube.com/watch?v={video_id}"
                info = ydl.extract_info(url, download=False)
                
                metadata = {
                    'video_id': video_id,
                    'title': info.get('title', ''),
                    'description': info.get('description', ''),
                    'uploader': info.get('uploader', ''),
                    'uploader_id': info.get('uploader_id', ''),
                    'upload_date': info.get('upload_date', ''),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'tags': info.get('tags', []),
                    'categories': info.get('categories', []),
                    'thumbnail_url': info.get('thumbnail', ''),
                    'resolution': f"{info.get('width', 0)}x{info.get('height', 0)}",
                    'fps': info.get('fps', 0),
                    'format': info.get('format', ''),
                }
                
                self.logger.info(f"Extracted metadata for: {metadata['title']}")
                return metadata
                
        except Exception as e:
            self.logger.error(f"Error extracting metadata for {video_id}: {e}")
            return None
    
    def download_thumbnail(self, video_id: str, thumbnail_url: str) -> Optional[str]:
        """
        Download video thumbnail separately.
        
        Args:
            video_id: YouTube video ID
            thumbnail_url: URL of the thumbnail
        
        Returns:
            Path to downloaded thumbnail or None
        """
        try:
            import requests
            
            response = requests.get(thumbnail_url, timeout=30)
            response.raise_for_status()
            
            # Determine extension from URL or content-type
            content_type = response.headers.get('content-type', '')
            if 'jpeg' in content_type or 'jpg' in content_type:
                ext = 'jpg'
            elif 'png' in content_type:
                ext = 'png'
            elif 'webp' in content_type:
                ext = 'webp'
            else:
                ext = 'jpg'  # Default
            
            thumbnail_path = self.output_dir / f"{video_id}_thumbnail.{ext}"
            
            with open(thumbnail_path, 'wb') as f:
                f.write(response.content)
            
            self.logger.info(f"Downloaded thumbnail: {thumbnail_path}")
            return str(thumbnail_path)
            
        except Exception as e:
            self.logger.error(f"Error downloading thumbnail: {e}")
            return None
    
    def get_available_formats(self, video_id: str) -> List[Dict[str, Any]]:
        """
        Get list of available formats for a video.
        
        Args:
            video_id: YouTube video ID
        
        Returns:
            List of available format dictionaries
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'ffmpeg_location': r'C:\Users\MOHIT\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0-full_build\bin',
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # type: ignore[arg-type]
                url = f"https://www.youtube.com/watch?v={video_id}"
                info = ydl.extract_info(url, download=False)
                
                formats = []
                if info:
                    for fmt in info.get('formats', []) or []:
                        formats.append({
                            'format_id': fmt.get('format_id', ''),
                            'ext': fmt.get('ext', ''),
                            'resolution': fmt.get('resolution', 'audio only'),
                            'filesize': fmt.get('filesize', 0),
                            'vcodec': fmt.get('vcodec', ''),
                            'acodec': fmt.get('acodec', ''),
                        })
                
                self.logger.info(f"Found {len(formats)} formats for {video_id}")
                return formats
                
        except Exception as e:
            self.logger.error(f"Error getting formats for {video_id}: {e}")
            return []
    
    def get_download_progress(self) -> Dict[str, Any]:
        """
        Get current download progress.
        
        Returns:
            Dictionary with progress information
        """
        return {
            'progress': self.current_progress,
            'status': self.current_status
        }
    
    def cleanup_temp_files(self) -> None:
        """Clean up temporary download files."""
        try:
            # Remove .part files (incomplete downloads)
            for part_file in self.output_dir.glob("*.part"):
                part_file.unlink()
                self.logger.info(f"Removed temp file: {part_file}")
            
            # Remove .ytdl files
            for ytdl_file in self.output_dir.glob("*.ytdl"):
                ytdl_file.unlink()
                self.logger.info(f"Removed temp file: {ytdl_file}")
                
        except Exception as e:
            self.logger.error(f"Error cleaning up temp files: {e}")
