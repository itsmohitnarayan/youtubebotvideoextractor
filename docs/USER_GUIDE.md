# YouTube Bot Video Extractor - User Guide

Complete guide to using YouTube Bot Video Extractor for automated video monitoring and replication.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [First Time Setup](#first-time-setup)
3. [Basic Operations](#basic-operations)
4. [Configuration Guide](#configuration-guide)
5. [Monitoring Videos](#monitoring-videos)
6. [Queue Management](#queue-management)
7. [Upload Settings](#upload-settings)
8. [Active Hours](#active-hours)
9. [System Tray](#system-tray)
10. [Dashboard Overview](#dashboard-overview)
11. [Advanced Features](#advanced-features)
12. [Best Practices](#best-practices)

---

## Getting Started

### Prerequisites

Before using the application, ensure you have:

✅ **Completed installation** (see [SETUP.md](SETUP.md))  
✅ **YouTube API credentials** configured  
✅ **Target channel ID** identified  
✅ **OAuth authentication** completed  
✅ **Configuration file** customized  

---

## First Time Setup

### Step 1: Launch Application

```powershell
# Navigate to project directory
cd youtubebotvideoextractor

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run application
python src/main.py
```

### Step 2: OAuth Authentication

On first run, the application will:

1. **Open browser** automatically
2. Show **Google OAuth consent screen**
3. Request permissions:
   - ✅ View your YouTube account
   - ✅ Manage your YouTube videos
   - ✅ Upload videos

4. **Click "Allow"** to grant permissions
5. Browser will show "Authentication successful"
6. Return to application

**Token saved to**: `data/token.json`

> **Note**: This token allows the app to act on your behalf. Keep it secure!

### Step 3: Verify Configuration

The application will verify:

- ✅ Configuration file valid
- ✅ API credentials present
- ✅ Target channel accessible
- ✅ Upload channel authenticated
- ✅ Directory permissions

If any issues, check logs in `logs/app.log`

### Step 4: Start Monitoring

Click **"Start Monitoring"** or the app will auto-start if configured.

---

## Basic Operations

### Starting Monitoring

**GUI**:
- Click **Start** button in main window
- Or: System tray → **Resume Monitoring**

**Automatic**:
```json
{
  "monitoring": {
    "auto_start": true
  }
}
```

### Stopping Monitoring

**GUI**:
- Click **Pause** button
- Or: System tray → **Pause Monitoring**

**Automatic** (via Active Hours):
- Will pause outside configured active hours
- Resumes automatically when active hours begin

### Force Check Now

**GUI**:
- Click **Check Now** button
- Or: System tray → **Check Now**

**Effect**:
- Immediately checks for new videos
- Bypasses normal check interval
- Does NOT count against active hours

### View Progress

**Dashboard shows**:
- Current status (monitoring/paused)
- Last check time
- Videos in queue
- Download progress
- Upload progress
- Recent activity

### Exit Application

**Options**:
1. **Close window**: Minimizes to system tray (still running)
2. **System tray → Exit**: Completely closes application
3. **File → Exit**: Same as system tray

---

## Configuration Guide

Configuration is in `config.json`. Edit with any text editor.

### Basic Structure

```json
{
  "monitoring": { ... },
  "active_hours": { ... },
  "download": { ... },
  "upload": { ... },
  "notifications": { ... },
  "performance": { ... }
}
```

### Monitoring Settings

```json
{
  "monitoring": {
    "enabled": true,
    "auto_start": true,
    "source_channel_id": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
    "check_interval_minutes": 10,
    "max_videos_per_check": 5,
    "lookback_hours": 24
  }
}
```

**Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable monitoring |
| `auto_start` | boolean | `true` | Start on application launch |
| `source_channel_id` | string | Required | Channel to monitor (UC...) |
| `check_interval_minutes` | integer | `10` | Minutes between checks |
| `max_videos_per_check` | integer | `5` | Max videos to process per check |
| `lookback_hours` | integer | `24` | How far back to check on first run |

**Tips**:
- Lower `check_interval_minutes` = faster detection, higher quota usage
- Higher `lookback_hours` = catch older videos, more quota usage
- Set `auto_start: false` for manual control

### Active Hours

Only monitor during specific hours:

```json
{
  "active_hours": {
    "enabled": true,
    "start": "10:00",
    "end": "22:00",
    "timezone": "local"
  }
}
```

**Examples**:

**9 AM - 5 PM (Office Hours)**:
```json
{
  "start": "09:00",
  "end": "17:00"
}
```

**24/7 Monitoring**:
```json
{
  "enabled": false
}
```

**Night Shift (10 PM - 6 AM)**:
```json
{
  "start": "22:00",
  "end": "06:00"  // Crosses midnight
}
```

### Download Settings

```json
{
  "download": {
    "directory": "downloads",
    "video_quality": "best",
    "format": "mp4",
    "max_filesize_mb": 2048,
    "timeout_seconds": 300,
    "retries": 3
  }
}
```

**Quality Options**:
- `"best"`: Highest available quality
- `"best[height<=1080]"`: Max 1080p
- `"best[height<=720]"`: Max 720p
- `"bestvideo[ext=mp4]+bestaudio[ext=m4a]"`: Best MP4 video + M4A audio

**Format Options**:
- `"mp4"`: Most compatible
- `"webm"`: Smaller file size
- `"mkv"`: Preserves all streams

### Upload Settings

```json
{
  "upload": {
    "title_prefix": "",
    "title_suffix": "",
    "description_append": "\n\nReuploaded from: {source_channel}",
    "privacy_status": "public",
    "category_id": "22",
    "tags": [],
    "made_for_kids": false
  }
}
```

**Privacy Options**:
- `"public"`: Anyone can watch
- `"unlisted"`: Only people with link
- `"private"`: Only you can watch

**Category IDs** (common):
- `"1"`: Film & Animation
- `"10"`: Music
- `"17"`: Sports
- `"20"`: Gaming
- `"22"`: People & Blogs
- `"24"`: Entertainment
- `"26"`: Howto & Style
- `"28"`: Science & Technology

See full list: https://developers.google.com/youtube/v3/docs/videoCategories/list

### Notification Settings

```json
{
  "notifications": {
    "enabled": true,
    "on_download": true,
    "on_upload": true,
    "on_error": true,
    "sound": false,
    "duration_ms": 5000
  }
}
```

**Effects**:
- Desktop notifications (Windows 10/11)
- System tray balloon tips
- Optional sound alerts

### Performance Settings

```json
{
  "performance": {
    "max_concurrent_downloads": 2,
    "max_concurrent_uploads": 1,
    "download_chunk_size_kb": 1024,
    "memory_limit_mb": 150
  }
}
```

**Recommendations**:
- **Low-end PC**: `max_concurrent_downloads: 1`
- **Mid-range PC**: `max_concurrent_downloads: 2` (default)
- **High-end PC**: `max_concurrent_downloads: 3`

---

## Monitoring Videos

### How Monitoring Works

1. **Timer triggers** (every X minutes)
2. **Check active hours** (if enabled)
3. **Query YouTube API** for new videos
4. **Compare with database** (duplicate check)
5. **Add to queue** (new videos only)
6. **Start download** (automatic)

### Video Detection

The app detects new videos by:

✅ **Checking upload date** (after last check time)  
✅ **Comparing video IDs** (not in database)  
✅ **Verifying availability** (not private/deleted)  

### Manual Check

Force immediate check:

**GUI**: Click **"Check Now"** button

**Effect**:
- Queries API immediately
- Bypasses timer
- Useful after known upload

### View Detected Videos

**Dashboard** shows:
- Recently detected videos
- Video title, thumbnail, duration
- Detection time
- Current status (queued/downloading/uploading/completed)

### Skip Videos

To skip specific videos:

1. Open **Queue Manager**
2. Find video in queue
3. Right-click → **Cancel**
4. Video marked as "skipped" in database

---

## Queue Management

### Queue Overview

The queue manages video processing workflow:

```
Detected → Queued → Downloading → Downloaded → Uploading → Completed
```

### View Queue

**GUI**: Click **"Queue"** tab

Shows:
- All videos in queue
- Current status
- Priority level
- Retry count
- Error messages (if any)

### Queue Priority

Videos processed by priority:

1. **HIGH**: User-added manually
2. **NORMAL**: Auto-detected (default)
3. **LOW**: Retry after failure

### Modify Queue

**Add video manually**:
1. Click **"Add Video"**
2. Enter video URL or ID
3. Select priority
4. Click **"Add to Queue"**

**Cancel video**:
1. Select video in queue
2. Click **"Cancel"**
3. Confirm action

**Retry failed**:
1. Find failed video
2. Click **"Retry"**
3. Moves back to queue

**Clear completed**:
- Click **"Clear Completed"**
- Removes successful uploads from queue
- Data still in database

### Queue Statistics

Dashboard shows:
- Total videos in queue
- Downloading: X
- Uploading: Y
- Completed today: Z
- Failed: W

---

## Upload Settings

### Metadata Customization

#### Title Formatting

**Preserve original**:
```json
{
  "upload": {
    "title_prefix": "",
    "title_suffix": ""
  }
}
```
Result: `"Original Video Title"`

**Add prefix**:
```json
{
  "upload": {
    "title_prefix": "[Reuploaded] "
  }
}
```
Result: `"[Reuploaded] Original Video Title"`

**Add suffix**:
```json
{
  "upload": {
    "title_suffix": " - Backup Copy"
  }
}
```
Result: `"Original Video Title - Backup Copy"`

#### Description Customization

**Preserve original + add note**:
```json
{
  "upload": {
    "description_append": "\n\n---\nReuploaded from: {source_channel}\nOriginal: {source_url}"
  }
}
```

**Variables available**:
- `{source_channel}`: Source channel name
- `{source_url}`: Original video URL
- `{source_id}`: Original video ID
- `{upload_date}`: Current date/time

#### Tags Management

**Keep original tags**:
```json
{
  "upload": {
    "tags": []  // Empty = use original
  }
}
```

**Add custom tags**:
```json
{
  "upload": {
    "tags": ["reupload", "backup", "archive"]
  }
}
```
Result: Original tags + your custom tags

**Replace all tags**:
```json
{
  "upload": {
    "tags": ["custom", "tags", "only"],
    "replace_tags": true
  }
}
```

### Thumbnail Handling

**Default**: Original thumbnail downloaded and re-uploaded

**Custom thumbnail**:
```json
{
  "upload": {
    "custom_thumbnail": "path/to/custom_thumb.jpg"
  }
}
```

**Thumbnail requirements**:
- Format: JPG, PNG
- Size: <2 MB
- Dimensions: 1280×720 (16:9 recommended)
- Minimum: 640×360

### Privacy & Visibility

**Public** (default):
- Anyone can find and watch
- Appears in search results
- Counts toward channel views

**Unlisted**:
- Only people with link can watch
- Won't appear in search
- Won't appear on channel page

**Private**:
- Only you can watch
- Invisible to others
- Good for testing

```json
{
  "upload": {
    "privacy_status": "unlisted"  // or "public" or "private"
  }
}
```

---

## Active Hours

### Purpose

Limit monitoring to specific hours to:
- Save API quota
- Reduce CPU usage
- Only operate during office hours
- Respect sleep schedule

### Configuration

```json
{
  "active_hours": {
    "enabled": true,
    "start": "10:00",
    "end": "22:00"
  }
}
```

### Behavior

**During active hours** (10:00 - 22:00):
- ✅ Monitoring active
- ✅ Downloads allowed
- ✅ Uploads allowed
- ✅ Checks run on schedule

**Outside active hours** (22:00 - 10:00):
- ⏸️ Monitoring paused
- ⏸️ No new checks
- ✅ Current downloads continue
- ✅ Current uploads continue

### Catch-Up Mechanism

When active hours resume:
- ✅ Checks for videos uploaded during off-hours
- ✅ Uses `lookback_hours` setting
- ✅ Processes all missed videos

### Override Active Hours

**Manual override**:
- Click **"Check Now"** anytime
- Works even outside active hours
- Single check, doesn't resume monitoring

---

## System Tray

### Tray Icon

The system tray icon shows current status:

- 🟢 **Green**: Monitoring active, no activity
- 🔵 **Blue**: Downloading video
- 🟡 **Yellow**: Uploading video
- 🔴 **Red**: Error occurred
- ⚫ **Gray**: Monitoring paused

### Tray Menu

Right-click icon for menu:

**📊 Show Dashboard**
- Opens main window
- Shows statistics and queue

**▶️ Resume Monitoring** / **⏸️ Pause Monitoring**
- Toggle monitoring on/off

**🔄 Check Now**
- Force immediate check
- Bypass timer and active hours

**⚙️ Settings**
- Open settings dialog
- Change configuration

**📋 View Logs**
- Open log viewer
- Filter by level (INFO/WARNING/ERROR)

**❌ Exit**
- Close application completely
- Graceful shutdown

### Notifications

**Balloon Tips** appear for:

✅ **New video detected**
```
New video found!
"Video Title Here"
Starting download...
```

✅ **Download complete**
```
Download complete
"Video Title"
Starting upload...
```

✅ **Upload complete**
```
Upload successful! 🎉
"Video Title"
Available at: youtube.com/watch?v=...
```

❌ **Error occurred**
```
Error during upload
"Video Title"
Click for details
```

### Click Actions

**Single-click**: Show/hide main window  
**Double-click**: Show dashboard  
**Right-click**: Show menu  

---

## Dashboard Overview

### Status Panel

Shows real-time status:

```
━━━━━━━━━━━━━━━━━━━━━━━━━
Status:      Monitoring ✅
Last Check:  2 minutes ago
Next Check:  8 minutes
Videos:      3 in queue
━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Statistics

**Today's Stats**:
- Videos detected: X
- Downloads: Y completed
- Uploads: Z completed
- Errors: W

**All-Time Stats**:
- Total videos processed
- Success rate (%)
- Average processing time
- Quota used today

### Activity Log

Real-time activity feed:

```
12:34 PM - New video detected: "Example Video"
12:35 PM - Download started: example_id.mp4
12:38 PM - Download complete (3.2 MB, 3m 15s)
12:39 PM - Upload started to YouTube
12:45 PM - Upload complete! Video ID: abc123xyz
```

### Progress Indicators

**Download Progress**:
```
Downloading: video_title.mp4
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 67%
Speed: 2.5 MB/s | ETA: 2m 15s
```

**Upload Progress**:
```
Uploading: video_title.mp4
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 82%
Speed: 1.8 MB/s | ETA: 1m 05s
```

---

## Advanced Features

### Custom Scripts

Run custom scripts on events:

```json
{
  "advanced": {
    "hooks": {
      "on_download_complete": "scripts/custom_post_download.ps1",
      "on_upload_complete": "scripts/notify_webhook.ps1"
    }
  }
}
```

**Available hooks**:
- `on_video_detected`
- `on_download_start`
- `on_download_complete`
- `on_upload_start`
- `on_upload_complete`
- `on_error`

### Database Queries

View processed videos:

```powershell
sqlite3 data/app.db "SELECT * FROM videos WHERE status='completed' ORDER BY created_at DESC LIMIT 10"
```

### API Direct Access

For advanced users, use the Python API:

```python
from src.youtube.api_client import YouTubeAPIClient

client = YouTubeAPIClient()
videos = client.search_videos("channel_id", published_after="2024-01-01")
```

### Logging Levels

Change log verbosity:

```json
{
  "logging": {
    "level": "DEBUG"  // INFO, WARNING, ERROR, DEBUG
  }
}
```

**DEBUG**: All events (very verbose)  
**INFO**: Normal operations  
**WARNING**: Potential issues  
**ERROR**: Failures only  

---

## Best Practices

### Quota Management

✅ **DO**:
- Use active hours to limit monitoring
- Increase check interval to 15-30 minutes
- Monitor quota usage in logs
- Plan uploads based on quota availability

❌ **DON'T**:
- Check every 5 minutes (wastes quota)
- Monitor 24/7 if not needed
- Ignore quota warnings

See [API_LIMITS.md](API_LIMITS.md) for details.

### Performance

✅ **DO**:
- Enable auto-cleanup for old downloads
- Limit concurrent downloads to 2
- Use SSD for download directory
- Close other bandwidth-heavy apps

❌ **DON'T**:
- Download to slow HDD
- Run 5+ downloads simultaneously
- Keep 100+ GB of downloads

### Security

✅ **DO**:
- Keep `client_secrets.json` private
- Protect `data/token.json`
- Use strong passwords for Google account
- Enable 2FA on Google account

❌ **DON'T**:
- Share OAuth tokens
- Commit secrets to git
- Use weak passwords
- Disable 2FA

### Reliability

✅ **DO**:
- Check logs regularly
- Review failed uploads
- Test with 1-2 videos first
- Monitor disk space

❌ **DON'T**:
- Ignore errors
- Assume everything works
- Fill up disk completely
- Never check logs

### Legal Compliance

✅ **DO**:
- Get permission from content owner
- Respect copyright laws
- Read YouTube TOS
- Use for legitimate purposes

❌ **DON'T**:
- Reupload copyrighted content without permission
- Violate YouTube TOS
- Use for spam or abuse
- Monetize others' content

---

## Keyboard Shortcuts

### Main Window

| Shortcut | Action |
|----------|--------|
| `Ctrl+S` | Start/pause monitoring |
| `Ctrl+R` | Check now |
| `Ctrl+Q` | Add video to queue |
| `Ctrl+L` | View logs |
| `Ctrl+,` | Settings |
| `Ctrl+W` | Close window (minimize to tray) |
| `Ctrl+Q` | Quit application |
| `F5` | Refresh queue |
| `F11` | Toggle fullscreen |

### Queue Manager

| Shortcut | Action |
|----------|--------|
| `Delete` | Cancel selected video |
| `Ctrl+A` | Select all |
| `Ctrl+C` | Copy video details |
| `Ctrl+F` | Find/filter videos |

---

## Tips & Tricks

### Tip 1: Test with Single Video First

```json
{
  "monitoring": {
    "max_videos_per_check": 1
  }
}
```

### Tip 2: Bandwidth-Saving Mode

```json
{
  "download": {
    "video_quality": "best[height<=720]"  // 720p max
  }
}
```

### Tip 3: Silent Mode (No Notifications)

```json
{
  "notifications": {
    "enabled": false
  }
}
```

### Tip 4: Catch-Up After Downtime

Increase `lookback_hours` to catch missed videos:
```json
{
  "monitoring": {
    "lookback_hours": 72  // 3 days
  }
}
```

### Tip 5: Monitor Logs in Real-Time

```powershell
Get-Content logs/app.log -Wait -Tail 50
```

---

## Getting Help

If you encounter issues:

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review logs: `logs/app.log`
3. Check configuration: `config.json`
4. Search [GitHub Issues](https://github.com/itsmohitnarayan/youtubebotvideoextractor/issues)
5. Create new issue with details

---

**Last Updated**: November 10, 2025  
**Version**: 1.0.0  
**Tested On**: Windows 10/11 (64-bit)
