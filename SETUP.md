# YouTube Bot Video Extractor - Setup Guide

**Complete installation guide for Windows 10/11**

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Python Installation](#python-installation)
3. [FFmpeg Installation](#ffmpeg-installation)
4. [Application Setup](#application-setup)
5. [YouTube API Credentials](#youtube-api-credentials)
6. [First Run Configuration](#first-run-configuration)
7. [Verification](#verification)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **Operating System:** Windows 10 (64-bit) or Windows 11
- **RAM:** Minimum 4 GB (8 GB recommended)
- **Storage:** 2 GB free space (more for video downloads)
- **Internet:** Stable connection (10 Mbps recommended)
- **Display:** 1024x768 minimum (1920x1080 recommended)

### Required Software
- **Python:** 3.8 or higher
- **FFmpeg:** Latest stable version
- **Git:** (Optional, for cloning repository)

---

## Python Installation

### Step 1: Download Python

1. Visit: [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)
2. Download **Python 3.11.x** or **Python 3.12.x** (recommended)
3. Choose the **Windows installer (64-bit)**

### Step 2: Install Python

1. Run the downloaded installer
2. **IMPORTANT:** Check ✅ **"Add Python to PATH"**
3. Click **"Install Now"**
4. Wait for installation to complete
5. Click **"Close"**

### Step 3: Verify Python Installation

Open **PowerShell** (or Command Prompt) and run:

```powershell
python --version
```

**Expected output:**
```
Python 3.11.x (or 3.12.x)
```

If you see an error, Python is not in your PATH. Reinstall with "Add to PATH" checked.

---

## FFmpeg Installation

### Step 1: Download FFmpeg

1. Visit: [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)
2. Download **ffmpeg-release-essentials.zip** (smaller, recommended)
   - Or: **ffmpeg-release-full.zip** (includes extra codecs)
3. Save to your Downloads folder

### Step 2: Extract FFmpeg

1. Extract the ZIP file to `C:\ffmpeg`
2. Your folder structure should be:
   ```
   C:\ffmpeg\
   ├── bin\
   │   ├── ffmpeg.exe
   │   ├── ffplay.exe
   │   └── ffprobe.exe
   ├── doc\
   └── presets\
   ```

### Step 3: Add FFmpeg to System PATH

1. Press **Win + R**, type `sysdm.cpl`, press Enter
2. Go to **Advanced** tab → click **Environment Variables**
3. Under **System variables**, find **Path** → click **Edit**
4. Click **New** → add `C:\ffmpeg\bin`
5. Click **OK** on all dialogs
6. **Restart PowerShell** (important!)

### Step 4: Verify FFmpeg Installation

```powershell
ffmpeg -version
```

**Expected output:**
```
ffmpeg version 6.x.x ...
```

---

## Application Setup

### Step 1: Download the Application

**Option A: Using Git (Recommended)**
```powershell
cd D:\2025
git clone https://github.com/itsmohitnarayan/youtubebotvideoextractor.git
cd youtubebotvideoextractor
```

**Option B: Download ZIP**
1. Download from GitHub: [Repository Link]
2. Extract to `D:\2025\youtubebotvideoextractor`
3. Open PowerShell in that folder

### Step 2: Create Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

You should see `(venv)` prefix in your terminal.

### Step 3: Install Python Dependencies

```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

This will install:
- `httpx` - HTTP client
- `requests` - HTTP library
- `google-api-python-client` - YouTube API
- `google-auth-oauthlib` - OAuth authentication
- `yt-dlp` - Video downloader
- `PyQt5` - GUI framework
- `APScheduler` - Task scheduling
- `Pillow` - Image processing
- `tqdm` - Progress bars
- `python-dotenv` - Environment variables

**Installation time:** 2-5 minutes depending on internet speed.

### Step 4: Verify Installation

```powershell
# Run the test suite to verify setup
pytest tests/ -v
```

**Expected:** All tests should pass (211 tests).

---

## YouTube API Credentials

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Create Project"**
3. Enter project name: `YouTube Bot Video Extractor`
4. Click **"Create"**

### Step 2: Enable YouTube Data API v3

1. In the Cloud Console, go to **APIs & Services → Library**
2. Search for **"YouTube Data API v3"**
3. Click on it → click **"Enable"**

### Step 3: Create OAuth 2.0 Credentials

1. Go to **APIs & Services → Credentials**
2. Click **"Create Credentials" → "OAuth client ID"**
3. If prompted, configure OAuth consent screen:
   - User Type: **External**
   - App name: `YouTube Bot Video Extractor`
   - Support email: Your email
   - Developer contact: Your email
   - Click **"Save and Continue"**
   - Scopes: Click **"Add or Remove Scopes"**
     - Add: `https://www.googleapis.com/auth/youtube.upload`
     - Add: `https://www.googleapis.com/auth/youtube.readonly`
   - Click **"Save and Continue"**
   - Test users: Add your Gmail address
   - Click **"Save and Continue"**
4. Back to Create OAuth Client ID:
   - Application type: **Desktop app**
   - Name: `YouTube Bot Desktop Client`
   - Click **"Create"**
5. Download the JSON file (click download icon ⬇️)
6. Rename it to `client_secrets.json`
7. Move it to: `D:\2025\youtubebotvideoextractor\data\`

### File Location:
```
D:\2025\youtubebotvideoextractor\
└── data\
    └── client_secrets.json  ← Your credentials file
```

⚠️ **SECURITY NOTE:** Never commit `client_secrets.json` to Git!

---

## First Run Configuration

### Step 1: Create Configuration File

The application will create `config.json` on first run, but you can create it manually:

```powershell
cd D:\2025\youtubebotvideoextractor
```

Create `data/config.json` with the following content:

```json
{
  "monitored_folders": [],
  "download_folder": "downloads",
  "max_concurrent_downloads": 3,
  "retry_attempts": 3,
  "retry_delay": 60,
  "upload": {
    "enabled": true,
    "title_template": "{original_title}",
    "description_template": "",
    "tags": [],
    "privacy_status": "private",
    "category_id": "22"
  },
  "active_hours": {
    "enabled": false,
    "days": [1, 2, 3, 4, 5],
    "start_time": "09:00",
    "end_time": "17:00"
  },
  "notifications": {
    "enabled": true,
    "on_success": true,
    "on_failure": true
  },
  "auto_start": false,
  "minimize_to_tray": true
}
```

### Step 2: Run the Application

```powershell
# Make sure virtual environment is activated
venv\Scripts\activate

# Run the application
python src/main.py
```

**First Launch:**
- ✅ Configuration file created
- ✅ Database initialized (`data/videos.db`)
- ✅ Logs folder created
- ✅ Downloads folder created
- ✅ System tray icon appears
- ✅ Main window opens

### Step 3: Authenticate with YouTube

1. Open the application
2. Go to **Settings → YouTube**
3. Click **"Authenticate with YouTube"**
4. Your browser will open → Log in with your Google account
5. Grant permissions (upload videos, read channel info)
6. Close browser tab
7. Return to application
8. You should see **"Authenticated as [your email]"**

**Authentication token saved:** `data/token.pickle`

---

## Verification

### Verify Complete Setup

Run this verification script:

```powershell
# Activate virtual environment
venv\Scripts\activate

# Run automated UAT verification
python scripts/run_uat.py
```

**Expected output:**
```
✅ ALL TESTS PASSED!
Recommendation: ✅ Ready for manual UAT testing
```

### Manual Verification Checklist

- [ ] Python 3.8+ installed and in PATH
- [ ] FFmpeg installed and in PATH
- [ ] Virtual environment created
- [ ] All dependencies installed (211 tests pass)
- [ ] YouTube API credentials configured
- [ ] Application launches without errors
- [ ] System tray icon visible
- [ ] OAuth authentication successful
- [ ] Configuration saved and loaded

---

## Troubleshooting

### Python Not Found

**Error:** `'python' is not recognized...`

**Solution:**
1. Reinstall Python with **"Add to PATH"** checked
2. Or manually add to PATH:
   - `C:\Users\[YourName]\AppData\Local\Programs\Python\Python311`
   - `C:\Users\[YourName]\AppData\Local\Programs\Python\Python311\Scripts`

### FFmpeg Not Found

**Error:** `'ffmpeg' is not recognized...`

**Solution:**
1. Verify FFmpeg is at `C:\ffmpeg\bin\ffmpeg.exe`
2. Check PATH environment variable includes `C:\ffmpeg\bin`
3. Restart PowerShell after adding to PATH

### Dependency Installation Fails

**Error:** `error: Microsoft Visual C++ 14.0 or greater is required`

**Solution:**
Install **Microsoft C++ Build Tools:**
1. Download: [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Install **Desktop development with C++**
3. Retry: `pip install -r requirements.txt`

### OAuth Authentication Fails

**Error:** `Redirect URI mismatch` or `Access blocked`

**Solution:**
1. Check `client_secrets.json` is correct file from Google Cloud
2. Ensure OAuth consent screen is configured
3. Add yourself as a test user
4. Delete `data/token.pickle` and re-authenticate

### Database Initialization Fails

**Error:** `database is locked` or `unable to open database file`

**Solution:**
1. Close all instances of the application
2. Delete `data/videos.db`
3. Restart application (database will be recreated)

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'PyQt5'`

**Solution:**
```powershell
# Make sure virtual environment is activated
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## Next Steps

After successful setup:

1. **Configure Monitored Folders:** Settings → Monitoring → Add folders
2. **Customize Upload Settings:** Settings → Upload → Template configuration
3. **Set Active Hours (Optional):** Settings → Schedule → Active hours
4. **Test with Sample Video:** Copy a small video to monitored folder
5. **Read User Guide:** `docs/USER_GUIDE.md` for detailed feature documentation

---

## Getting Help

If you encounter issues not covered here:

1. **Check logs:** `logs/errors.log`
2. **Read troubleshooting guide:** `docs/TROUBLESHOOTING.md`
3. **Check API quota:** `docs/API_LIMITS.md`
4. **File an issue:** [GitHub Issues](https://github.com/itsmohitnarayan/youtubebotvideoextractor/issues)

---

## Estimated Setup Time

- **Python installation:** 5 minutes
- **FFmpeg installation:** 5 minutes
- **Application setup:** 10 minutes
- **YouTube API setup:** 15 minutes
- **Total:** ~35 minutes (first-time users)

---

**Setup complete! 🎉**

You're now ready to use the YouTube Bot Video Extractor. Proceed to `docs/USER_GUIDE.md` for usage instructions.
