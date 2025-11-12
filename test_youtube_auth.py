"""Test YouTube API authentication and upload capability"""
from pathlib import Path
import sys

print("\n" + "="*80)
print("🔑 TESTING YOUTUBE API AUTHENTICATION")
print("="*80)

# Check if we can import the API client
try:
    sys.path.insert(0, str(Path.cwd() / 'src'))
    from youtube.api_client import YouTubeAPIClient
    print("\n✅ Successfully imported YouTubeAPIClient")
except ImportError as e:
    print(f"\n❌ Failed to import YouTubeAPIClient: {e}")
    sys.exit(1)

# Check credential files
print("\n📁 Checking credential files:")
print("-"*80)

client_secrets = Path('client_secrets.json')
token_file = Path('token.json')

if client_secrets.exists():
    print(f"✅ client_secrets.json exists ({client_secrets.stat().st_size} bytes)")
else:
    print(f"❌ client_secrets.json NOT FOUND")

if token_file.exists():
    print(f"✅ token.json exists ({token_file.stat().st_size} bytes)")
    
    # Try to load and check token
    try:
        import json
        with open(token_file) as f:
            token_data = json.load(f)
        
        print("\n🔍 Token contents:")
        if 'token' in token_data:
            print("   ✅ Token present")
        if 'refresh_token' in token_data:
            print("   ✅ Refresh token present")
        if 'expiry' in token_data:
            print(f"   ⏰ Expiry: {token_data.get('expiry')}")
        
        # Check if token is expired
        if 'expiry' in token_data:
            from datetime import datetime
            try:
                expiry = datetime.fromisoformat(token_data['expiry'].replace('Z', '+00:00'))
                now = datetime.now(expiry.tzinfo)
                if expiry < now:
                    print("   ⚠️ TOKEN IS EXPIRED!")
                else:
                    print(f"   ✅ Token valid until {expiry}")
            except Exception as e:
                print(f"   ⚠️ Could not parse expiry: {e}")
                
    except Exception as e:
        print(f"   ⚠️ Could not read token file: {e}")
else:
    print(f"❌ token.json NOT FOUND")

# Try to initialize API client
print("\n🔧 Initializing YouTube API client:")
print("-"*80)

try:
    api_client = YouTubeAPIClient(
        credentials_file='client_secrets.json',
        token_file='token.json'
    )
    print("✅ API client initialized")
    
    # Check if YouTube API client is available
    print("\n📡 Testing API connectivity...")
    if api_client.youtube:
        try:
            # Get authenticated user's channel info
            response = api_client.youtube.channels().list(
                part='snippet,contentDetails',
                mine=True
            ).execute()
            
            if 'items' in response and len(response['items']) > 0:
                channel = response['items'][0]
                channel_title = channel['snippet']['title']
                channel_id = channel['id']
                
                print(f"✅ Successfully connected to YouTube!")
                print(f"   Channel: {channel_title}")
                print(f"   Channel ID: {channel_id}")
                
                # Check upload playlist
                uploads_playlist = channel['contentDetails']['relatedPlaylists'].get('uploads')
                print(f"   Uploads Playlist: {uploads_playlist}")
                
                print("\n✅ YouTube API is fully functional!")
                print("   You should be able to upload videos.")
                
            else:
                print("⚠️ API call succeeded but no channel found")
                print("   The authenticated account may not have a YouTube channel")
                
        except Exception as e:
            print(f"❌ API call failed: {e}")
            print("   This could be why uploads are failing!")
            import traceback
            traceback.print_exc()
    else:
        print("❌ YouTube API client not initialized!")
        print("   This explains why uploads are returning NULL!")
        
except Exception as e:
    print(f"❌ Failed to initialize API client: {e}")
    print("\n📋 Full error details:")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("💡 RECOMMENDATIONS:")
print("="*80)

print("""
If authentication failed or API test failed:

1. Re-authenticate:
   python refresh_oauth.py

2. Check OAuth credentials:
   - Ensure client_secrets.json has correct credentials
   - Verify OAuth consent screen is configured
   - Check if app is in testing mode (limit 100 test users)

3. Check API enablement:
   - Go to: https://console.cloud.google.com/apis/library
   - Search for "YouTube Data API v3"
   - Ensure it's ENABLED

4. Check quota:
   - Go to: https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas
   - Ensure daily quota not exceeded

5. If API is disabled or restricted:
   - This would explain why uploads return NULL without errors
""")

print("\n" + "="*80 + "\n")
