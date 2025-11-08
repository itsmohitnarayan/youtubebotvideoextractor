# Product Requirements Document (PRD)
## YouTube Video Replicator Bot

**Version:** 1.0  
**Date:** November 8, 2025  
**Project:** YouTubeBotVideoExtractor  
**Type:** Windows Desktop Application

---

## 1. Product Overview

### 1.1 Purpose
A Windows desktop application that automatically monitors a specified YouTube channel, downloads newly uploaded videos with thumbnails and metadata, and re-uploads them to the user's YouTube channel within a 15-minute window.

### 1.2 Target Users
- Content creators with permission to replicate content
- Channel managers handling multiple channels
- Users running local automation on Windows PC (10 AM - 10 PM daily)

### 1.3 Key Value Proposition
- **Automated workflow**: Zero manual intervention once configured
- **Time-bound execution**: Works during PC active hours (10 AM - 10 PM)
- **Non-intrusive**: System tray application, minimal UI interaction
- **Fast replication**: 15-minute upload window from source video publication
- **Catch-up capability**: Processes missed videos from overnight

---

## 2. Technical Stack

### 2.1 Core Technologies
| Component | Technology | Version |
|-----------|------------|---------|
| **Language** | Python | 3.11+ |
| **GUI Framework** | PyQt5 | 5.15+ |
| **Video Download** | yt-dlp | Latest |
| **YouTube API** | google-api-python-client | 2.x |
| **Task Scheduling** | APScheduler | 3.x |
| **HTTP Client** | httpx | Latest |
| **Configuration** | python-dotenv + JSON | Latest |
| **Logging** | Python logging module | Built-in |
| **Packaging** | PyInstaller | 6.x |

### 2.2 Architecture
```
┌─────────────────────────────────────────────┐
│           Windows Desktop App               │
│              (System Tray)                  │
└─────────────────┬───────────────────────────┘
                  │
    ┌─────────────┴─────────────┐
    │                           │
┌───▼────┐              ┌───────▼──────┐
│ Monitor│              │   GUI Layer  │
│ Service│              │   (PyQt5)    │
└───┬────┘              └──────────────┘
    │
    ├─► YouTube API (Detection)
    │
    ├─► yt-dlp (Download)
    │
    ├─► YouTube API (Upload)
    │
    └─► SQLite DB (State/Logs)
```

### 2.3 External Dependencies
- **YouTube Data API v3**: Channel monitoring, video upload
- **OAuth 2.0**: Authentication for YouTube API
- **FFmpeg**: Video processing (bundled with yt-dlp)

### 2.4 Data Structures & Algorithms (DSA)

The backend implementation leverages proper data structures and algorithms for optimal performance:

#### Core Data Structures
| Use Case | Data Structure | Justification |
|----------|----------------|---------------|
| **Processed Videos Tracking** | Hash Set (Python `set`) | O(1) duplicate detection, fast lookup for video IDs |
| **Video Processing Queue** | Priority Queue (`queue.PriorityQueue`) | FIFO processing with priority support for urgent videos |
| **Download/Upload Cache** | LRU Cache (`functools.lru_cache`) | Cache API responses, reduce redundant calls |
| **Video Metadata Storage** | Dictionary (Hash Map) | O(1) access to video metadata by video ID |
| **Task Scheduling** | Min Heap | Efficient next-task retrieval for scheduler |
| **Log Buffer** | Circular Buffer (Ring Buffer) | Fixed-size in-memory log storage, prevent memory bloat |
| **Statistics Aggregation** | OrderedDict | Maintain time-series stats in insertion order |

#### Key Algorithms
| Operation | Algorithm | Complexity | Purpose |
|-----------|-----------|------------|---------|
| **Duplicate Detection** | Hash-based lookup | O(1) | Check if video already processed |
| **Video Queue Processing** | FIFO Queue | O(1) enqueue/dequeue | Sequential video processing |
| **API Quota Management** | Token Bucket Algorithm | O(1) | Rate limiting, prevent quota exhaustion |
| **Retry Logic** | Exponential Backoff | O(log n) | Network failure recovery |
| **File Cleanup** | LRU Eviction | O(1) amortized | Remove oldest downloaded files when disk space low |
| **Log Rotation** | Sliding Window | O(1) | Maintain last N log entries in memory |
| **Time-based Scheduling** | Cron Expression Parsing | O(1) | Determine next execution time |
| **Database Queries** | Indexed B-Tree Search | O(log n) | Fast video lookup in SQLite |

#### Performance Optimizations
```python
# Example implementations:

# 1. Hash Set for O(1) duplicate detection
processed_videos: set[str] = set()

def is_video_processed(video_id: str) -> bool:
    return video_id in processed_videos  # O(1) lookup

# 2. Priority Queue for video processing
import queue

video_queue = queue.PriorityQueue()
video_queue.put((priority, timestamp, video_data))  # O(log n) insertion

# 3. LRU Cache for API responses
from functools import lru_cache

@lru_cache(maxsize=128)
def get_video_details(video_id: str):
    return youtube_api.videos().list(id=video_id).execute()

# 4. Token Bucket for rate limiting
class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False  # Rate limited
    
    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

# 5. Circular Buffer for logs
class CircularBuffer:
    def __init__(self, max_size: int):
        self.buffer = [None] * max_size
        self.max_size = max_size
        self.head = 0
        self.count = 0
    
    def append(self, item):
        self.buffer[self.head] = item
        self.head = (self.head + 1) % self.max_size
        self.count = min(self.count + 1, self.max_size)
```

#### Memory Management
- **Bounded queues**: Prevent unbounded memory growth
- **Lazy loading**: Load video data only when needed
- **Stream processing**: Process large files without loading entirely into memory
- **Garbage collection**: Explicit cleanup of temporary files and objects

#### Concurrency Patterns
- **Producer-Consumer**: Monitor thread produces, worker threads consume
- **Thread Pool**: Reuse threads for download/upload tasks
- **Locks/Semaphores**: Thread-safe access to shared resources (database, queues)
- **Async I/O**: Non-blocking API calls where possible

---

## 3. Functional Requirements

### 3.1 Core Features

#### F1: Channel Monitoring
- **F1.1**: Monitor specified YouTube channel for new video uploads
- **F1.2**: Check for new videos every 10 minutes during active hours
- **F1.3**: Detect videos uploaded since last check (catch-up mechanism)
- **F1.4**: Extract video metadata (title, description, tags, thumbnail)

#### F2: Video Download
- **F2.1**: Download video in highest quality available
- **F2.2**: Download custom thumbnail image
- **F2.3**: Save metadata (title, description, tags, category)
- **F2.4**: Store videos in organized local directory structure
- **F2.5**: Verify download integrity

#### F3: Video Upload
- **F3.1**: Upload video to user's YouTube channel
- **F3.2**: Apply original title (with optional prefix/suffix)
- **F3.3**: Apply original description (with optional modifications)
- **F3.4**: Apply original tags
- **F3.5**: Set custom thumbnail
- **F3.6**: Configure privacy settings (public/unlisted/private)
- **F3.7**: Track upload progress

#### F4: Scheduling & Automation
- **F4.1**: Auto-start on Windows boot
- **F4.2**: Operate only during configured hours (10 AM - 10 PM)
- **F4.3**: Auto-pause outside active hours
- **F4.4**: Resume automatically at start time
- **F4.5**: Catch-up: Process videos missed during downtime

#### F5: System Tray Interface
- **F5.1**: Minimize to system tray on startup
- **F5.2**: Show status icon (idle/monitoring/downloading/uploading)
- **F5.3**: Right-click context menu:
  - Show Dashboard
  - Pause/Resume Monitoring
  - Force Check Now
  - Open Logs
  - Settings
  - Exit
- **F5.4**: Balloon notifications for events

#### F6: Dashboard (Main Window)
- **F6.1**: Display monitoring status
- **F6.2**: Show last checked timestamp
- **F6.3**: List recent videos processed
- **F6.4**: Display success/failure statistics
- **F6.5**: Show current operation progress
- **F6.6**: Quick access to logs

#### F7: Configuration Management
- **F7.1**: GUI settings panel for:
  - Target channel URL/ID
  - YouTube API credentials
  - OAuth tokens
  - Active hours (start/end time)
  - Check interval (minutes)
  - Download directory
  - Title prefix/suffix
  - Privacy settings
- **F7.2**: Save/load configuration from JSON
- **F7.3**: Validate configuration on save

#### F8: Logging & Error Handling
- **F8.1**: Log all operations (info, warning, error)
- **F8.2**: Rotate log files (max size: 10MB)
- **F8.3**: Display errors in GUI
- **F8.4**: Retry logic for failed operations
- **F8.5**: Export logs to file

#### F9: Database/State Management
- **F9.1**: Track processed video IDs (avoid duplicates)
- **F9.2**: Store upload history
- **F9.3**: Maintain operation statistics
- **F9.4**: Persist last check timestamp

### 3.2 Non-Functional Requirements

#### Performance
- **NF1**: Check for new videos within 30 seconds
- **NF2**: Start download within 1 minute of detection
- **NF3**: Complete upload within 15 minutes of source publication
- **NF4**: Handle videos up to 4K resolution
- **NF5**: Support videos up to 2 hours duration

#### Reliability
- **NF6**: 99% uptime during active hours
- **NF7**: Auto-recovery from network failures
- **NF8**: Graceful handling of API quota limits
- **NF9**: No data loss on unexpected shutdown

#### Usability
- **NF10**: One-click installation (.exe installer)
- **NF11**: Setup wizard for initial configuration
- **NF12**: Clear error messages with resolution steps
- **NF13**: Minimal resource usage (<200MB RAM, <5% CPU idle)

#### Security
- **NF14**: Secure storage of API credentials (encrypted)
- **NF15**: OAuth tokens stored securely
- **NF16**: No hardcoded secrets
- **NF17**: HTTPS for all API communications

---

## 4. User Workflows

### 4.1 Initial Setup
```
1. User downloads YouTubeBotVideoExtractor.exe
2. User runs installer
3. Setup wizard launches:
   a. Welcome screen
   b. YouTube API credentials input
   c. OAuth authentication flow
   d. Target channel selection
   e. Active hours configuration
   f. Download directory selection
   g. Upload settings (title format, privacy)
4. App starts and minimizes to system tray
5. Monitoring begins
```

### 4.2 Daily Operation
```
10:00 AM - PC boots, app auto-starts
10:01 AM - App checks for videos uploaded overnight
        - If found: Download → Upload queue
10:01 AM - 10:00 PM:
        - Check every 10 minutes
        - Download new videos immediately
        - Upload automatically
        - Show notifications
10:00 PM - User shuts down PC
        - App saves state
        - Graceful shutdown
```

### 4.3 Manual Intervention
```
User wants to pause:
1. Right-click system tray icon
2. Select "Pause Monitoring"
3. App stops checking (existing downloads complete)

User wants to force check:
1. Right-click system tray icon
2. Select "Check Now"
3. Immediate check for new videos

User wants to view status:
1. Double-click system tray icon
2. Dashboard opens showing current state
```

---

## 5. API Requirements

### 5.1 YouTube Data API v3

#### Endpoints Used:
| Operation | Endpoint | Quota Cost |
|-----------|----------|------------|
| Search channel videos | `search.list` | 100 units |
| Get video details | `videos.list` | 1 unit |
| Upload video | `videos.insert` | 1600 units |
| Set thumbnail | `thumbnails.set` | 50 units |

#### Daily Quota:
- **Default**: 10,000 units/day
- **Estimated usage** (12 hours, check every 10min):
  - 72 searches × 100 = 7,200 units
  - 5 uploads × 1650 = 8,250 units (if 5 videos/day)
  - **Total**: ~15,450 units (needs quota increase request)

### 5.2 Authentication
- **OAuth 2.0** flow for user consent
- **Scopes required**:
  - `https://www.googleapis.com/auth/youtube.upload`
  - `https://www.googleapis.com/auth/youtube.readonly`
- **Token refresh**: Automatic refresh token handling

---

## 6. Data Models

### 6.1 Configuration Schema
```json
{
  "target_channel_id": "UC...",
  "active_hours": {
    "start": "10:00",
    "end": "22:00"
  },
  "check_interval_minutes": 10,
  "download_directory": "C:/YouTubeBot/downloads",
  "upload_settings": {
    "title_prefix": "",
    "title_suffix": "",
    "privacy_status": "public",
    "category_id": "22"
  },
  "youtube_api": {
    "client_secrets_file": "client_secrets.json",
    "token_file": "oauth_token.json"
  }
}
```

### 6.2 Database Schema (SQLite)
```sql
-- Processed videos
CREATE TABLE videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_video_id TEXT UNIQUE NOT NULL,
    source_title TEXT,
    source_published_at DATETIME,
    downloaded_at DATETIME,
    uploaded_at DATETIME,
    target_video_id TEXT,
    status TEXT, -- pending, downloading, uploading, completed, failed
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Logs
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    level TEXT, -- INFO, WARNING, ERROR
    message TEXT,
    details TEXT
);

-- Statistics
CREATE TABLE stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE UNIQUE,
    videos_detected INTEGER DEFAULT 0,
    videos_downloaded INTEGER DEFAULT 0,
    videos_uploaded INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0
);
```

---

## 7. UI Mockup Structure

### 7.1 System Tray Icon States
- 🟢 **Green**: Monitoring active, idle
- 🔵 **Blue**: Downloading video
- 🟡 **Yellow**: Uploading video
- 🔴 **Red**: Error occurred
- ⚫ **Gray**: Paused/Outside active hours

### 7.2 Main Dashboard (PyQt5 Window)
```
┌─────────────────────────────────────────────┐
│  YouTube Video Replicator Bot        [_][□][X]│
├─────────────────────────────────────────────┤
│  Status: ● Monitoring Active                │
│  Target Channel: @ExampleChannel            │
│  Last Checked: 2 minutes ago                │
│  Next Check: in 8 minutes                   │
├─────────────────────────────────────────────┤
│  Today's Activity:                          │
│    Videos Detected: 3                       │
│    Downloaded: 3                            │
│    Uploaded: 2                              │
│    In Progress: 1 (uploading...)            │
│                                             │
│  [Progress Bar: 67% - "Video Title"]        │
├─────────────────────────────────────────────┤
│  Recent Videos:                             │
│  ✓ Video 1 - Uploaded at 2:30 PM            │
│  ✓ Video 2 - Uploaded at 1:15 PM            │
│  ⏳ Video 3 - Uploading...                   │
├─────────────────────────────────────────────┤
│  [Pause] [Check Now] [Settings] [View Logs] │
└─────────────────────────────────────────────┘
```

---

## 8. Error Handling

### 8.1 Error Scenarios
| Error Type | Handling Strategy |
|------------|-------------------|
| Network failure | Retry 3 times with exponential backoff |
| API quota exceeded | Pause monitoring, resume next day |
| Download failure | Retry 2 times, skip if persistent |
| Upload failure | Save to queue, retry later |
| Invalid credentials | Show error dialog, prompt re-authentication |
| Disk space low | Alert user, pause downloads |
| Video unavailable | Log and skip |

---

## 9. Success Metrics

### 9.1 KPIs
- **Detection Speed**: <5 minutes from source publication
- **Upload Success Rate**: >95% of detected videos
- **Time to Upload**: <15 minutes from detection
- **Uptime**: >99% during active hours
- **Error Rate**: <5% of operations

---

## 10. Future Enhancements (Post-MVP)

### Phase 2 Features:
- Multiple channel monitoring
- Video editing before upload (intro/outro insertion)
- Custom watermark overlay
- Scheduled uploads (delay publication)
- Cloud sync for multi-PC operation
- Mobile app for monitoring
- Discord/Telegram notifications
- Advanced filters (upload only certain video types)

### Phase 3 Features:
- Web dashboard
- Analytics integration
- AI-powered title/description optimization
- Automatic tag generation
- Multi-language support
- Plugin system for extensibility

---

## 11. Legal & Compliance

### 11.1 Requirements
- ⚠️ **User must have explicit permission** from source channel owner
- ⚠️ **Comply with YouTube Terms of Service**
- ⚠️ **Respect copyright laws**
- ⚠️ **Include disclaimer in app**: "Use only with proper authorization"

### 11.2 Disclaimer
```
This software is provided for legitimate content management purposes only.
Users are solely responsible for ensuring they have the legal right to 
download and re-upload content. Misuse may result in account termination,
DMCA claims, or legal action. Use at your own risk.
```

---

## 12. Deployment & Distribution

### 12.1 Packaging
- **Format**: Single .exe (PyInstaller)
- **Size Target**: <100MB
- **Installer**: Inno Setup or NSIS
- **Auto-update**: GitHub Releases integration

### 12.2 Installation Requirements
- **OS**: Windows 10/11 (64-bit)
- **RAM**: 4GB minimum, 8GB recommended
- **.NET Framework**: Not required (Python bundled)
- **Disk Space**: 500MB for app + downloads
- **Internet**: Broadband connection required

---

## 13. Support & Documentation

### 13.1 Documentation Deliverables
1. **README.md**: Quick start guide
2. **SETUP.md**: YouTube API credential setup
3. **USER_GUIDE.md**: Complete user manual
4. **TROUBLESHOOTING.md**: Common issues & solutions
5. **API_LIMITS.md**: Quota management guide
6. **FAQ.md**: Frequently asked questions

---

**Document Status**: ✅ Approved  
**Next Step**: Review PLAN.md for implementation phases
