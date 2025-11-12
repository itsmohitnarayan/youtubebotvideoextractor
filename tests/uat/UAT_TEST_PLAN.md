# User Acceptance Testing (UAT) Plan
**YouTube Bot Video Extractor**  
**Phase 5 Task 6**  
**Date:** November 10, 2025  
**Version:** 1.0.0

---

## Table of Contents
1. [Overview](#overview)
2. [Test Environment Setup](#test-environment-setup)
3. [Test Scenarios](#test-scenarios)
4. [Acceptance Criteria](#acceptance-criteria)
5. [Test Execution Checklist](#test-execution-checklist)
6. [Issue Tracking](#issue-tracking)
7. [Sign-off Requirements](#sign-off-requirements)

---

## Overview

### Purpose
Validate that the YouTube Bot Video Extractor meets user requirements and operates correctly in real-world conditions.

### Scope
- **In Scope:**
  - Installation and setup procedures
  - Core functionality (download, queue, upload)
  - GUI responsiveness and usability
  - Performance under various network conditions
  - Error handling and recovery
  - Documentation accuracy
  - Long-term stability (24-hour soak test)

- **Out of Scope:**
  - Unit/integration testing (already completed)
  - Performance benchmarking (already completed)
  - Security penetration testing (audit completed)

### Success Criteria
- ✅ All critical test cases pass
- ✅ No high-severity bugs found
- ✅ Application runs continuously for 24 hours without crashes
- ✅ Documentation allows users to complete tasks without external help
- ✅ GUI remains responsive under all tested conditions

---

## Test Environment Setup

### Hardware Requirements
| Component | Minimum | Recommended | Test Configuration |
|-----------|---------|-------------|-------------------|
| OS | Windows 10 (64-bit) | Windows 11 (64-bit) | Windows 10/11 |
| RAM | 4 GB | 8 GB | 8 GB / 16 GB |
| Storage | 500 MB | 2 GB | 1 TB SSD |
| Display | 1024x768 | 1920x1080 | 1920x1080, 2560x1440, 3840x2160 (4K) |
| DPI | 100% | 100-150% | 100%, 125%, 150%, 200% |
| GPU | Integrated | Dedicated | RTX 3060 6GB |
| Internet | 1 Mbps | 10 Mbps | 0.5 Mbps, 10 Mbps, 100 Mbps |

### Software Requirements
- **Python:** 3.8+ (3.9, 3.10, 3.11, 3.12)
- **FFmpeg:** Latest stable version
- **yt-dlp:** Latest version (auto-updated by application)
- **Browser:** Edge, Chrome, or Firefox (for OAuth)

### Test Environments
1. **Clean Install Environment**
   - Fresh Windows 10/11 VM
   - No Python installed initially
   - No previous application data

2. **Upgrade Environment**
   - Existing application installation (if applicable)
   - Test upgrade/migration path

3. **Multiple Monitor Setup**
   - Primary: 1920x1080 @ 100% DPI
   - Secondary: 2560x1440 @ 125% DPI

4. **High DPI Environment**
   - 4K display @ 200% DPI
   - Test GUI scaling and readability

5. **Network Conditions**
   - **Slow:** Throttle to 0.5 Mbps (mobile 2G simulation)
   - **Normal:** 10 Mbps (typical home internet)
   - **Fast:** 100 Mbps (fiber connection)
   - **Offline:** No internet connection

---

## Test Scenarios

### TS-001: Fresh Installation
**Priority:** Critical  
**Environment:** Clean Install

**Steps:**
1. Download application from repository
2. Follow `SETUP.md` documentation
3. Install Python dependencies
4. Install FFmpeg
5. Run application for the first time

**Expected Results:**
- ✅ Installation completes without errors
- ✅ First-run wizard appears
- ✅ Configuration file created with defaults
- ✅ Database initialized successfully
- ✅ System tray icon appears
- ✅ GUI opens without errors

**Pass/Fail:** ___________  
**Notes:** ___________________________________________

---

### TS-002: YouTube OAuth Authentication
**Priority:** Critical  
**Environment:** Clean Install

**Steps:**
1. Open Settings → YouTube tab
2. Click "Authenticate with YouTube"
3. Complete OAuth flow in browser
4. Return to application

**Expected Results:**
- ✅ Browser opens to Google consent page
- ✅ After authorization, credentials saved
- ✅ "Authenticated as [email]" appears
- ✅ Token stored securely in `data/token.pickle`
- ✅ Re-authentication not required on restart

**Pass/Fail:** ___________  
**Notes:** ___________________________________________

---

### TS-003: Video Detection and Queuing
**Priority:** Critical  
**Environment:** Normal Network (10 Mbps)

**Steps:**
1. Configure monitored folder in Settings
2. Copy 3 test videos to monitored folder:
   - Small video (10 MB, 1 min)
   - Medium video (100 MB, 10 min)
   - Large video (500 MB, 30 min)
3. Observe video detection

**Expected Results:**
- ✅ Videos detected within 5 seconds
- ✅ All 3 videos added to queue
- ✅ Queue shows correct order (priority/timestamp)
- ✅ Status changes: Pending → Processing → Downloaded
- ✅ Event log shows detection events
- ✅ Dashboard updates in real-time

**Pass/Fail:** ___________  
**Notes:** ___________________________________________

---

### TS-004: Video Download
**Priority:** Critical  
**Environment:** Normal Network (10 Mbps)

**Steps:**
1. Queue a public YouTube video
2. Monitor download progress
3. Verify downloaded file

**Expected Results:**
- ✅ Download starts automatically
- ✅ Progress bar updates smoothly
- ✅ Download speed displayed (MB/s)
- ✅ ETA calculated correctly
- ✅ File saved to `downloads/` folder
- ✅ File integrity verified (playable)
- ✅ Metadata extracted (title, description, tags)

**Pass/Fail:** ___________  
**Notes:** ___________________________________________

---

### TS-005: Video Upload to YouTube
**Priority:** Critical  
**Environment:** Normal Network (10 Mbps)

**Steps:**
1. Configure upload settings (title template, description, tags, privacy)
2. Queue a small test video (10 MB)
3. Monitor upload process
4. Verify uploaded video on YouTube

**Expected Results:**
- ✅ Upload starts automatically after download
- ✅ Progress bar updates during upload
- ✅ Upload speed displayed
- ✅ Video appears on YouTube channel
- ✅ Title, description, tags applied correctly
- ✅ Privacy setting (unlisted/private) correct
- ✅ Thumbnail uploaded if configured
- ✅ Status updated to "Uploaded" with video ID

**Pass/Fail:** ___________  
**Notes:** ___________________________________________

---

### TS-006: Queue Management
**Priority:** High  
**Environment:** Normal Network (10 Mbps)

**Steps:**
1. Add 5 videos to queue
2. Test queue operations:
   - Pause a video
   - Resume a video
   - Remove a video
   - Change priority (move up/down)
   - Retry a failed video
3. Observe queue behavior

**Expected Results:**
- ✅ Pause stops processing immediately
- ✅ Resume continues from last state
- ✅ Remove deletes video from queue (not file)
- ✅ Priority changes affect processing order
- ✅ Retry resets status and re-queues
- ✅ Concurrent processing limit respected (default: 3)
- ✅ Queue persists across application restarts

**Pass/Fail:** ___________  
**Notes:** ___________________________________________

---

### TS-007: Active Hours Scheduling
**Priority:** High  
**Environment:** Normal Network (10 Mbps)

**Steps:**
1. Enable Active Hours in Settings
2. Configure: Monday-Friday, 9:00 AM - 5:00 PM
3. Queue videos outside active hours (e.g., 8:00 PM)
4. Wait for active hours to begin
5. Test behavior during/after active hours

**Expected Results:**
- ✅ Videos queued but not processed outside active hours
- ✅ Processing starts automatically at 9:00 AM
- ✅ Processing pauses automatically at 5:00 PM
- ✅ System tray shows "Waiting for Active Hours" status
- ✅ Dashboard displays next active period
- ✅ Manual override works (Force Start button)

**Pass/Fail:** ___________  
**Notes:** ___________________________________________

---

### TS-008: Error Handling - Download Failure
**Priority:** Critical  
**Environment:** Normal Network (10 Mbps)

**Steps:**
1. Queue an invalid YouTube URL
2. Queue a deleted/private video
3. Queue a geo-restricted video
4. Observe error handling

**Expected Results:**
- ✅ Invalid URL shows error: "Invalid YouTube URL"
- ✅ Deleted video shows error: "Video unavailable"
- ✅ Geo-restricted shows error with explanation
- ✅ Videos marked as "Failed" in queue
- ✅ Error message displayed in GUI
- ✅ Error logged to `logs/errors.log`
- ✅ Retry button available for failed videos
- ✅ Other videos continue processing

**Pass/Fail:** ___________  
**Notes:** ___________________________________________

---

### TS-009: Error Handling - Upload Failure
**Priority:** Critical  
**Environment:** Normal Network (10 Mbps)

**Steps:**
1. Disconnect internet during upload
2. Upload a video exceeding YouTube file size limit
3. Upload with quota exceeded (simulate)
4. Observe error handling

**Expected Results:**
- ✅ Network error triggers auto-retry (3 attempts)
- ✅ File size error shows clear message
- ✅ Quota exceeded shows helpful message with quota info
- ✅ Failed uploads remain in queue for retry
- ✅ Errors logged with full context
- ✅ User notified via system tray notification

**Pass/Fail:** ___________  
**Notes:** ___________________________________________

---

### TS-010: Network Conditions - Slow Internet
**Priority:** High  
**Environment:** Slow Network (0.5 Mbps)

**Steps:**
1. Throttle internet to 0.5 Mbps using Windows NetLimiter or router QoS
2. Queue a 50 MB video
3. Monitor download/upload behavior

**Expected Results:**
- ✅ Download progresses (slow but steady)
- ✅ Progress bar updates every 5-10 seconds
- ✅ ETA calculated based on current speed
- ✅ No timeouts or connection errors
- ✅ Upload completes successfully (slow)
- ✅ GUI remains responsive during slow transfers
- ✅ Can pause/resume during slow transfer

**Pass/Fail:** ___________  
**Notes:** ___________________________________________

---

### TS-011: Network Conditions - Fast Internet
**Priority:** Medium  
**Environment:** Fast Network (100 Mbps)

**Steps:**
1. Configure 100 Mbps connection
2. Queue a 500 MB video
3. Monitor download/upload performance

**Expected Results:**
- ✅ Download utilizes full bandwidth
- ✅ Speed displayed accurately (MB/s)
- ✅ Progress bar updates smoothly (60 FPS)
- ✅ No bandwidth throttling by application
- ✅ Upload utilizes available bandwidth
- ✅ Concurrent downloads work efficiently
- ✅ No memory leaks during large transfers

**Pass/Fail:** ___________  
**Notes:** ___________________________________________

---

### TS-012: Network Conditions - Connection Loss
**Priority:** Critical  
**Environment:** Normal Network (simulated disconnection)

**Steps:**
1. Start downloading/uploading a video
2. Disable network adapter mid-transfer
3. Wait 30 seconds
4. Re-enable network adapter
5. Observe recovery behavior

**Expected Results:**
- ✅ Transfer pauses when connection lost
- ✅ Error message: "Network unavailable, retrying..."
- ✅ Auto-retry after connection restored
- ✅ Transfer resumes from last position (if supported)
- ✅ No data corruption
- ✅ Queue status updates correctly
- ✅ System tray shows offline indicator

**Pass/Fail:** ___________  
**Notes:** ___________________________________________

---

### TS-013: GUI Responsiveness - High DPI
**Priority:** High  
**Environment:** 4K Display @ 200% DPI

**Steps:**
1. Launch application on 4K display
2. Set Windows scaling to 200%
3. Navigate all GUI screens
4. Test all controls (buttons, dropdowns, sliders)

**Expected Results:**
- ✅ All UI elements scaled correctly
- ✅ No blurry text or icons
- ✅ Buttons and controls properly sized
- ✅ Tooltips readable and positioned correctly
- ✅ Dialogs centered on screen
- ✅ No clipping or overlapping elements
- ✅ Font sizes appropriate for DPI

**Pass/Fail:** ___________  
**Notes:** ___________________________________________

---

### TS-014: GUI Responsiveness - Multiple Monitors
**Priority:** Medium  
**Environment:** Multiple Monitor Setup

**Steps:**
1. Connect 2 monitors with different resolutions/DPI
2. Launch application on primary monitor
3. Move window to secondary monitor
4. Test all GUI operations

**Expected Results:**
- ✅ Window moves smoothly between monitors
- ✅ UI scales correctly on secondary monitor
- ✅ System tray icon appears on correct monitor
- ✅ Dialogs open on monitor with main window
- ✅ Application remembers last monitor position
- ✅ No visual artifacts during monitor switch

**Pass/Fail:** ___________  
**Notes:** ___________________________________________

---

### TS-015: GUI Responsiveness - Window States
**Priority:** Medium  
**Environment:** Normal Network (10 Mbps)

**Steps:**
1. Test window operations:
   - Minimize to system tray
   - Restore from system tray
   - Maximize window
   - Restore to normal size
   - Close to system tray
   - Exit application
2. Test during active download/upload

**Expected Results:**
- ✅ Minimize hides window, tray icon remains
- ✅ Restore brings window back to previous state
- ✅ Maximize fills screen (respects taskbar)
- ✅ Close to tray continues background operations
- ✅ Exit prompts if operations in progress
- ✅ Window size/position persisted across sessions
- ✅ Operations continue when minimized

**Pass/Fail:** ___________  
**Notes:** ___________________________________________

---

### TS-016: System Tray Functionality
**Priority:** High  
**Environment:** Normal Network (10 Mbps)

**Steps:**
1. Right-click system tray icon
2. Test all context menu options:
   - Show/Hide Window
   - Pause All
   - Resume All
   - Settings
   - Exit
3. Test tray icon states

**Expected Results:**
- ✅ Context menu appears on right-click
- ✅ Show/Hide toggles window visibility
- ✅ Pause All stops all operations
- ✅ Resume All restarts operations
- ✅ Settings opens settings dialog
- ✅ Exit prompts confirmation if operations active
- ✅ Icon changes color/animation during activity:
   - 🟢 Green: Idle
   - 🔵 Blue: Processing
   - 🔴 Red: Error
   - ⚫ Gray: Paused

**Pass/Fail:** ___________  
**Notes:** ___________________________________________

---

### TS-017: Dashboard Real-time Updates
**Priority:** Medium  
**Environment:** Normal Network (10 Mbps)

**Steps:**
1. Open Dashboard tab
2. Queue 3 videos simultaneously
3. Monitor dashboard metrics:
   - Total videos processed
   - Success/failure counts
   - Average processing time
   - Quota usage
   - Recent activity log
4. Test refresh rate

**Expected Results:**
- ✅ Metrics update in real-time (< 2 second delay)
- ✅ Counters increment correctly
- ✅ Charts/graphs render smoothly
- ✅ Activity log shows latest events (auto-scroll)
- ✅ Quota usage accurate (based on API calls)
- ✅ Statistics persist across sessions
- ✅ No performance degradation with 100+ entries

**Pass/Fail:** ___________  
**Notes:** ___________________________________________

---

### TS-018: Settings Persistence
**Priority:** High  
**Environment:** Normal Network (10 Mbps)

**Steps:**
1. Modify all settings:
   - Monitored folders: Add 2 folders
   - Max concurrent: 5
   - Auto-start: Enabled
   - Active hours: Custom schedule
   - Upload template: Custom title/description
   - Notification settings: Email enabled
2. Close application
3. Reopen application
4. Verify all settings retained

**Expected Results:**
- ✅ All settings loaded from `config.yaml`
- ✅ Monitored folders list intact
- ✅ Concurrent limit applied
- ✅ Auto-start registered in Windows registry
- ✅ Active hours schedule active
- ✅ Upload templates available
- ✅ Notification preferences preserved

**Pass/Fail:** ___________  
**Notes:** ___________________________________________

---

### TS-019: Auto-start on Windows Boot
**Priority:** Medium  
**Environment:** Normal Network (10 Mbps)

**Steps:**
1. Enable "Start with Windows" in Settings
2. Restart Windows
3. Verify application behavior
4. Disable auto-start
5. Restart Windows again

**Expected Results:**
- ✅ Application starts automatically after login
- ✅ Starts minimized to system tray
- ✅ No UAC prompt during startup
- ✅ Registry entry created: `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
- ✅ Disable removes registry entry
- ✅ Application does NOT start after second restart

**Pass/Fail:** ___________  
**Notes:** ___________________________________________

---

### TS-020: Database Integrity
**Priority:** Critical  
**Environment:** Normal Network (10 Mbps)

**Steps:**
1. Process 10 videos (download + upload)
2. Close application abruptly (Task Manager → End Task)
3. Reopen application
4. Verify queue state and history
5. Run database integrity check

**Expected Results:**
- ✅ Database not corrupted after forced exit
- ✅ Queue state restored accurately
- ✅ Processing videos marked as "Interrupted"
- ✅ Completed videos remain in history
- ✅ No duplicate entries
- ✅ All foreign key constraints valid
- ✅ Database file size reasonable (< 10 MB for 100 videos)

**Pass/Fail:** ___________  
**Notes:** ___________________________________________

---

### TS-021: Logging and Debugging
**Priority:** Medium  
**Environment:** Normal Network (10 Mbps)

**Steps:**
1. Enable Debug logging in Settings
2. Process 3 videos (1 success, 1 download fail, 1 upload fail)
3. Check log files:
   - `logs/app.log`
   - `logs/errors.log`
   - `logs/youtube_api.log`
4. Verify log content and format

**Expected Results:**
- ✅ All operations logged with timestamps
- ✅ Log levels appropriate (DEBUG, INFO, WARNING, ERROR)
- ✅ Errors include stack traces
- ✅ Sensitive data NOT logged (OAuth tokens, API keys)
- ✅ Logs rotated when exceeding size limit (10 MB)
- ✅ Old logs archived with date suffix
- ✅ Logs help diagnose issues without code access

**Pass/Fail:** ___________  
**Notes:** ___________________________________________

---

### TS-022: Resource Usage - Idle State
**Priority:** High  
**Environment:** Normal Network (10 Mbps)

**Steps:**
1. Launch application with empty queue
2. Minimize to system tray
3. Monitor resource usage for 30 minutes:
   - CPU usage (Task Manager)
   - RAM usage (Task Manager)
   - Disk I/O (Resource Monitor)
   - Network usage (Resource Monitor)

**Expected Results:**
- ✅ CPU usage: 0-1% (background monitoring)
- ✅ RAM usage: < 50 MB
- ✅ Disk I/O: Minimal (< 1 KB/s)
- ✅ Network usage: 0 (no active transfers)
- ✅ No memory leaks (RAM stable over time)
- ✅ Process count stable (no thread leaks)

**Pass/Fail:** ___________  
**Notes:** ___________________________________________

---

### TS-023: Resource Usage - Active Processing
**Priority:** High  
**Environment:** Normal Network (10 Mbps)

**Steps:**
1. Queue 5 videos (total 1 GB)
2. Set max concurrent to 3
3. Monitor resource usage during processing:
   - CPU usage per video
   - RAM usage with 3 concurrent downloads
   - Disk I/O during video processing
   - Network bandwidth utilization

**Expected Results:**
- ✅ CPU usage: 5-20% per video (encoding/decoding)
- ✅ RAM usage: < 200 MB with 3 concurrent operations
- ✅ Disk I/O: Appropriate for download speeds
- ✅ Network: Full bandwidth utilized (no artificial limits)
- ✅ No resource contention between concurrent tasks
- ✅ Resources released after task completion

**Pass/Fail:** ___________  
**Notes:** ___________________________________________

---

### TS-024: 24-Hour Soak Test
**Priority:** Critical  
**Environment:** Normal Network (10 Mbps)

**Steps:**
1. Configure application:
   - Max concurrent: 3
   - Active hours: Disabled (24/7 processing)
   - Monitored folder: Enabled
2. Prepare 50 test videos (various sizes: 10 MB - 500 MB)
3. Add videos in batches over 24 hours:
   - Hour 0: 10 videos
   - Hour 6: 10 videos
   - Hour 12: 10 videos
   - Hour 18: 10 videos
   - Hour 24: 10 videos
4. Monitor continuously for:
   - Crashes or freezes
   - Memory leaks
   - Error accumulation
   - Performance degradation
   - Database growth

**Expected Results:**
- ✅ Application runs for full 24 hours without crashes
- ✅ All 50 videos processed successfully
- ✅ Memory usage stable (no continuous growth)
- ✅ CPU usage returns to idle between batches
- ✅ Database size reasonable (< 20 MB)
- ✅ Log files rotated properly
- ✅ No degradation in processing speed over time
- ✅ GUI remains responsive throughout
- ✅ Error count: 0 (or all handled gracefully)
- ✅ System tray icon functional throughout

**Pass/Fail:** ___________  
**Notes:** ___________________________________________

---

### TS-025: Documentation Accuracy - Setup
**Priority:** Critical  
**Environment:** Clean Install

**Steps:**
1. New user (tester unfamiliar with application)
2. Follow `SETUP.md` step-by-step
3. Document any:
   - Missing steps
   - Unclear instructions
   - Incorrect commands
   - Outdated information

**Expected Results:**
- ✅ User completes setup without external help
- ✅ All prerequisite links work
- ✅ Installation commands execute successfully
- ✅ Screenshots/examples match actual UI
- ✅ No ambiguous instructions
- ✅ Estimated time accurate (< 15 minutes)

**Pass/Fail:** ___________  
**Notes:** ___________________________________________

---

### TS-026: Documentation Accuracy - User Guide
**Priority:** High  
**Environment:** Normal Network (10 Mbps)

**Steps:**
1. New user follows `USER_GUIDE.md`
2. Complete tasks:
   - Configure monitored folder
   - Add custom upload template
   - Set active hours
   - Process first video
3. Document any confusion or errors

**Expected Results:**
- ✅ User completes all tasks successfully
- ✅ Configuration examples work as-is (copy-paste)
- ✅ Screenshots match current UI version
- ✅ All features documented
- ✅ No broken internal links
- ✅ Code snippets execute without modification

**Pass/Fail:** ___________  
**Notes:** ___________________________________________

---

### TS-027: Documentation Accuracy - Troubleshooting
**Priority:** High  
**Environment:** Normal Network (10 Mbps)

**Steps:**
1. Simulate 5 common issues from `TROUBLESHOOTING.md`:
   - Authentication failure
   - Download error (invalid URL)
   - Upload quota exceeded
   - FFmpeg not found
   - Database locked
2. Follow troubleshooting steps for each

**Expected Results:**
- ✅ All issues resolved using documented steps
- ✅ Diagnostic commands work correctly
- ✅ Solutions accurate and complete
- ✅ Emergency reset procedure works
- ✅ No issues missing from guide (found during UAT)

**Pass/Fail:** ___________  
**Notes:** ___________________________________________

---

### TS-028: Concurrent Users (Same Machine)
**Priority:** Low  
**Environment:** Normal Network (10 Mbps)

**Steps:**
1. Launch application as User A
2. Switch Windows user (Fast User Switching)
3. Launch application as User B
4. Test both instances simultaneously

**Expected Results:**
- ✅ Both instances run independently
- ✅ Separate databases (`data/` per user)
- ✅ Separate configurations
- ✅ No file locking conflicts
- ✅ No port conflicts (if applicable)
- ✅ Both system tray icons visible

**Pass/Fail:** ___________  
**Notes:** ___________________________________________

---

### TS-029: Edge Case - Empty Queue
**Priority:** Medium  
**Environment:** Normal Network (10 Mbps)

**Steps:**
1. Launch application with empty queue
2. Click "Start Processing"
3. Click "Pause All"
4. Click "Clear Queue"
5. Navigate all GUI tabs

**Expected Results:**
- ✅ No errors with empty queue
- ✅ Start button disabled or shows "Queue Empty"
- ✅ Pause button disabled
- ✅ Clear button disabled or shows warning
- ✅ Dashboard shows "No data" gracefully
- ✅ Queue tab shows empty state message

**Pass/Fail:** ___________  
**Notes:** ___________________________________________

---

### TS-030: Edge Case - Very Long Filenames
**Priority:** Low  
**Environment:** Normal Network (10 Mbps)

**Steps:**
1. Create video with 200-character filename
2. Add to monitored folder
3. Process video
4. Upload to YouTube

**Expected Results:**
- ✅ Filename detected and queued
- ✅ Download succeeds (filename truncated if needed)
- ✅ Upload succeeds with valid title
- ✅ File saved with legal Windows filename
- ✅ No path length errors (< 260 chars total)
- ✅ Database stores full metadata

**Pass/Fail:** ___________  
**Notes:** ___________________________________________

---

## Acceptance Criteria

### Critical Criteria (Must Pass All)
- [ ] **Installation:** Fresh install completes in < 15 minutes using `SETUP.md`
- [ ] **Authentication:** OAuth flow completes successfully
- [ ] **Download:** Videos download without corruption
- [ ] **Upload:** Videos upload to YouTube with correct metadata
- [ ] **Error Handling:** All errors handled gracefully (no crashes)
- [ ] **24-Hour Soak:** Application runs for 24 hours without crashes
- [ ] **Documentation:** Users complete tasks using docs alone

### High Priority Criteria (≥ 90% Pass Rate)
- [ ] **Queue Management:** All queue operations function correctly
- [ ] **Active Hours:** Scheduling works as configured
- [ ] **Network Resilience:** Recovers from connection loss
- [ ] **Resource Usage:** Idle < 50 MB RAM, Active < 200 MB RAM
- [ ] **GUI Responsiveness:** UI updates < 2 second delay
- [ ] **High DPI:** Scales correctly on 4K displays

### Medium Priority Criteria (≥ 80% Pass Rate)
- [ ] **Multiple Monitors:** Works correctly across monitors
- [ ] **Auto-start:** Registers/unregisters correctly
- [ ] **Logging:** Logs contain useful diagnostic information
- [ ] **Database:** Integrity maintained after forced exit
- [ ] **Concurrent Processing:** Handles 3+ simultaneous tasks

### Low Priority Criteria (≥ 70% Pass Rate)
- [ ] **Concurrent Users:** Multiple user profiles supported
- [ ] **Edge Cases:** Handles empty queues, long filenames gracefully

---

## Test Execution Checklist

### Pre-Testing
- [ ] Backup existing data (if applicable)
- [ ] Prepare test videos (various sizes and formats)
- [ ] Configure network throttling tools
- [ ] Install monitoring tools (Resource Monitor, Process Explorer)
- [ ] Create test YouTube channel (for uploads)
- [ ] Set up multiple user accounts (for concurrent testing)
- [ ] Prepare high DPI display / multiple monitors

### During Testing
- [ ] Execute test scenarios in order
- [ ] Document PASS/FAIL for each scenario
- [ ] Capture screenshots of issues
- [ ] Record error messages verbatim
- [ ] Note performance anomalies
- [ ] Save log files for failed tests
- [ ] Track time spent per scenario

### Post-Testing
- [ ] Compile issue list with severity ratings
- [ ] Calculate pass rates per priority
- [ ] Review acceptance criteria compliance
- [ ] Create UAT summary report
- [ ] Archive test evidence (screenshots, logs)
- [ ] Present findings to development team

---

## Issue Tracking

### Issue Template
```markdown
**Issue ID:** UAT-XXX  
**Scenario:** TS-XXX  
**Severity:** Critical / High / Medium / Low  
**Environment:** [OS, Network, DPI, etc.]  

**Description:**
[Clear description of the issue]

**Steps to Reproduce:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happened]

**Evidence:**
- Screenshot: [path/to/screenshot.png]
- Logs: [relevant log excerpt]
- Video: [if applicable]

**Workaround:**
[Temporary solution, if any]

**Proposed Fix:**
[Suggested solution]
```

### Severity Definitions
- **Critical:** Application crash, data loss, security vulnerability
- **High:** Major feature not working, severe performance issue
- **Medium:** Minor feature issue, cosmetic bug, unclear documentation
- **Low:** Enhancement request, typo, rare edge case

### Issue Log
| ID | Scenario | Severity | Status | Assigned To | Resolution |
|----|----------|----------|--------|-------------|------------|
| UAT-001 | TS-XXX | Critical | Open | - | - |
| UAT-002 | TS-XXX | High | Fixed | - | Patch v1.0.1 |
| ... | ... | ... | ... | ... | ... |

---

## Sign-off Requirements

### Stakeholder Approval

**Product Owner:**  
Name: ___________________  
Signature: _______________  
Date: ___________

**Development Lead:**  
Name: ___________________  
Signature: _______________  
Date: ___________

**QA Lead:**  
Name: ___________________  
Signature: _______________  
Date: ___________

### Acceptance Decision
- [ ] **APPROVED:** Application meets all critical acceptance criteria
- [ ] **APPROVED WITH RESERVATIONS:** Minor issues to be fixed in next release
- [ ] **REJECTED:** Critical issues must be resolved before release

**Comments:**  
_____________________________________________  
_____________________________________________  
_____________________________________________

---

## Appendix A: Test Data

### Test Videos
| Filename | Size | Duration | Resolution | Format | Purpose |
|----------|------|----------|------------|--------|---------|
| test_small.mp4 | 10 MB | 1 min | 720p | H.264 | Quick tests |
| test_medium.mp4 | 100 MB | 10 min | 1080p | H.264 | Normal tests |
| test_large.mp4 | 500 MB | 30 min | 1080p | H.264 | Stress tests |
| test_4k.mp4 | 1 GB | 10 min | 2160p | H.265 | High quality tests |
| test_long_filename_[200 chars].mp4 | 50 MB | 5 min | 720p | H.264 | Edge case tests |

### Test YouTube Videos (Public)
| Video ID | Title | Duration | Purpose |
|----------|-------|----------|---------|
| dQw4w9WgXcQ | Test Video 1 | 3:33 | Download test |
| jNQXAC9IVRw | Test Video 2 | 3:43 | Download test |

---

## Appendix B: Network Throttling

### Windows NetLimiter Configuration
```plaintext
Download: 0.5 Mbps (62.5 KB/s)
Upload: 0.5 Mbps (62.5 KB/s)
Latency: 100 ms
Packet Loss: 0%
```

### Router QoS Configuration
```plaintext
Device: [Application PC MAC Address]
Download Limit: 0.5 Mbps
Upload Limit: 0.5 Mbps
Priority: Low
```

---

## Appendix C: Monitoring Commands

### Resource Monitoring
```powershell
# Monitor CPU, RAM, Disk, Network
Get-Process "python" | Select-Object CPU, WorkingSet, Id

# Continuous monitoring (every 5 seconds)
while ($true) { 
    Get-Process "python" | Select-Object ProcessName, CPU, @{Name="RAM(MB)";Expression={[math]::round($_.WorkingSet/1MB,2)}}
    Start-Sleep 5 
}
```

### Database Integrity Check
```powershell
# SQLite integrity check
sqlite3 data/videos.db "PRAGMA integrity_check;"
```

### Log Analysis
```powershell
# Count errors in log
Select-String -Path "logs\errors.log" -Pattern "ERROR" | Measure-Object
```

---

**End of UAT Test Plan**
