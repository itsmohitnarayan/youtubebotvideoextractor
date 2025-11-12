# Implementation Plan
## YouTube Video Replicator Bot

**Project:** YouTubeBotVideoExtractor  
**Start Date:** November 8, 2025  
**Estimated Duration:** 4-6 weeks  
**Development Approach:** Agile, Phase-based

---

## Project Phases Overview

```
Phase 0: Setup & Foundation          [Week 1]      ████░░░░░░  40%
Phase 1: Core Backend Logic          [Week 2]      ██████░░░░  60%
Phase 2: YouTube Integration         [Week 2-3]    ████████░░  80%
Phase 3: GUI Development             [Week 3-4]    ██████████ 100%
Phase 4: System Integration          [Week 4-5]    ██████████ 100%
Phase 5: Testing & Optimization      [Week 5-6]    ██████████ 100%
Phase 6: Packaging & Deployment      [Week 6]      ██████████ 100%
```

---

## Phase 0: Setup & Foundation
**Duration:** 3-4 days  
**Status:** ✅ **COMPLETE** (November 10, 2025)  
**Priority:** Critical

### Objectives
- Set up development environment
- Initialize project structure
- Configure dependencies
- Create base architecture

### Tasks

#### 0.1 Environment Setup
- [ ] Install Python 3.11+ (verify in PATH)
- [ ] Install Git and configure
- [ ] Set up virtual environment (`venv`)
- [ ] Install VS Code with Python extensions
- [ ] Configure linter (flake8/pylint)
- [ ] Configure formatter (Black)

#### 0.2 Project Structure Creation
```
youtubebotvideoextractor/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Configuration manager
│   │   ├── database.py            # SQLite database handler
│   │   ├── logger.py              # Logging setup
│   │   └── scheduler.py           # APScheduler wrapper
│   ├── youtube/
│   │   ├── __init__.py
│   │   ├── api_client.py          # YouTube API wrapper
│   │   ├── downloader.py          # yt-dlp integration
│   │   ├── uploader.py            # Video upload logic
│   │   └── monitor.py             # Channel monitoring
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── main_window.py         # Main dashboard
│   │   ├── system_tray.py         # System tray icon
│   │   ├── settings_dialog.py     # Settings window
│   │   └── widgets/               # Custom widgets
│   │       ├── __init__.py
│   │       ├── progress_widget.py
│   │       └── log_viewer.py
│   └── utils/
│       ├── __init__.py
│       ├── validators.py          # Input validation
│       ├── helpers.py             # Utility functions
│       └── constants.py           # App constants
├── resources/
│   ├── icons/                     # Tray icons, app icon
│   ├── ui/                        # Qt Designer .ui files
│   └── styles/                    # QSS stylesheets
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_downloader.py
│   ├── test_uploader.py
│   └── test_monitor.py
├── docs/
│   ├── SETUP.md
│   ├── USER_GUIDE.md
│   ├── TROUBLESHOOTING.md
│   └── API_LIMITS.md
├── scripts/
│   ├── setup_env.ps1              # Setup script for Windows
│   └── build.ps1                  # Build script
├── .env.example                   # Environment variables template
├── .gitignore
├── requirements.txt               # Python dependencies
├── requirements-dev.txt           # Development dependencies
├── config.example.json            # Config template
├── README.md
├── PRD.md                         # ✓ Created
├── PLAN.md                        # ✓ Created
└── LICENSE
```

#### 0.3 Dependency Installation
Create `requirements.txt`:
```txt
# Core
python-dotenv==1.0.0
httpx==0.25.0
requests==2.31.0

# YouTube
google-api-python-client==2.108.0
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.1.1
yt-dlp==2023.11.16

# GUI
PyQt5==5.15.10
PyQt5-Qt5==5.15.2
PyQt5-sip==12.13.0

# Scheduling
APScheduler==3.10.4

# Database
sqlite3 (built-in)

# Utilities
Pillow==10.1.0
tqdm==4.66.1
```

Create `requirements-dev.txt`:
```txt
# Testing
pytest==7.4.3
pytest-cov==4.1.0
pytest-mock==3.12.0

# Linting
flake8==6.1.0
pylint==3.0.2
black==23.11.0

# Type checking
mypy==1.7.0

# Packaging
PyInstaller==6.2.0
```

#### 0.4 Base Configuration Files

**`.env.example`:**
```env
# YouTube API Credentials
YOUTUBE_CLIENT_SECRETS_FILE=client_secrets.json
YOUTUBE_TOKEN_FILE=oauth_token.json

# Application Settings
APP_NAME=YouTubeBotVideoExtractor
LOG_LEVEL=INFO
DATABASE_PATH=data/app.db
DOWNLOAD_DIR=downloads

# Active Hours (24-hour format)
ACTIVE_START=10:00
ACTIVE_END=22:00

# Monitoring
CHECK_INTERVAL_MINUTES=10
```

**`config.example.json`:**
```json
{
  "version": "1.0.0",
  "target_channel": {
    "channel_id": "",
    "channel_url": ""
  },
  "active_hours": {
    "start": "10:00",
    "end": "22:00",
    "timezone": "UTC"
  },
  "monitoring": {
    "check_interval_minutes": 10,
    "catch_up_on_start": true,
    "max_videos_per_check": 5
  },
  "download": {
    "directory": "downloads",
    "video_quality": "best",
    "format": "mp4",
    "max_filesize_mb": 2048
  },
  "upload": {
    "title_prefix": "",
    "title_suffix": "",
    "description_append": "",
    "privacy_status": "public",
    "category_id": "22",
    "tags": []
  },
  "notifications": {
    "enabled": true,
    "on_download": true,
    "on_upload": true,
    "on_error": true
  }
}
```

#### 0.5 Git Repository Setup
```bash
git init
git add .
git commit -m "Initial project structure"
git branch -M main
git remote add origin https://github.com/itsmohitnarayan/youtubebotvideoextractor.git
git push -u origin main
```

### Deliverables
- ✅ Development environment ready
- ✅ Project structure created
- ✅ Dependencies documented and installed
- ✅ Git repository initialized
- ✅ All core components tested and working

---

## Phase 1: Core Backend Logic
**Duration:** 5-6 days  
**Status:** 🔴 Not Started  
**Priority:** Critical  
**Dependencies:** Phase 0

### Objectives
- Implement configuration management
- Set up database layer
- Create logging system
- Build scheduler framework

### Tasks

#### 1.1 Configuration Manager (`src/core/config.py`)
```python
Features:
- Load config from JSON file
- Validate configuration schema
- Provide default values
- Environment variable override
- Save configuration changes
- Encrypt sensitive data
```

**Key Methods:**
- `load_config()` - Load from file
- `save_config()` - Persist changes
- `validate()` - Schema validation
- `get(key, default)` - Get config value
- `set(key, value)` - Update config

#### 1.2 Database Manager (`src/core/database.py`)
```python
Features:
- SQLite connection management
- Create tables on first run
- CRUD operations for videos
- Query builders
- Migration support
```

**Tables:**
1. `videos` - Processed video tracking
2. `logs` - Application logs
3. `stats` - Daily statistics
4. `settings` - Runtime settings

**Key Methods:**
- `init_db()` - Initialize database
- `add_video()` - Insert video record
- `get_processed_videos()` - Query processed
- `update_video_status()` - Update status
- `get_stats()` - Retrieve statistics

#### 1.3 Logger (`src/core/logger.py`)
```python
Features:
- Multi-level logging (DEBUG, INFO, WARNING, ERROR)
- File rotation (10MB max)
- Console output (dev mode)
- Database logging (errors only)
- Structured log format
```

**Log Format:**
```
[2025-11-08 10:30:45] [INFO] [Monitor] Checking for new videos...
[2025-11-08 10:31:12] [INFO] [Downloader] Downloaded: Video Title (12.3MB)
[2025-11-08 10:35:30] [ERROR] [Uploader] Upload failed: API quota exceeded
```

#### 1.4 Scheduler (`src/core/scheduler.py`)
```python
Features:
- APScheduler wrapper
- Cron-like scheduling
- Active hours enforcement
- Job pause/resume
- Job status tracking
```

**Jobs:**
1. `check_for_videos` - Runs every N minutes
2. `cleanup_old_files` - Daily at midnight
3. `rotate_logs` - Daily
4. `update_stats` - Hourly

#### 1.5 Utilities (`src/utils/`)

**`validators.py`:**
- `validate_youtube_url()` - Check URL format
- `validate_channel_id()` - Verify channel ID
- `validate_time_format()` - Check HH:MM format
- `validate_file_path()` - Path validation

**`helpers.py`:**
- `format_file_size()` - Human-readable sizes
- `format_duration()` - Convert seconds to HH:MM:SS
- `sanitize_filename()` - Remove invalid chars
- `is_within_active_hours()` - Time check

**`constants.py`:**
```python
APP_NAME = "YouTube Video Replicator"
APP_VERSION = "1.0.0"
DATABASE_VERSION = 1
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds
API_TIMEOUT = 30  # seconds
```

### Testing Tasks
- [ ] Unit tests for config manager
- [ ] Database CRUD tests
- [ ] Logger output verification
- [ ] Scheduler timing tests
- [ ] Validator edge cases

### Deliverables
- ✅ Configuration system working
- ✅ Database layer functional
- ✅ Logging system operational
- ✅ Scheduler framework ready
- ✅ 80%+ test coverage

---

## Phase 2: YouTube Integration
**Duration:** 7-8 days  
**Status:** 🔴 Not Started  
**Priority:** Critical  
**Dependencies:** Phase 1

### Objectives
- Integrate YouTube Data API
- Implement video downloader
- Build upload pipeline
- Create channel monitor

### Tasks

#### 2.1 YouTube API Client (`src/youtube/api_client.py`)
```python
Features:
- OAuth 2.0 authentication
- Token management (refresh)
- API quota tracking
- Rate limiting
- Error handling
```

**Key Methods:**
- `authenticate()` - OAuth flow
- `get_channel_info(channel_id)` - Channel details
- `search_videos(channel_id, published_after)` - Find new videos
- `get_video_details(video_id)` - Full metadata
- `upload_video(file_path, metadata)` - Upload
- `set_thumbnail(video_id, thumbnail_path)` - Set thumb

**API Quota Management:**
```python
Daily quota: 10,000 units
Track usage:
- Log each API call cost
- Warn at 80% usage
- Pause at 95% usage
- Reset counter at midnight
```

#### 2.2 Video Downloader (`src/youtube/downloader.py`)
```python
Features:
- yt-dlp integration
- Progress tracking
- Quality selection
- Metadata extraction
- Thumbnail download
- Error recovery
```

**Key Methods:**
- `download_video(video_id, output_dir)` - Main download
- `extract_metadata(video_id)` - Get title, desc, tags
- `download_thumbnail(video_id)` - Get custom thumbnail
- `get_video_info(video_id)` - Quick metadata fetch

**Download Options:**
```python
ydl_opts = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'outtmpl': '%(id)s.%(ext)s',
    'writesubtitles': False,
    'writethumbnail': True,
    'quiet': False,
    'no_warnings': False,
    'progress_hooks': [progress_callback],
}
```

#### 2.3 Video Uploader (`src/youtube/uploader.py`)
```python
Features:
- Resumable uploads
- Progress tracking
- Metadata application
- Thumbnail setting
- Privacy configuration
- Retry logic
```

**Key Methods:**
- `upload(video_path, metadata)` - Upload video
- `apply_metadata(video_id, metadata)` - Set title/desc/tags
- `set_thumbnail(video_id, thumb_path)` - Upload thumbnail
- `set_privacy(video_id, status)` - Set visibility

**Upload Flow:**
```python
1. Prepare metadata (title, description, tags)
2. Start resumable upload
3. Monitor progress (0-100%)
4. Upload thumbnail
5. Set privacy status
6. Verify upload success
7. Return video ID
```

#### 2.4 Channel Monitor (`src/youtube/monitor.py`)
```python
Features:
- Periodic channel checks
- New video detection
- Duplicate prevention
- Catch-up mechanism
- Event notifications
```

**Key Methods:**
- `start_monitoring()` - Begin monitoring loop
- `check_for_new_videos()` - Single check cycle
- `get_videos_since(datetime)` - Catch-up query
- `is_video_processed(video_id)` - Duplicate check
- `on_new_video(video)` - Event handler

**Monitoring Logic:**
```python
1. Query YouTube API for recent uploads
2. Compare with processed video IDs in database
3. For each new video:
   a. Trigger download
   b. Queue for upload
   c. Mark as processing
4. Sleep until next check interval
```

### Testing Tasks
- [ ] Test OAuth flow (mock + real)
- [ ] Download various video formats
- [ ] Upload test video to test channel
- [ ] Monitor test channel for 24h
- [ ] Test quota limit handling
- [ ] Test network failure recovery

### Deliverables
- ✅ YouTube API integrated
- ✅ Video download working
- ✅ Upload pipeline functional
- ✅ Monitoring system active
- ✅ API quota management

---

## Phase 3: GUI Development
**Duration:** 7-8 days  
**Status:** 🔴 Not Started  
**Priority:** High  
**Dependencies:** Phase 1

### Objectives
- Build system tray application
- Create main dashboard
- Implement settings dialog
- Design notification system

### Tasks

#### 3.1 System Tray Icon (`src/gui/system_tray.py`)
```python
Features:
- Persistent tray icon
- Context menu
- Status icon changes
- Balloon notifications
- Click actions
```

**Context Menu:**
```
┌─────────────────────────┐
│ YouTube Bot             │
├─────────────────────────┤
│ ● Monitoring Active     │
│ Last Check: 2 min ago   │
├─────────────────────────┤
│ 🪟 Show Dashboard       │
│ ▶️ Pause Monitoring     │
│ 🔄 Check Now           │
│ ⚙️ Settings            │
│ 📋 View Logs           │
├─────────────────────────┤
│ ❌ Exit                 │
└─────────────────────────┘
```

**Icon States:**
- 🟢 Idle/Monitoring
- 🔵 Downloading
- 🟡 Uploading
- 🔴 Error
- ⚫ Paused

#### 3.2 Main Dashboard (`src/gui/main_window.py`)
```python
Components:
- Status panel (monitoring state)
- Statistics panel (today's activity)
- Progress bar (current operation)
- Recent videos list
- Control buttons
```

**Layout (PyQt5):**
```python
QMainWindow
├── QVBoxLayout
│   ├── Status GroupBox
│   │   ├── Status Label
│   │   ├── Channel Label
│   │   ├── Last Check Label
│   │   └── Next Check Label
│   ├── Statistics GroupBox
│   │   ├── Detected Count
│   │   ├── Downloaded Count
│   │   ├── Uploaded Count
│   │   └── Errors Count
│   ├── Progress GroupBox
│   │   ├── Current Operation Label
│   │   ├── Progress Bar
│   │   └── ETA Label
│   ├── Recent Videos List
│   │   └── QListWidget (scrollable)
│   └── Control Panel
│       ├── Pause Button
│       ├── Check Now Button
│       ├── Settings Button
│       └── View Logs Button
```

#### 3.3 Settings Dialog (`src/gui/settings_dialog.py`)
```python
Tabs:
1. General
   - Target channel URL
   - Active hours (start/end)
   - Check interval

2. Download
   - Download directory (file picker)
   - Video quality dropdown
   - Max file size

3. Upload
   - Title prefix/suffix
   - Description append
   - Privacy status dropdown
   - Default category

4. YouTube API
   - Client secrets file path
   - OAuth re-authenticate button
   - Quota usage display

5. Notifications
   - Enable/disable checkboxes
   - Notification types
```

**Validation:**
- Real-time input validation
- Show errors inline
- Disable "Save" if invalid
- Confirm on cancel if dirty

#### 3.4 Custom Widgets

**Progress Widget (`src/gui/widgets/progress_widget.py`):**
- Shows current operation (download/upload)
- Progress bar with percentage
- Speed indicator (MB/s)
- ETA countdown
- Cancel button

**Log Viewer (`src/gui/widgets/log_viewer.py`):**
- Read-only text area
- Color-coded log levels
- Auto-scroll to bottom
- Filter by level
- Export to file button
- Clear logs button

#### 3.5 Styling (QSS)
Create `resources/styles/main.qss`:
```css
/* Modern dark theme */
QMainWindow {
    background-color: #2b2b2b;
    color: #e0e0e0;
}

QPushButton {
    background-color: #3c3c3c;
    border: 1px solid #555;
    padding: 8px 16px;
    border-radius: 4px;
}

QPushButton:hover {
    background-color: #4a4a4a;
}

/* More styling... */
```

### Testing Tasks
- [ ] Test tray icon on Windows 10/11
- [ ] Verify all GUI interactions
- [ ] Test settings persistence
- [ ] Check notification display
- [ ] UI responsiveness under load

### Deliverables
- ✅ System tray app functional
- ✅ Dashboard displays correctly
- ✅ Settings dialog working
- ✅ Notifications operational
- ✅ Professional UI/UX

---

## Phase 4: System Integration
**Duration:** 5-6 days  
**Status:** 🔴 Not Started  
**Priority:** Critical  
**Dependencies:** Phase 2, Phase 3

### Objectives
- Connect GUI to backend
- Implement event system
- Add auto-start functionality
- Build complete workflow

### Tasks

#### 4.1 Event Bus (`src/core/events.py`)
```python
Features:
- Pub/sub pattern
- Event types:
  - MonitoringStarted
  - MonitoringStopped
  - VideoDetected
  - DownloadStarted
  - DownloadProgress
  - DownloadCompleted
  - UploadStarted
  - UploadProgress
  - UploadCompleted
  - ErrorOccurred
```

**Usage:**
```python
# Publisher (backend)
events.emit('video_detected', video_id='abc123', title='...')

# Subscriber (GUI)
events.on('video_detected', lambda data: update_ui(data))
```

#### 4.2 Application Controller (`src/main.py`)
```python
Responsibilities:
- Initialize all components
- Start GUI thread
- Start monitoring thread
- Handle graceful shutdown
- Manage application lifecycle
```

**Main Flow:**
```python
1. Load configuration
2. Initialize database
3. Setup logger
4. Create GUI (system tray)
5. Initialize YouTube client
6. Start scheduler
7. Begin monitoring (if within active hours)
8. Enter Qt event loop
9. On exit: cleanup resources
```

#### 4.3 Thread Management
```python
Threads:
1. Main Thread (Qt GUI)
2. Monitoring Thread (background checks)
3. Download Thread (per video)
4. Upload Thread (per video)

Synchronization:
- QThread for Qt integration
- Queue for video processing
- Locks for database access
- Signals/slots for GUI updates
```

#### 4.4 Auto-Start Setup

**Windows Registry Method:**
```python
import winreg

def add_to_startup():
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0, winreg.KEY_SET_VALUE
    )
    winreg.SetValueEx(
        key, "YouTubeBotVideoExtractor", 0,
        winreg.REG_SZ, sys.executable
    )
    winreg.CloseKey(key)
```

**Startup Folder Method:**
```python
import os
import shutil

startup_folder = os.path.join(
    os.environ['APPDATA'],
    r'Microsoft\Windows\Start Menu\Programs\Startup'
)
shortcut_path = os.path.join(startup_folder, 'YouTubeBot.lnk')
create_shortcut(sys.executable, shortcut_path)
```

#### 4.5 Complete Workflow Integration

**Video Processing Pipeline:**
```
New Video Detected
       ↓
Add to Queue
       ↓
Start Download Thread
       ↓
Download Video + Thumbnail
       ↓
Update Database (downloaded)
       ↓
Start Upload Thread
       ↓
Upload Video
       ↓
Set Thumbnail
       ↓
Update Database (completed)
       ↓
Notify User
       ↓
Cleanup Local Files (optional)
```

### Testing Tasks
- [ ] Test end-to-end workflow
- [ ] Verify auto-start on reboot
- [ ] Test concurrent video processing
- [ ] Stress test with multiple videos
- [ ] Verify thread safety
- [ ] Test graceful shutdown

### Deliverables
- ✅ Full system integration
- ✅ Auto-start functional
- ✅ Event system working
- ✅ Complete video pipeline
- ✅ Stable multi-threading

---

## Phase 5: Testing & Optimization
**Duration:** 7-8 days  
**Status:** 🔴 Not Started  
**Priority:** High  
**Dependencies:** Phase 4

### Objectives
- Comprehensive testing
- Performance optimization
- Bug fixes
- Documentation

### Tasks

#### 5.1 Unit Testing
```python
Test Coverage Goals:
- core/: 90%+
- youtube/: 85%+
- utils/: 95%+
- gui/: 70%+ (GUI harder to test)
```

**Test Suites:**
- `test_config.py` - Configuration loading/saving
- `test_database.py` - CRUD operations
- `test_downloader.py` - Download logic (mocked)
- `test_uploader.py` - Upload logic (mocked)
- `test_monitor.py` - Monitoring logic
- `test_validators.py` - Input validation

#### 5.2 Integration Testing
```python
Scenarios:
1. Fresh install → Setup → First video
2. Overnight catch-up
3. Multiple videos in quick succession
4. API quota limit hit
5. Network failure during download
6. Upload failure and retry
7. Configuration change while running
8. Graceful shutdown mid-upload
```

#### 5.3 Performance Optimization

**Targets:**
- Startup time: <3 seconds
- Memory usage: <150MB idle
- CPU usage: <5% idle, <40% downloading
- API response time: <2 seconds
- Download speed: Maximum available bandwidth
- Upload speed: Maximum available bandwidth

**Optimizations:**
- Lazy load modules
- Cache API responses (5 min TTL)
- Batch database writes
- Optimize GUI redraws
- Compress logs aggressively

#### 5.4 Security Audit
- [ ] Encrypt OAuth tokens at rest
- [ ] Secure API key storage
- [ ] Validate all user inputs
- [ ] Sanitize file paths
- [ ] Check for SQL injection (use parameterized queries)
- [ ] HTTPS only for API calls
- [ ] No hardcoded secrets

#### 5.5 User Acceptance Testing (UAT)
- [ ] Test on Windows 10 (version 21H2+)
- [ ] Test on Windows 11
- [ ] Test with different screen resolutions
- [ ] Test with high DPI displays
- [ ] Test with slow internet (<1 Mbps)
- [ ] Test with fast internet (>100 Mbps)
- [ ] 24-hour soak test

#### 5.6 Documentation
- [ ] Code comments (docstrings)
- [ ] README.md (quick start)
- [ ] SETUP.md (detailed setup guide)
- [ ] USER_GUIDE.md (how to use)
- [ ] TROUBLESHOOTING.md (common issues)
- [ ] API_LIMITS.md (quota management)
- [ ] CONTRIBUTING.md (for open source)

### Deliverables
- ✅ 80%+ test coverage
- ✅ All integration tests pass
- ✅ Performance targets met
- ✅ Security audit complete
- ✅ Documentation complete

---

## Phase 6: Packaging & Deployment
**Duration:** 4-5 days  
**Status:** 🔴 Not Started  
**Priority:** High  
**Dependencies:** Phase 5

### Objectives
- Package as standalone .exe
- Create installer
- Set up auto-update
- Prepare distribution

### Tasks

#### 6.1 PyInstaller Configuration

**`build.spec`:**
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources', 'resources'),
        ('config.example.json', '.'),
        ('.env.example', '.'),
    ],
    hiddenimports=[
        'google.auth',
        'googleapiclient',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='YouTubeBotVideoExtractor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icons/app_icon.ico',
)
```

**Build Script (`scripts/build.ps1`):**
```powershell
# Clean previous builds
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue

# Activate venv
.\venv\Scripts\Activate.ps1

# Run PyInstaller
pyinstaller build.spec

# Copy additional files
Copy-Item README.md dist\
Copy-Item LICENSE dist\
Copy-Item docs\* dist\docs\ -Recurse

Write-Host "Build complete! Check dist/ folder"
```

#### 6.2 Installer Creation (Inno Setup)

**`installer.iss`:**
```ini
[Setup]
AppName=YouTube Bot Video Extractor
AppVersion=1.0.0
DefaultDirName={autopf}\YouTubeBotVideoExtractor
DefaultGroupName=YouTube Bot
OutputBaseFilename=YouTubeBotVideoExtractor_Setup
Compression=lzma2
SolidCompression=yes
OutputDir=installer

[Files]
Source: "dist\YouTubeBotVideoExtractor.exe"; DestDir: "{app}"
Source: "dist\resources\*"; DestDir: "{app}\resources"; Flags: recursesubdirs
Source: "dist\docs\*"; DestDir: "{app}\docs"; Flags: recursesubdirs
Source: "dist\README.md"; DestDir: "{app}"
Source: "dist\LICENSE"; DestDir: "{app}"

[Icons]
Name: "{group}\YouTube Bot Video Extractor"; Filename: "{app}\YouTubeBotVideoExtractor.exe"
Name: "{group}\Uninstall"; Filename: "{uninstallexe}"
Name: "{autodesktop}\YouTube Bot"; Filename: "{app}\YouTubeBotVideoExtractor.exe"

[Run]
Filename: "{app}\YouTubeBotVideoExtractor.exe"; Description: "Launch YouTube Bot"; Flags: nowait postinstall skipifsilent

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "YouTubeBotVideoExtractor"; ValueData: """{app}\YouTubeBotVideoExtractor.exe"""; Flags: uninsdeletevalue
```

#### 6.3 Auto-Update System

**GitHub Releases Integration:**
```python
import requests

def check_for_updates():
    current_version = "1.0.0"
    api_url = "https://api.github.com/repos/itsmohitnarayan/youtubebotvideoextractor/releases/latest"
    
    response = requests.get(api_url)
    latest = response.json()
    latest_version = latest['tag_name'].lstrip('v')
    
    if latest_version > current_version:
        return {
            'available': True,
            'version': latest_version,
            'download_url': latest['assets'][0]['browser_download_url'],
            'release_notes': latest['body']
        }
    return {'available': False}
```

**Update Prompt:**
```python
if update_available:
    reply = QMessageBox.question(
        self, 'Update Available',
        f'Version {update["version"]} is available. Download now?',
        QMessageBox.Yes | QMessageBox.No
    )
    if reply == QMessageBox.Yes:
        webbrowser.open(update['download_url'])
```

#### 6.4 Distribution Checklist
- [ ] Test installer on clean Windows 10 VM
- [ ] Test installer on Windows 11 VM
- [ ] Verify auto-start works
- [ ] Test uninstaller
- [ ] Check file associations
- [ ] Verify digital signature (optional)
- [ ] Create release notes
- [ ] Tag release in Git
- [ ] Upload to GitHub Releases
- [ ] Create download page

#### 6.5 Release Assets
```
Release v1.0.0
├── YouTubeBotVideoExtractor_Setup.exe (Installer)
├── YouTubeBotVideoExtractor_Portable.zip (No install)
├── README.md
├── CHANGELOG.md
├── SETUP_GUIDE.pdf
└── checksums.txt (SHA256)
```

### Deliverables
- ✅ Standalone .exe built
- ✅ Installer created
- ✅ Auto-update functional
- ✅ Release published
- ✅ Distribution ready

---

## Post-Launch Tasks

### Week 1 Post-Launch
- [ ] Monitor error reports
- [ ] Gather user feedback
- [ ] Fix critical bugs
- [ ] Update documentation

### Week 2-4 Post-Launch
- [ ] Implement feature requests
- [ ] Performance improvements
- [ ] Release patch updates
- [ ] Plan v1.1.0 features

---

## Development Guidelines

### Code Standards
- **Style**: Follow PEP 8
- **Formatter**: Black (line length 100)
- **Linter**: Flake8 + Pylint
- **Type Hints**: Required for public methods
- **Docstrings**: Google style

### Git Workflow
```
main (protected)
  ↑
develop
  ↑
feature/phase-1-core
feature/phase-2-youtube
feature/phase-3-gui
```

**Commit Message Format:**
```
[Phase-X] Brief description

- Detailed change 1
- Detailed change 2

Closes #issue-number
```

### Pull Request Template
```markdown
## Description
Brief description of changes

## Phase
Phase X: [Phase Name]

## Testing
- [ ] Unit tests added/updated
- [ ] Manual testing completed
- [ ] No regressions

## Checklist
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] No hardcoded secrets
```

### Code Review Criteria
- [ ] Functionality works as intended
- [ ] Code is readable and maintainable
- [ ] No security vulnerabilities
- [ ] Adequate error handling
- [ ] Tests cover edge cases
- [ ] Documentation is clear

---

## Risk Management

### High Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| YouTube API quota exceeded | High | Implement quota tracking, request increase |
| API policy changes | High | Monitor YouTube API updates, have fallback |
| PyInstaller packaging issues | Medium | Test early, use virtual environments |
| OAuth token expiry | Medium | Implement auto-refresh, user re-auth |

### Medium Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| yt-dlp breaking changes | Medium | Pin version, test updates before deploying |
| Network failures | Medium | Retry logic, queue system |
| Disk space issues | Medium | Monitor space, alert user, auto-cleanup |

### Low Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| GUI rendering issues | Low | Test on multiple systems |
| Log file bloat | Low | Implement rotation, max size limits |

---

## Resource Requirements

### Development Tools
- Windows 10/11 PC (for development & testing)
- Python 3.11+
- VS Code or PyCharm
- Git for version control
- YouTube test channels (2 minimum)

### External Services
- YouTube Data API v3 (free, quota limits apply)
- GitHub (repository hosting, releases)

### Estimated Time Investment
- **Development**: 120-150 hours
- **Testing**: 30-40 hours
- **Documentation**: 15-20 hours
- **Total**: ~165-210 hours (4-6 weeks full-time)

---

## Success Criteria

### MVP Requirements (Must Have)
- ✅ Monitor single channel
- ✅ Download videos automatically
- ✅ Upload to user channel
- ✅ System tray UI
- ✅ Active hours support
- ✅ Basic error handling
- ✅ Logging

### V1.0 Requirements (Should Have)
- ✅ All MVP features
- ✅ Settings GUI
- ✅ Dashboard with stats
- ✅ Notifications
- ✅ Catch-up on startup
- ✅ Auto-start with Windows
- ✅ Comprehensive documentation

### V1.1 Requirements (Nice to Have)
- ⬜ Multiple channel support
- ⬜ Video editing (intro/outro)
- ⬜ Scheduled uploads
- ⬜ Cloud backup
- ⬜ Mobile monitoring app

---

## Next Steps

### Immediate Actions (This Week)
1. ✅ Review and approve PRD
2. ✅ Review and approve PLAN
3. 🔄 Set up development environment (Phase 0)
4. 🔄 Create project structure (Phase 0)
5. 🔄 Initialize Git repository (Phase 0)

### Week 2 Actions
1. 🔲 Complete Phase 0 (Setup)
2. 🔲 Begin Phase 1 (Core Backend)
3. 🔲 Set up YouTube API credentials
4. 🔲 Create test YouTube channels

### Weekly Sync
- **When**: Every Monday 10 AM
- **What**: Review progress, blockers, next week plan
- **Where**: GitHub Issues / Project Board

---

**Status Legend:**
- ✅ Completed
- 🔄 In Progress  
- 🔲 Not Started
- ⚠️ Blocked
- ❌ Cancelled

**Document Version:** 1.0  
**Last Updated:** November 8, 2025  
**Next Review:** Start of each phase
