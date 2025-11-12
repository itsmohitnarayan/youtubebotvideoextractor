# Troubleshooting Guide

Common issues and solutions for YouTube Bot Video Extractor.

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Authentication Problems](#authentication-problems)
3. [Download Failures](#download-failures)
4. [Upload Errors](#upload-errors)
5. [Performance Issues](#performance-issues)
6. [GUI Problems](#gui-problems)
7. [Network Issues](#network-issues)
8. [Database Errors](#database-errors)
9. [Quota Limit Issues](#quota-limit-issues)
10. [General Troubleshooting](#general-troubleshooting)

---

## Installation Issues

### Problem: `pip install` fails with permission errors

**Symptoms**:
```
ERROR: Could not install packages due to an OSError: [WinError 5] Access is denied
```

**Solution**:
```powershell
# Run PowerShell as Administrator, then:
pip install --user -r requirements.txt
```

Or create virtual environment first:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

### Problem: Python not found or wrong version

**Symptoms**:
```
'python' is not recognized as an internal or external command
```

**Solution**:
1. Install Python 3.11+ from [python.org](https://www.python.org/downloads/)
2. During installation, check ✅ **"Add Python to PATH"**
3. Restart PowerShell
4. Verify: `python --version`

---

### Problem: Virtual environment activation fails

**Symptoms**:
```
.\venv\Scripts\Activate.ps1 : File cannot be loaded because running scripts is disabled
```

**Solution**:
```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate again
.\venv\Scripts\Activate.ps1
```

---

## Authentication Problems

### Problem: OAuth authentication fails or hangs

**Symptoms**:
- Browser doesn't open
- "Authorization failed" error
- Stuck on "Please visit this URL" message

**Solution**:

1. **Check `client_secrets.json`**:
   ```json
   {
     "installed": {
       "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
       "project_id": "your-project",
       "auth_uri": "https://accounts.google.com/o/oauth2/auth",
       "token_uri": "https://oauth2.googleapis.com/token",
       "client_secret": "YOUR_SECRET",
       "redirect_uris": ["http://localhost"]
     }
   }
   ```

2. **Delete old tokens**:
   ```powershell
   Remove-Item data/token.json -ErrorAction SilentlyContinue
   ```

3. **Re-authenticate**:
   ```powershell
   python src/main.py
   ```

4. **If browser doesn't open**, manually visit the URL shown in console

---

### Problem: "Invalid grant" or "Token has been expired or revoked"

**Symptoms**:
```
google.auth.exceptions.RefreshError: invalid_grant: Token has been expired or revoked
```

**Solution**:
```powershell
# Delete token and re-authenticate
Remove-Item data/token.json
python src/main.py
```

---

### Problem: "Access blocked: This app's request is invalid"

**Symptoms**:
OAuth consent screen shows error about invalid redirect URI

**Solution**:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. **APIs & Services** → **Credentials**
3. Click your OAuth 2.0 Client ID
4. Under "Authorized redirect URIs", add:
   - `http://localhost:8080/`
   - `http://localhost`
5. Save and try again after 5 minutes (propagation delay)

---

## Download Failures

### Problem: "Video unavailable" or "Private video"

**Symptoms**:
```
ERROR: Video unavailable
ERROR: This video is private
```

**Solution**:
- Verify video is **public** on source channel
- Check video wasn't deleted
- Wait a few minutes (processing delay)
- Verify you have permission to access the video

---

### Problem: yt-dlp download fails with "HTTP Error 403"

**Symptoms**:
```
ERROR: unable to download video data: HTTP Error 403: Forbidden
```

**Solutions**:

1. **Update yt-dlp**:
   ```powershell
   pip install --upgrade yt-dlp
   ```

2. **Clear cache**:
   ```powershell
   yt-dlp --rm-cache-dir
   ```

3. **Use different format**:
   Edit `config.json`:
   ```json
   {
     "download": {
       "video_quality": "best[height<=1080]",
       "format": "mp4"
     }
   }
   ```

---

### Problem: Download is very slow

**Symptoms**:
- Download speed < 1 MB/s
- ETA shows hours for small video

**Solutions**:

1. **Check internet speed**: [fast.com](https://fast.com)

2. **Change download location to SSD**:
   ```json
   {
     "download": {
       "directory": "C:\\FastStorage\\downloads"
     }
   }
   ```

3. **Limit concurrent downloads**:
   ```json
   {
     "performance": {
       "max_concurrent_downloads": 1
     }
   }
   ```

---

### Problem: "Disk space error" or downloads fail with space warning

**Symptoms**:
```
ERROR: Not enough free disk space
```

**Solution**:

1. **Free up space**: Delete old downloads from `downloads/` folder

2. **Enable auto-cleanup**:
   ```json
   {
     "download": {
       "auto_cleanup": true,
       "keep_files_days": 7,
       "max_storage_gb": 50
     }
   }
   ```

3. **Change download directory** to drive with more space

---

## Upload Errors

### Problem: Upload fails with "Quota exceeded"

**Symptoms**:
```
ERROR: The request cannot be completed because you have exceeded your quota
```

**Solution**:
- Check quota usage in [Google Cloud Console](https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas)
- Default quota: **10,000 units/day**
- Upload cost: **1,600 units per video**
- **Max uploads/day: ~6 videos**
- Wait until midnight PT (Pacific Time) for quota reset
- See [API_LIMITS.md](API_LIMITS.md) for quota optimization

---

### Problem: Upload fails with "File too large"

**Symptoms**:
```
ERROR: Request entity too large
```

**Solution**:

YouTube limits:
- **128 GB** maximum file size
- **12 hours** maximum duration

If your file exceeds:

1. **Re-encode to lower quality**:
   ```json
   {
     "download": {
       "video_quality": "best[height<=1080]"
     }
   }
   ```

2. **Compress video** (future feature with GPU acceleration)

---

### Problem: Upload succeeds but video is "Processing"

**Symptoms**:
- Upload completes
- Video shows as "Processing" for hours
- Thumbnail not visible

**Solution**:
- **Normal**: YouTube processing can take 1-4 hours for HD videos
- **4K videos**: Can take 8-12 hours
- Video is uploaded successfully, just wait for processing
- Check YouTube Studio for processing status

---

### Problem: "Upload failed: Invalid metadata"

**Symptoms**:
```
ERROR: Invalid request: title, description, or tags too long
```

**Solution**:

YouTube limits:
- **Title**: 100 characters
- **Description**: 5,000 characters
- **Tags**: 500 characters total

Check `config.json`:
```json
{
  "upload": {
    "title_prefix": "",     // Keep short!
    "title_suffix": "",     // Keep short!
    "description_append": ""  // Don't exceed limit
  }
}
```

---

## Performance Issues

### Problem: Application uses too much RAM (>150MB)

**Symptoms**:
- High memory usage
- System slowdown

**Solution**:

1. **Limit concurrent operations**:
   ```json
   {
     "performance": {
       "max_concurrent_downloads": 1,
       "max_concurrent_uploads": 1
     }
   }
   ```

2. **Enable auto-cleanup**:
   ```json
   {
     "download": {
       "auto_cleanup": true
     }
   }
   ```

3. **Restart application** if running for days

**Note**: Normal idle usage is ~26 MB (from performance profiling)

---

### Problem: High CPU usage (>40%) during idle

**Symptoms**:
- CPU fan running
- High CPU usage when not downloading/uploading

**Solution**:

1. **Increase check interval**:
   ```json
   {
     "monitoring": {
       "check_interval_minutes": 15  // From 10 to 15
     }
   }
   ```

2. **Disable active hours** if not needed:
   ```json
   {
     "active_hours": {
       "enabled": false
     }
   }
   ```

**Note**: Normal idle CPU is 0% (from performance profiling)

---

### Problem: Application slow to start

**Symptoms**:
- Takes >3 seconds to launch
- Splash screen frozen

**Solution**:

1. **Check antivirus**: Add application folder to exclusions

2. **Run security utility**:
   ```powershell
   python src/utils/file_security.py
   ```

3. **Clear old logs**:
   ```powershell
   Remove-Item logs/*.log -Force
   ```

**Note**: Normal startup time is 0.002s (from performance profiling)

---

## GUI Problems

### Problem: Main window won't open or shows blank

**Symptoms**:
- Application runs but no window appears
- Window is blank/white

**Solution**:

1. **Check if minimized to tray**: Look for icon in system tray

2. **Reset window position**:
   ```powershell
   # Delete settings file
   Remove-Item data/settings.json -ErrorAction SilentlyContinue
   python src/main.py
   ```

3. **Check display scaling**:
   - Right-click desktop → **Display settings**
   - Set scaling to **100%** temporarily
   - Restart application

---

### Problem: System tray icon missing

**Symptoms**:
- No tray icon appears
- Can't access menus

**Solution**:

1. **Enable system tray icons**:
   - Windows Settings → **Personalization** → **Taskbar**
   - **Select which icons appear on the taskbar**
   - Enable **YouTube Bot Video Extractor**

2. **Restart explorer.exe**:
   ```powershell
   Stop-Process -Name explorer -Force
   # Explorer will auto-restart
   ```

---

### Problem: High DPI / scaling issues

**Symptoms**:
- Blurry text
- UI elements cut off
- Buttons too small/large

**Solution**:

1. **Enable DPI awareness**:
   - Right-click `python.exe` (in venv)
   - **Properties** → **Compatibility**
   - ✅ **Override high DPI scaling behavior**
   - Application: **System (Enhanced)**

2. **Or set environment variable**:
   ```powershell
   $env:QT_AUTO_SCREEN_SCALE_FACTOR=1
   python src/main.py
   ```

---

## Network Issues

### Problem: "Connection timeout" or "Network unreachable"

**Symptoms**:
```
ERROR: Connection timed out
ERROR: Unable to reach YouTube servers
```

**Solution**:

1. **Check internet connection**: [fast.com](https://fast.com)

2. **Test YouTube API**:
   ```powershell
   ping www.googleapis.com
   ```

3. **Check firewall**:
   - Windows Defender Firewall
   - Allow **Python** through firewall

4. **Proxy settings** (if behind corporate proxy):
   ```powershell
   # Set proxy in environment
   $env:HTTP_PROXY="http://proxy.company.com:8080"
   $env:HTTPS_PROXY="http://proxy.company.com:8080"
   python src/main.py
   ```

---

### Problem: SSL certificate verification fails

**Symptoms**:
```
ERROR: SSL: CERTIFICATE_VERIFY_FAILED
```

**Solution**:

1. **Update certificates**:
   ```powershell
   pip install --upgrade certifi
   ```

2. **Check system time**: Ensure date/time is correct

3. **Corporate network**: Import company SSL certificate

---

## Database Errors

### Problem: "Database is locked" error

**Symptoms**:
```
sqlite3.OperationalError: database is locked
```

**Solution**:

1. **Close all instances** of the application

2. **Check for orphaned processes**:
   ```powershell
   Get-Process | Where-Object {$_.ProcessName -eq "python"}
   Stop-Process -Name python -Force
   ```

3. **Delete lock file** (if exists):
   ```powershell
   Remove-Item data/app.db-journal -ErrorAction SilentlyContinue
   ```

---

### Problem: "Database disk image is malformed"

**Symptoms**:
```
sqlite3.DatabaseError: database disk image is malformed
```

**Solution**:

1. **Backup database**:
   ```powershell
   Copy-Item data/app.db data/app.db.backup
   ```

2. **Attempt repair**:
   ```powershell
   sqlite3 data/app.db ".dump" | sqlite3 data/app_repaired.db
   Move-Item data/app_repaired.db data/app.db -Force
   ```

3. **Or start fresh**:
   ```powershell
   Remove-Item data/app.db
   python src/main.py  # Will recreate database
   ```

---

## Quota Limit Issues

### Problem: "Daily limit exceeded" too early in the day

**Symptoms**:
- Quota exhausted after only 2-3 videos
- Unexpected quota consumption

**Solution**:

1. **Check quota breakdown** in logs:
   ```
   INFO: Quota usage: 1650/10000 units (16.5%)
   ```

2. **Reduce API calls**:
   ```json
   {
     "monitoring": {
       "check_interval_minutes": 15,  // Increase from 10
       "max_videos_per_check": 3      // Reduce from 5
     }
   }
   ```

3. **Optimize monitoring**:
   - Only monitor during active upload hours
   - Use catch-up mechanism instead of frequent checks

See [**API_LIMITS.md**](API_LIMITS.md) for detailed quota management.

---

## General Troubleshooting

### Problem: Application crashes on startup

**Solution**:

1. **Check logs**:
   ```powershell
   Get-Content logs/app.log -Tail 50
   ```

2. **Run with debug output**:
   ```powershell
   python -u src/main.py 2>&1 | Tee-Object -FilePath debug.log
   ```

3. **Verify all dependencies**:
   ```powershell
   pip install -r requirements.txt --force-reinstall
   ```

4. **Check Python version**:
   ```powershell
   python --version  # Should be 3.11+
   ```

---

### Problem: Videos not being detected

**Symptoms**:
- Monitoring running but no new videos found
- Manual check shows "No new videos"

**Solution**:

1. **Verify channel ID** in `config.json`:
   ```json
   {
     "source_channel_id": "UC_x5XG1OV2P6uZZ5FSM9Ttw"  // Must be correct
   }
   ```

2. **Check lookback period**:
   ```json
   {
     "monitoring": {
       "lookback_hours": 24  // Increase if needed
     }
   }
   ```

3. **Verify OAuth permissions**:
   - Delete `data/token.json`
   - Re-authenticate with proper scopes

4. **Test API manually**:
   ```powershell
   python -c "from src.youtube.monitor import ChannelMonitor; m = ChannelMonitor('CHANNEL_ID'); print(m.check_for_new_videos())"
   ```

---

### Enabling Debug Mode

For detailed troubleshooting, enable debug logging:

**Edit `config.json`**:
```json
{
  "logging": {
    "level": "DEBUG",  // Change from INFO
    "console": true
  }
}
```

Or set environment variable:
```powershell
$env:LOG_LEVEL="DEBUG"
python src/main.py
```

Debug logs show:
- All API calls with parameters
- Database queries
- Event bus messages
- Queue operations
- Network requests

---

## Getting Help

### Before asking for help:

1. ✅ Check this troubleshooting guide
2. ✅ Review [SETUP.md](SETUP.md)
3. ✅ Check application logs in `logs/`
4. ✅ Try with a fresh configuration
5. ✅ Update to latest version

### Where to get help:

- **GitHub Issues**: https://github.com/itsmohitnarayan/youtubebotvideoextractor/issues
- **Include**:
  - Operating system & version
  - Python version
  - Error message (full stack trace)
  - Relevant logs (last 50 lines)
  - Steps to reproduce
  - What you've already tried

### Useful diagnostic commands:

```powershell
# System info
python --version
pip list | Select-String -Pattern "PyQt5|google|yt-dlp|APScheduler"

# Application info
python -c "from src import __version__; print(__version__)"

# Run tests
pytest tests/ -v

# Security audit
python scripts/security_audit.py

# Performance profiling
python scripts/performance_profiler.py
```

---

## Performance Benchmarks (For Reference)

From comprehensive performance profiling (Nov 10, 2025):

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Startup Time | <3s | 0.002s | ✅ 1500x better |
| Memory (Idle) | <150MB | 26MB | ✅ 5.7x better |
| CPU (Idle) | <5% | 0% | ✅ Optimal |
| Database Query | <10ms | 0.01ms | ✅ Sub-millisecond |
| Event Throughput | - | 299,424/sec | ✅ Excellent |
| Queue Processing | - | 4,777 tasks/sec | ✅ Excellent |

If your performance differs significantly, check the troubleshooting sections above.

---

## Emergency Reset

If nothing else works, perform a complete reset:

```powershell
# Backup important data
Copy-Item data/app.db data/app.db.backup
Copy-Item config.json config.json.backup

# Clean slate
Remove-Item data/* -Force -ErrorAction SilentlyContinue
Remove-Item logs/* -Force -ErrorAction SilentlyContinue
Remove-Item downloads/* -Recurse -Force -ErrorAction SilentlyContinue

# Recreate from example
Copy-Item config.example.json config.json

# Re-run setup
.\scripts\setup_env.ps1

# Start fresh
python src/main.py
```

---

**Last Updated**: November 10, 2025  
**Version**: 1.0.0
