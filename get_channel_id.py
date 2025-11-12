"""
Helper script to get Channel ID from YouTube handle/username or URL
Usage: python get_channel_id.py @SnaxGaming
       python get_channel_id.py https://www.youtube.com/@SnaxGaming
"""

import sys
import re
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from youtube.api_client import YouTubeAPIClient


def extract_handle(input_str: str) -> str:
    """
    Extract handle from various input formats.
    
    Args:
        input_str: Can be @handle, handle, or full URL
        
    Returns:
        Clean handle without @ symbol
    """
    # Remove whitespace
    input_str = input_str.strip()
    
    # Pattern 1: Full URL - https://www.youtube.com/@SnaxGaming
    url_pattern = r'youtube\.com/@([^/?]+)'
    match = re.search(url_pattern, input_str)
    if match:
        return match.group(1)
    
    # Pattern 2: Just @handle - @SnaxGaming
    if input_str.startswith('@'):
        return input_str[1:]
    
    # Pattern 3: Just handle - SnaxGaming
    return input_str


def get_channel_id_from_handle(handle: str) -> dict:
    """
    Get channel ID and details from handle using YouTube API.
    
    Args:
        handle: YouTube handle (without @)
        
    Returns:
        Dictionary with channel details
    """
    try:
        # Initialize YouTube API client
        client = YouTubeAPIClient('client_secrets.json', 'data/token.pickle')
        
        # Search for channel by handle
        # YouTube API doesn't directly support handle lookup, so we search
        request = client.youtube.search().list(
            part='snippet',
            q=f'@{handle}',
            type='channel',
            maxResults=5
        )
        response = request.execute()
        
        if not response.get('items'):
            return {'error': f'No channel found for handle: @{handle}'}
        
        # Get the first result (usually the correct one)
        channel_snippet = response['items'][0]['snippet']
        channel_id = response['items'][0]['snippet']['channelId']
        
        # Get full channel details
        channel_request = client.youtube.channels().list(
            part='snippet,statistics',
            id=channel_id
        )
        channel_response = channel_request.execute()
        
        if not channel_response.get('items'):
            return {'error': 'Channel details not found'}
        
        channel = channel_response['items'][0]
        
        return {
            'channel_id': channel_id,
            'channel_name': channel['snippet']['title'],
            'channel_url': f'https://www.youtube.com/channel/{channel_id}',
            'handle': f"@{channel['snippet'].get('customUrl', handle)}",
            'description': channel['snippet']['description'][:200] + '...' if len(channel['snippet']['description']) > 200 else channel['snippet']['description'],
            'subscriber_count': channel['statistics'].get('subscriberCount', 'Hidden'),
            'video_count': channel['statistics'].get('videoCount', '0'),
            'view_count': channel['statistics'].get('viewCount', '0'),
        }
        
    except Exception as e:
        return {'error': f'Error: {str(e)}'}


def main():
    if len(sys.argv) < 2:
        print("Usage: python get_channel_id.py <handle_or_url>")
        print("\nExamples:")
        print("  python get_channel_id.py @SnaxGaming")
        print("  python get_channel_id.py SnaxGaming")
        print("  python get_channel_id.py https://www.youtube.com/@SnaxGaming")
        sys.exit(1)
    
    input_str = sys.argv[1]
    
    print(f"\n🔍 Looking up channel: {input_str}")
    print("=" * 60)
    
    # Extract handle
    handle = extract_handle(input_str)
    print(f"Handle: @{handle}\n")
    
    # Get channel details
    result = get_channel_id_from_handle(handle)
    
    if 'error' in result:
        print(f"❌ {result['error']}")
        sys.exit(1)
    
    # Print results
    print("✅ Channel Found!")
    print("=" * 60)
    print(f"Channel Name:     {result['channel_name']}")
    print(f"Channel ID:       {result['channel_id']}")
    print(f"Handle:           {result['handle']}")
    print(f"Channel URL:      {result['channel_url']}")
    print(f"Subscribers:      {result['subscriber_count']}")
    print(f"Total Videos:     {result['video_count']}")
    print(f"Total Views:      {result['view_count']}")
    print(f"\nDescription:\n{result['description']}")
    print("=" * 60)
    
    # Show how to add to config
    print("\n📝 To monitor this channel, add to config.json:")
    print('-' * 60)
    print(f'''
  "target_channel": {{
    "channel_id": "{result['channel_id']}",
    "channel_url": "{result['channel_url']}",
    "channel_name": "{result['channel_name']}"
  }}
''')
    print('-' * 60)


if __name__ == '__main__':
    main()
