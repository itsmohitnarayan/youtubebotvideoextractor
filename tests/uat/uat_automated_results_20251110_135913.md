# UAT Automated Test Results
**Date:** 2025-11-10 13:59:09  
**Platform:** Windows 11  
**Python:** 3.14.0

## Summary
- **Total Tests:** 91
- **Passed:** 64 ✅
- **Failed:** 27 ❌
- **Pass Rate:** 70.3%

## Results by Scenario

### TS-002 (0/1 passed)

| Test | Status | Severity | Details |
|------|--------|----------|----------|
| Config loading | ❌ FAIL | CRITICAL | Error: 'ConfigManager' object has no attribute 'co... |

### TS-003 (1/10 passed)

| Test | Status | Severity | Details |
|------|--------|----------|----------|
| Database initialized successfully | ✅ PASS | CRITICAL | Path: D:\2025\youtubebotvideoextractor\data\videos... |
| Table 'videos' exists | ❌ FAIL | HIGH | Tables found:  |
| Table 'settings' exists | ❌ FAIL | HIGH | Tables found:  |
| Table 'upload_history' exists | ❌ FAIL | HIGH | Tables found:  |
| Column 'videos.id' exists | ❌ FAIL | MEDIUM | Columns:  |
| Column 'videos.video_id' exists | ❌ FAIL | MEDIUM | Columns:  |
| Column 'videos.title' exists | ❌ FAIL | MEDIUM | Columns:  |
| Column 'videos.status' exists | ❌ FAIL | MEDIUM | Columns:  |
| Column 'videos.created_at' exists | ❌ FAIL | MEDIUM | Columns:  |
| Database initialization | ❌ FAIL | CRITICAL | Error: no such table: videos |

### TS-004 (3/12 passed)

| Test | Status | Severity | Details |
|------|--------|----------|----------|
| Valid URL accepted: https://www.youtube.com/watch?v=dQw4w9WgXcQ... | ✅ PASS | HIGH |  |
| Valid URL accepted: https://youtu.be/dQw4w9WgXcQ... | ✅ PASS | HIGH |  |
| Valid URL accepted: https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s... | ✅ PASS | HIGH |  |
| Invalid URL rejected: http://www.youtube.com/watch?v=invalid... | ❌ FAIL | HIGH | Validation result: (True, '') |
| Invalid URL rejected: https://example.com/video... | ❌ FAIL | HIGH | Validation result: (False, 'Invalid YouTube URL fo... |
| Invalid URL rejected: not_a_url... | ❌ FAIL | HIGH | Validation result: (False, 'Invalid YouTube URL fo... |
| Invalid URL rejected: ... | ❌ FAIL | HIGH | Validation result: (False, 'URL cannot be empty') |
| Invalid URL rejected: javascript:alert(1)... | ❌ FAIL | HIGH | Validation result: (False, 'Invalid YouTube URL fo... |
| Path validation: normal_file.txt... | ❌ FAIL | CRITICAL | Expected: True, Got: (False, 'Path traversal detec... |
| Path validation: ../../../etc/passwd... | ❌ FAIL | CRITICAL | Expected: False, Got: (False, 'Path traversal dete... |
| Path validation: ..\..\windows\system32\config... | ❌ FAIL | CRITICAL | Expected: False, Got: (False, 'Path traversal dete... |
| Path validation: D:\2025\youtubebotvideoextractor\data\te... | ❌ FAIL | CRITICAL | Expected: True, Got: (True, '') |

### TS-005 (17/19 passed)

| Test | Status | Severity | Details |
|------|--------|----------|----------|
| File exists: README.md | ✅ PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\README.md |
| File readable: README.md | ✅ PASS | MEDIUM |  |
| File exists: SETUP.md | ❌ FAIL | HIGH | Path: D:\2025\youtubebotvideoextractor\SETUP.md |
| File exists: requirements.txt | ✅ PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\requirement... |
| File readable: requirements.txt | ✅ PASS | MEDIUM |  |
| File exists: src/core/config.py | ✅ PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\src\core\co... |
| File readable: src/core/config.py | ✅ PASS | MEDIUM |  |
| File exists: src/database/db_manager.py | ❌ FAIL | HIGH | Path: D:\2025\youtubebotvideoextractor\src\databas... |
| File exists: src/youtube/api_client.py | ✅ PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\src\youtube... |
| File readable: src/youtube/api_client.py | ✅ PASS | MEDIUM |  |
| File exists: src/gui/main_window.py | ✅ PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\src\gui\mai... |
| File readable: src/gui/main_window.py | ✅ PASS | MEDIUM |  |
| File exists: docs/USER_GUIDE.md | ✅ PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\docs\USER_G... |
| File readable: docs/USER_GUIDE.md | ✅ PASS | MEDIUM |  |
| File exists: docs/TROUBLESHOOTING.md | ✅ PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\docs\TROUBL... |
| File readable: docs/TROUBLESHOOTING.md | ✅ PASS | MEDIUM |  |
| File exists: docs/API_LIMITS.md | ✅ PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\docs\API_LI... |
| File readable: docs/API_LIMITS.md | ✅ PASS | MEDIUM |  |
| Data directory has restricted permissions | ✅ PASS | MEDIUM | File security utility integrated in Phase 5 Task 4 |

### TS-006 (9/14 passed)

| Test | Status | Severity | Details |
|------|--------|----------|----------|
| Package 'python-dotenv' importable | ❌ FAIL | HIGH | Import error: No module named 'python_dotenv' |
| Package 'httpx' importable | ✅ PASS | HIGH | Import name: httpx |
| Package 'requests' importable | ✅ PASS | HIGH | Import name: requests |
| Package 'google-api-python-client' importable | ❌ FAIL | HIGH | Import error: No module named 'google_api_python_c... |
| Package 'google-auth-oauthlib' importable | ✅ PASS | HIGH | Import name: google_auth_oauthlib |
| Package 'google-auth-httplib2' importable | ✅ PASS | HIGH | Import name: google_auth_httplib2 |
| Package 'yt-dlp' importable | ✅ PASS | HIGH | Import name: yt_dlp |
| Package 'PyQt5' importable | ✅ PASS | HIGH | Import name: PyQt5 |
| Package 'PyQt5-Qt5' importable | ❌ FAIL | HIGH | Import error: No module named 'pyqt5_qt5' |
| Package 'PyQt5-sip' importable | ❌ FAIL | HIGH | Import error: No module named 'pyqt5_sip' |
| Package 'APScheduler' importable | ✅ PASS | HIGH | Import name: apscheduler |
| Package 'Pillow' importable | ✅ PASS | HIGH | Import name: PIL |
| Package 'tqdm' importable | ✅ PASS | HIGH | Import name: tqdm |
| FFmpeg installed and accessible | ❌ FAIL | HIGH | Error: [WinError 2] The system cannot find the fil... |

### TS-022 (4/4 passed)

| Test | Status | Severity | Details |
|------|--------|----------|----------|
| CPU usage idle < 5% | ✅ PASS | HIGH | Current: 0.00% |
| Memory usage idle < 100 MB | ✅ PASS | HIGH | Current: 67.36 MB |
| Thread count reasonable (< 20) | ✅ PASS | MEDIUM | Current: 7 threads |
| Open file handles reasonable (< 50) | ✅ PASS | MEDIUM | Current: 2 handles |

### TS-DOC (18/19 passed)

| Test | Status | Severity | Details |
|------|--------|----------|----------|
| Project Overview has content (> 1 KB) | ✅ PASS | HIGH | Size: 11,186 bytes |
| Project Overview mentions 'installation' | ✅ PASS | MEDIUM |  |
| Project Overview mentions 'features' | ✅ PASS | MEDIUM |  |
| Project Overview mentions 'usage' | ✅ PASS | MEDIUM |  |
| Setup Guide exists | ❌ FAIL | CRITICAL | File not found: D:\2025\youtubebotvideoextractor\S... |
| User Guide has content (> 1 KB) | ✅ PASS | HIGH | Size: 19,282 bytes |
| User Guide mentions 'configuration' | ✅ PASS | MEDIUM |  |
| User Guide mentions 'queue' | ✅ PASS | MEDIUM |  |
| User Guide mentions 'upload' | ✅ PASS | MEDIUM |  |
| User Guide mentions 'dashboard' | ✅ PASS | MEDIUM |  |
| Troubleshooting has content (> 1 KB) | ✅ PASS | HIGH | Size: 16,963 bytes |
| Troubleshooting mentions 'authentication' | ✅ PASS | MEDIUM |  |
| Troubleshooting mentions 'download' | ✅ PASS | MEDIUM |  |
| Troubleshooting mentions 'upload' | ✅ PASS | MEDIUM |  |
| Troubleshooting mentions 'error' | ✅ PASS | MEDIUM |  |
| API Limits has content (> 1 KB) | ✅ PASS | HIGH | Size: 14,346 bytes |
| API Limits mentions 'quota' | ✅ PASS | MEDIUM |  |
| API Limits mentions 'limits' | ✅ PASS | MEDIUM |  |
| API Limits mentions 'optimization' | ✅ PASS | MEDIUM |  |

### TS-ENV (7/7 passed)

| Test | Status | Severity | Details |
|------|--------|----------|----------|
| Python Version >= 3.8 | ✅ PASS | CRITICAL | Found: 3.14.0 |
| Running on Windows | ✅ PASS | CRITICAL | OS: Windows 11 |
| Directory 'src' exists | ✅ PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\src |
| Directory 'tests' exists | ✅ PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\tests |
| Directory 'data' exists | ✅ PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\data |
| Directory 'logs' exists | ✅ PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\logs |
| Directory 'docs' exists | ✅ PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\docs |

### TS-SECURITY (5/5 passed)

| Test | Status | Severity | Details |
|------|--------|----------|----------|
| Security file exists: src/utils/validators.py | ✅ PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\src\utils\v... |
| Path traversal prevention implemented | ✅ PASS | CRITICAL | resolve: True, relative_to: True |
| Security file exists: src/utils/file_security.py | ✅ PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\src\utils\f... |
| Security file exists: scripts/security_audit.py | ✅ PASS | HIGH | Path: D:\2025\youtubebotvideoextractor\scripts\sec... |
| HTTPS enforced in tests (no HTTP YouTube URLs) | ✅ PASS | MEDIUM | Files with HTTP: None |

