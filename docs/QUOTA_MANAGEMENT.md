# YouTube API Quota Management Guide

## Understanding Quota

**Daily Limit:** 10,000 units per project (cannot be purchased)
**Reset Time:** Midnight Pacific Time (PST/PDT)

## Quota Costs

| Operation | Units | Frequency in Your App |
|-----------|-------|----------------------|
| Video Upload | 1,600 | Per upload |
| Thumbnail Set | 50 | Per upload |
| Video Update | 50 | When updating metadata |
| Channel Info | 1 | Once per session |
| Search Videos | 100 | Per check (every 10 min) |
| Get Video Details | 1 | Per video found |

## Maximum Daily Capacity

With 10,000 units per day:
- **Max video uploads:** 6 videos/day (9,600 units)
- **Remaining for checks:** 400 units (4 checks or 40 minutes of monitoring)

## Solution: Create Additional Projects

### Step 1: Create New Google Cloud Project

1. Go to: https://console.cloud.google.com/
2. Click project dropdown (top bar)
3. Click "NEW PROJECT"
4. Name it: "YouTube Bot Project 2"
5. Click "CREATE"

### Step 2: Enable YouTube Data API v3

1. In new project, go to: APIs & Services → Library
2. Search for "YouTube Data API v3"
3. Click on it
4. Click "ENABLE"

### Step 3: Create OAuth Credentials

1. Go to: APIs & Services → Credentials
2. Click "CREATE CREDENTIALS" → "OAuth 2.0 Client ID"
3. If asked, configure consent screen:
   - User Type: External
   - App name: YouTube Video Bot
   - User support email: Your email
   - Developer contact: Your email
   - Click "SAVE AND CONTINUE" through all steps
4. Back to Create OAuth Client ID:
   - Application type: Desktop app
   - Name: YouTube Bot Desktop
   - Click "CREATE"
5. Download JSON file
6. Rename it to: `client_secrets_project2.json`

### Step 4: Switch Projects in Your App

#### Option A: Manual Switch (Recommended)
```powershell
# Backup current credentials
Copy-Item client_secrets.json client_secrets_project1.json
Copy-Item token.json token_project1.json

# Use new project
Copy-Item client_secrets_project2.json client_secrets.json
Remove-Item token.json  # Force re-authentication

# Re-authenticate
.\venv\Scripts\python.exe refresh_oauth.py
```

#### Option B: Automatic Project Rotation (Advanced)
Edit `config.json` to add project rotation:
```json
{
  "youtube": {
    "projects": [
      {
        "name": "project1",
        "client_secrets_file": "client_secrets_project1.json",
        "token_file": "token_project1.json",
        "quota_limit": 9500
      },
      {
        "name": "project2",
        "client_secrets_file": "client_secrets_project2.json",
        "token_file": "token_project2.json",
        "quota_limit": 9500
      }
    ]
  }
}
```

## Managing Multiple Projects

### Quick Switch Script

Create `switch_project.py`:
```python
import shutil
import sys

project = sys.argv[1] if len(sys.argv) > 1 else '1'

# Switch to specified project
shutil.copy(f'client_secrets_project{project}.json', 'client_secrets.json')
shutil.copy(f'token_project{project}.json', 'token.json')

print(f"✅ Switched to Project {project}")
print("Run the application now: .\\venv\\Scripts\\python.exe run.py")
```

Usage:
```powershell
# Switch to project 1
python switch_project.py 1

# Switch to project 2
python switch_project.py 2
```

## Best Practices

1. **Monitor Quota:** Check quota usage before uploads
2. **Rotate Projects:** Switch projects when quota is low
3. **Cache Data:** Reduce API calls by caching channel info
4. **Batch Operations:** Group API calls when possible
5. **Optimize Checks:** Reduce monitoring frequency during low-activity hours

## Current Quota Status

Check your quota at:
https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas

## Quota Reset Schedule

**Pacific Time (PT):**
- Resets at: 12:00 AM (midnight)
- Your time: Check timezone converter

**Example:**
- If you're in India (IST): Reset at 1:30 PM
- If you're in EST: Reset at 3:00 AM
- If you're in UK (GMT): Reset at 8:00 AM

## Troubleshooting

### "Quota exceeded" Error
- **Solution:** Wait for reset or switch project

### "Invalid credentials" After Switch
- **Solution:** Delete token.json and re-run refresh_oauth.py

### Quota Not Resetting
- **Solution:** Check you're looking at correct project in Google Cloud Console

## Additional Resources

- [YouTube API Quota Calculator](https://developers.google.com/youtube/v3/determine_quota_cost)
- [Google Cloud Console](https://console.cloud.google.com/)
- [YouTube Data API Documentation](https://developers.google.com/youtube/v3)

---

**Remember:** Creating multiple projects is the ONLY way to get more quota. Google does not sell additional quota for YouTube Data API v3.
