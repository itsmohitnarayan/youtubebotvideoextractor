"""
OAuth Token Refresh Script
Run this script to re-authenticate with YouTube API when you get 401 errors.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from youtube.api_client import YouTubeAPIClient


def main():
    """Refresh OAuth token by re-authenticating."""
    print("=" * 60)
    print("YouTube API OAuth Token Refresh")
    print("=" * 60)
    print()
    
    # Check if token exists
    token_file = Path("token.json")
    if token_file.exists():
        print(f"Found existing token: {token_file}")
        print("Deleting old token to force re-authentication...")
        token_file.unlink()
        print("✓ Old token deleted")
        print()
    
    # Check for credentials - try both filenames
    creds_file = None
    for filename in ["credentials.json", "client_secrets.json"]:
        if Path(filename).exists():
            creds_file = Path(filename)
            break
    
    if not creds_file:
        print("ERROR: OAuth credentials not found!")
        print("Looking for: credentials.json OR client_secrets.json")
        print()
        print("Please download OAuth2 credentials from Google Cloud Console:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Select your project")
        print("3. Go to APIs & Services > Credentials")
        print("4. Download OAuth 2.0 Client ID JSON")
        print("5. Save as credentials.json in the project root")
        return 1
    
    print(f"Found credentials: {creds_file}")
    print()
    print("Starting OAuth flow...")
    print("Your browser will open for authentication.")
    print("Please sign in with your YouTube account (mossad.streamer@gmail.com).")
    print()
    
    try:
        # Initialize API client (will trigger OAuth flow)
        api_client = YouTubeAPIClient(
            credentials_file=str(creds_file),
            token_file="token.json"
        )
        
        print()
        print("=" * 60)
        print("✓ Authentication successful!")
        print("=" * 60)
        print()
        
        # Test the connection
        print("Testing API connection...")
        try:
            request = api_client.youtube.channels().list(
                part="snippet,contentDetails,statistics",
                mine=True
            )
            response = request.execute()
            
            if response.get('items'):
                channel = response['items'][0]
                snippet = channel['snippet']
                stats = channel['statistics']
                
                print()
                print("Connected YouTube Channel:")
                print(f"  Name: {snippet['title']}")
                print(f"  ID: {channel['id']}")
                print(f"  Subscribers: {stats.get('subscriberCount', 'Hidden')}")
                print(f"  Videos: {stats.get('videoCount', '0')}")
                print()
            
            print("✓ API connection test successful!")
            print()
            print("You can now run the application:")
            print("  .\\venv\\Scripts\\python.exe run.py")
            print()
            
        except Exception as e:
            print(f"WARNING: API test failed: {e}")
            print("Token was created but API test failed.")
            print("Try running the application anyway.")
            print()
        
        return 0
        
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return 1
        
    except Exception as e:
        print(f"ERROR: Authentication failed: {e}")
        print()
        print("Common issues:")
        print("1. Wrong Google account selected")
        print("2. App not verified (click 'Advanced' > 'Go to app')")
        print("3. Insufficient permissions granted")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
