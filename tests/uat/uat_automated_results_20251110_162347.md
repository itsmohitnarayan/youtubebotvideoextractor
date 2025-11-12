# UAT Automated Test Results
**Date:** 2025-11-10 16:23:46  
**Platform:** Windows 11  
**Python:** 3.14.0

## Summary
- **Total Tests:** 96
- **Passed:** 83
- **Failed:** 13
- **Pass Rate:** 86.5%

## Results by Scenario

### TS-002 (0/1 passed)

| Test | Status | Severity | Details |
|------|--------|----------|----------|
| Config loading | FAIL | CRITICAL | Error: 'ConfigManager' object has no attribute 'co... |

### TS-003 (12/12 passed)

| Test | Status | Severity | Details |
|------|--------|----------|----------|
| Database initialized successfully | PASS | CRITICAL | Path: D:\2025\youtubebotvideoextractor\data\videos... |
| Table 'videos' exists | PASS | HIGH | Tables found: videos, sqlite_sequence, logs, stats... |
| Table 'settings' exists | PASS | HIGH | Tables found: videos, sqlite_sequence, logs, stats... |
| Table 'logs' exists | PASS | HIGH | Tables found: videos, sqlite_sequence, logs, stats... |
| Table 'stats' exists | PASS | HIGH | Tables found: videos, sqlite_sequence, logs, stats... |
| Column 'videos.id' exists | PASS | MEDIUM | Columns: id, source_video_id, source_title, source... |
| Column 'videos.source_video_id' exists | PASS | MEDIUM | Columns: id, source_video_id, source_title, source... |
| Column 'videos.source_title' exists | PASS | MEDIUM | Columns: id, source_video_id, source_title, source... |
| Column 'videos.status' exists | PASS | MEDIUM | Columns: id, source_video_id, source_title, source... |
| Column 'videos.created_at' exists | PASS | MEDIUM | Columns: id, source_video_id, source_title, source... |
| Can query videos table | PASS | HIGH | Current record count: 0 |
| Database integrity check | PASS | CRITICAL | Result: ok |

### TS-004 (12/12 passed)

| Test | Status | Severity | Details |
|------|--------|----------|----------|
| Valid URL accepted: https://www.youtube.com/watch?v=dQw4w9WgXcQ... | PASS | HIGH |  |
| Valid URL accepted: https://youtu.be/dQw4w9WgXcQ... | PASS | HIGH |  |
| Valid URL accepted: https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s... | PASS | HIGH |  |
| Invalid URL rejected: http://www.youtube.com/watch?v=invalid... | PASS | HIGH | Error message: Only HTTPS URLs are allowed for sec... |
| Invalid URL rejected: https://example.com/video... | PASS | HIGH | Error message: Invalid YouTube URL format |
| Invalid URL rejected: not_a_url... | PASS | HIGH | Error message: Invalid YouTube URL format |
| Invalid URL rejected: ... | PASS | HIGH | Error message: URL cannot be empty |
| Invalid URL rejected: javascript:alert(1)... | PASS | HIGH | Error message: Invalid YouTube URL format |
| Path validation: normal_file.txt... | PASS | CRITICAL | Expected valid=True, Got valid=True, Message:  |
| Path validation: ../../../etc/passwd... | PASS | CRITICAL | Expected valid=False, Got valid=False, Message: Pa... |
| Path validation: ..\..\windows\system32\config... | PASS | CRITICAL | Expected valid=False, Got valid=False, Message: Pa... |
| Path validation: D:\2025\youtubebotvideoextractor\data\te... | PASS | CRITICAL | Expected valid=True, Got valid=True, Message:  |

### TS-005 (19/20 passed)

| Test | Status | Severity | Details |
|------|--------|----------|----------|
| File exists: README.md | PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\README.md |
| File readable: README.md | PASS | MEDIUM |  |
| File exists: SETUP.md | PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\SETUP.md |
| File readable: SETUP.md | PASS | MEDIUM |  |
| File exists: requirements.txt | PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\requirement... |
| File readable: requirements.txt | PASS | MEDIUM |  |
| File exists: src/core/config.py | PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\src\core\co... |
| File readable: src/core/config.py | PASS | MEDIUM |  |
| File exists: src/database/db_manager.py | FAIL | HIGH | Path: D:\2025\youtubebotvideoextractor\src\databas... |
| File exists: src/youtube/api_client.py | PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\src\youtube... |
| File readable: src/youtube/api_client.py | PASS | MEDIUM |  |
| File exists: src/gui/main_window.py | PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\src\gui\mai... |
| File readable: src/gui/main_window.py | PASS | MEDIUM |  |
| File exists: docs/USER_GUIDE.md | PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\docs\USER_G... |
| File readable: docs/USER_GUIDE.md | PASS | MEDIUM |  |
| File exists: docs/TROUBLESHOOTING.md | PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\docs\TROUBL... |
| File readable: docs/TROUBLESHOOTING.md | PASS | MEDIUM |  |
| File exists: docs/API_LIMITS.md | PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\docs\API_LI... |
| File readable: docs/API_LIMITS.md | PASS | MEDIUM |  |
| Data directory has restricted permissions | PASS | MEDIUM | File security utility integrated in Phase 5 Task 4 |

### TS-006 (1/12 passed)

| Test | Status | Severity | Details |
|------|--------|----------|----------|
| Package 'python-dotenv' importable | FAIL | HIGH | Package not installed (tried importing 'python_dot... |
| Package 'httpx' importable | FAIL | HIGH | Package not installed (tried importing 'httpx') |
| Package 'requests' importable | FAIL | HIGH | Package not installed (tried importing 'requests') |
| Package 'google-api-python-client' importable | FAIL | HIGH | Package not installed (tried importing 'google_api... |
| Package 'google-auth-oauthlib' importable | FAIL | HIGH | Package not installed (tried importing 'google_aut... |
| Package 'google-auth-httplib2' importable | FAIL | HIGH | Package not installed (tried importing 'google_aut... |
| Package 'yt-dlp' importable | FAIL | HIGH | Package not installed (tried importing 'yt_dlp') |
| Package 'PyQt5' importable | FAIL | HIGH | Package not installed (tried importing 'PyQt5') |
| Package 'APScheduler' importable | FAIL | HIGH | Package not installed (tried importing 'apschedule... |
| Package 'Pillow' importable | FAIL | HIGH | Package not installed (tried importing 'PIL') |
| Package 'tqdm' importable | FAIL | HIGH | Package not installed (tried importing 'tqdm') |
| FFmpeg installed and accessible | PASS | HIGH | Version: ffmpeg version 8.0-full_build-www.gyan.de... |

### TS-022 (4/4 passed)

| Test | Status | Severity | Details |
|------|--------|----------|----------|
| CPU usage idle < 5% | PASS | HIGH | Current: 0.00% |
| Memory usage idle < 100 MB | PASS | HIGH | Current: 29.58 MB |
| Thread count reasonable (< 20) | PASS | MEDIUM | Current: 7 threads |
| Open file handles reasonable (< 50) | PASS | MEDIUM | Current: 1 handles |

### TS-DOC (23/23 passed)

| Test | Status | Severity | Details |
|------|--------|----------|----------|
| Project Overview has content (> 1 KB) | PASS | HIGH | Size: 11,218 bytes |
| Project Overview mentions 'installation' | PASS | MEDIUM |  |
| Project Overview mentions 'features' | PASS | MEDIUM |  |
| Project Overview mentions 'usage' | PASS | MEDIUM |  |
| Setup Guide has content (> 1 KB) | PASS | HIGH | Size: 11,232 bytes |
| Setup Guide mentions 'prerequisites' | PASS | MEDIUM |  |
| Setup Guide mentions 'python' | PASS | MEDIUM |  |
| Setup Guide mentions 'ffmpeg' | PASS | MEDIUM |  |
| Setup Guide mentions 'dependencies' | PASS | MEDIUM |  |
| User Guide has content (> 1 KB) | PASS | HIGH | Size: 19,282 bytes |
| User Guide mentions 'configuration' | PASS | MEDIUM |  |
| User Guide mentions 'queue' | PASS | MEDIUM |  |
| User Guide mentions 'upload' | PASS | MEDIUM |  |
| User Guide mentions 'dashboard' | PASS | MEDIUM |  |
| Troubleshooting has content (> 1 KB) | PASS | HIGH | Size: 16,963 bytes |
| Troubleshooting mentions 'authentication' | PASS | MEDIUM |  |
| Troubleshooting mentions 'download' | PASS | MEDIUM |  |
| Troubleshooting mentions 'upload' | PASS | MEDIUM |  |
| Troubleshooting mentions 'error' | PASS | MEDIUM |  |
| API Limits has content (> 1 KB) | PASS | HIGH | Size: 14,346 bytes |
| API Limits mentions 'quota' | PASS | MEDIUM |  |
| API Limits mentions 'limits' | PASS | MEDIUM |  |
| API Limits mentions 'optimization' | PASS | MEDIUM |  |

### TS-ENV (7/7 passed)

| Test | Status | Severity | Details |
|------|--------|----------|----------|
| Python Version >= 3.8 | PASS | CRITICAL | Found: 3.14.0 |
| Running on Windows | PASS | CRITICAL | OS: Windows 11 |
| Directory 'src' exists | PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\src |
| Directory 'tests' exists | PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\tests |
| Directory 'data' exists | PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\data |
| Directory 'logs' exists | PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\logs |
| Directory 'docs' exists | PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\docs |

### TS-SECURITY (5/5 passed)

| Test | Status | Severity | Details |
|------|--------|----------|----------|
| Security file exists: src/utils/validators.py | PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\src\utils\v... |
| Path traversal prevention implemented | PASS | CRITICAL | resolve: True, relative_to: True |
| Security file exists: src/utils/file_security.py | PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\src\utils\f... |
| Security file exists: scripts/security_audit.py | PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\scripts\sec... |
| HTTPS enforced in tests (no HTTP YouTube URLs) | PASS | MEDIUM | Files with HTTP: None |

