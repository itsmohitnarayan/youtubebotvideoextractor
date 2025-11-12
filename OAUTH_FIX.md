# OAuth 401 Error Fix

## Problem
You're seeing this error:
```
HTTP error during upload: <HttpError 401 when requesting None returned "Unauthorized". 
Details: "[{'message': 'Unauthorized', 'domain': 'youtube.header', 'reason': 'youtubeSignupRequired', 'location': 'Authorization', 'locationType': 'header'}]">
```

## Cause
The OAuth token has expired or was created with a different Google account.

## Solution

### Option 1: Quick Fix (Recommended)
Run the OAuth refresh script:
```powershell
.\venv\Scripts\python.exe refresh_oauth.py
```

This will:
1. Delete the old `token.json`
2. Open your browser for re-authentication
3. Test the connection
4. Verify your YouTube channel

### Option 2: Manual Fix
1. Delete `token.json` from the project root
2. Run the application again:
   ```powershell
   .\venv\Scripts\python.exe run.py
   ```
3. Browser will open automatically for authentication

## Important Notes

### Which Account to Use?
- **Upload Account**: Sign in with `mossad.streamer@gmail.com` (@mohit8gamer)
- This is where videos will be uploaded
- Make sure this account has a YouTube channel created

### OAuth Consent Screen
If you see "This app isn't verified":
1. Click **"Advanced"**
2. Click **"Go to [App Name] (unsafe)"**
3. Click **"Allow"** for all permissions

### Required Permissions
The app needs these YouTube API permissions:
- ✓ View your YouTube account
- ✓ Upload videos
- ✓ Manage your YouTube videos

## Verification
After authentication, the script will show:
```
Connected YouTube Channel:
  Name: Your Channel Name
  ID: UCxxxxxxxxxxxxxxxxx
  Subscribers: XXX
  Videos: XXX
```

Verify this matches your intended upload channel!

## Common Issues

### "credentials.json not found"
1. Go to https://console.cloud.google.com/
2. Select your project
3. Navigate to: APIs & Services > Credentials
4. Download OAuth 2.0 Client ID JSON
5. Save as `credentials.json` in project root

### Token keeps expiring
- Tokens expire after 7 days if app is in "Testing" mode
- Publish your app in Google Cloud Console to get longer token life
- OR: Run `refresh_oauth.py` weekly

### Wrong channel appears
- Delete `token.json`
- Re-authenticate with the correct Google account
- Make sure you select the right account in the browser

## Next Steps
After fixing OAuth:
1. Close the running application (Ctrl+C)
2. Re-run: `.\venv\Scripts\python.exe run.py`
3. Click "Check Now" to test the workflow
4. Videos should now upload successfully!
