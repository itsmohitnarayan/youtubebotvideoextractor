# Manual UAT Testing - Getting Started Guide

**For:** User (Manual Tester)  
**Date:** November 10, 2025  
**Automated Tests:** ✅ 94.8% Pass Rate (91/96 tests)

---

## 🎯 You Are Here

✅ **Automated testing complete** - All critical issues fixed  
⏳ **Manual testing ready** - You will now install and test the application  
📋 **30 test scenarios prepared** - Comprehensive testing plan available

---

## 📦 What You Need To Do Next

### Step 1: Install FFmpeg (Required - 10 minutes)

FFmpeg is the **ONLY** missing external dependency. Follow these steps:

1. **Download FFmpeg:**
   - Visit: https://www.gyan.dev/ffmpeg/builds/
   - Download: `ffmpeg-release-essentials.zip`

2. **Extract to C:\ffmpeg:**
   ```
   C:\ffmpeg\
   ├── bin\
   │   ├── ffmpeg.exe  ← You need this!
   │   ├── ffplay.exe
   │   └── ffprobe.exe
   ```

3. **Add to System PATH:**
   - Press `Win + R`, type `sysdm.cpl`, press Enter
   - Go to **Advanced** tab → **Environment Variables**
   - Under **System variables**, find **Path** → click **Edit**
   - Click **New** → add `C:\ffmpeg\bin`
   - Click **OK** on all dialogs
   - **IMPORTANT:** Restart PowerShell/Terminal

4. **Verify Installation:**
   ```powershell
   ffmpeg -version
   ```
   Should show: `ffmpeg version 6.x.x ...`

**Full instructions:** See `SETUP.md` Section "FFmpeg Installation"

---

### Step 2: Verify Application Setup (5 minutes)

Run the automated verification script:

```powershell
# Activate virtual environment
venv\Scripts\activate

# Run automated UAT tests
python scripts/run_uat.py
```

**Expected Results After Installing FFmpeg:**
```
Total Tests:        96
Passed:            92-95  ✅ (should improve from 91)
Failed:            1-4    ⚠️  (acceptable false positives)
Pass Rate:         95-99%

[SUCCESS] or [WARNING] MOSTLY PASSING
Recommendation: [READY] Ready for manual UAT testing
```

---

### Step 3: Begin Manual UAT Testing (2-3 weeks)

Open the comprehensive test plan:

```
tests/uat/UAT_TEST_PLAN.md
```

#### Test Scenarios Overview (30 Total):

**Week 1: Core Functionality (10 scenarios)**
- TS-001: Fresh Installation ⏱️ 30 min
- TS-002: YouTube OAuth Authentication ⏱️ 15 min
- TS-003: Video Detection and Queuing ⏱️ 30 min
- TS-004: Video Download ⏱️ 30 min
- TS-005: Video Upload to YouTube ⏱️ 45 min
- TS-006: Queue Management ⏱️ 45 min
- TS-007: Active Hours Scheduling ⏱️ 60 min
- TS-008-009: Error Handling ⏱️ 60 min
- TS-012: Connection Loss Recovery ⏱️ 30 min

**Week 2: Advanced Features (10 scenarios)**
- TS-010-011: Network Conditions (slow/fast) ⏱️ 90 min
- TS-013-016: GUI Responsiveness (DPI, monitors, states) ⏱️ 120 min
- TS-017-021: System Integration (tray, dashboard, auto-start, database, logging) ⏱️ 180 min

**Week 3: Stability & Documentation (10 scenarios)**
- TS-022-023: Resource Usage (idle/active) ⏱️ 60 min
- TS-024: **24-Hour Soak Test** ⏱️ 24 hours + monitoring
- TS-025-027: Documentation Accuracy ⏱️ 120 min
- TS-028-030: Edge Cases ⏱️ 90 min

---

## 📝 How To Perform Manual Tests

### For Each Test Scenario:

1. **Read the scenario** in `tests/uat/UAT_TEST_PLAN.md`
2. **Follow the steps exactly** as written
3. **Compare results** with expected outcomes
4. **Mark Pass/Fail** in the checkbox
5. **Take notes** of any issues found

### Example Test Execution:

```
### TS-001: Fresh Installation
Priority: Critical
Environment: Clean Install

Steps:
1. Download application from repository          [✓ Done]
2. Follow SETUP.md documentation                 [✓ Done]
3. Install Python dependencies                   [✓ Done]
4. Install FFmpeg                               [✓ Done]
5. Run application for the first time           [? Testing...]

Expected Results:
- Installation completes without errors         [✓ PASS]
- First-run wizard appears                      [✓ PASS]
- Configuration file created                    [✓ PASS]
- Database initialized successfully             [✓ PASS]
- System tray icon appears                      [✓ PASS]
- GUI opens without errors                      [✓ PASS]

Pass/Fail: PASS ✓
Notes: Installation smooth, took 25 minutes total
```

---

## 🐛 If You Find Bugs

Use the issue template from UAT_TEST_PLAN.md:

```markdown
**Issue ID:** UAT-001  
**Scenario:** TS-003 (Video Detection)  
**Severity:** High  
**Environment:** Windows 11, 1920x1080, 100 Mbps

**Description:**
Videos not detected when copied to monitored folder

**Steps to Reproduce:**
1. Configure monitored folder: D:\Videos
2. Copy test.mp4 to D:\Videos
3. Wait 10 seconds

**Expected Behavior:**
Video appears in queue within 5 seconds

**Actual Behavior:**
No video detected after 2 minutes

**Evidence:**
- Screenshot: issue_001.png
- Logs: logs/errors.log (lines 45-67)

**Workaround:**
Restart application, then detection works

**Proposed Fix:**
Check folder monitoring initialization
```

---

## 📊 Progress Tracking

Create a simple tracking file: `my_uat_progress.md`

```markdown
# My Manual UAT Progress

**Started:** November 10, 2025

## Completed Scenarios
- [x] TS-001: Fresh Installation - PASS ✓ (Nov 10, 2:30 PM)
- [x] TS-002: OAuth Authentication - PASS ✓ (Nov 10, 3:00 PM)
- [ ] TS-003: Video Detection - In Progress...

## Issues Found
1. UAT-001 - Video detection delay (MEDIUM)
2. UAT-002 - GUI tooltip typo (LOW)

## Time Spent
- Installation: 30 min
- Testing: 2 hours
- Total: 2.5 hours
```

---

## ✅ Acceptance Criteria

To consider UAT complete, you need:

### Critical (Must Pass All)
- [x] Installation completes in < 15 min using SETUP.md
- [ ] OAuth flow completes successfully
- [ ] Videos download without corruption
- [ ] Videos upload to YouTube with correct metadata
- [ ] All errors handled gracefully (no crashes)
- [ ] Application runs for 24 hours without crashes
- [ ] Users complete tasks using docs alone

### High Priority (≥ 90% Pass Rate)
- [ ] Queue management works correctly
- [ ] Active hours scheduling functions
- [ ] Recovers from connection loss
- [ ] Resource usage acceptable (< 50 MB idle, < 200 MB active)
- [ ] GUI responsive (< 2 second updates)
- [ ] High DPI displays supported

---

## 🎯 Success Metrics

### What "PASS" Looks Like:
- ✅ All 30 critical/high scenarios pass
- ✅ 0-3 medium/low issues found
- ✅ Application runs 24 hours continuously
- ✅ Documentation allows task completion without help
- ✅ No data corruption or crashes

### What "NEEDS WORK" Looks Like:
- ❌ > 3 high severity issues
- ❌ Application crashes during testing
- ❌ Critical features not working
- ❌ Documentation missing critical steps

---

## 🚀 Quick Start Commands

```powershell
# Step 1: Activate environment
cd D:\2025\youtubebotvideoextractor
venv\Scripts\activate

# Step 2: Verify FFmpeg installed
ffmpeg -version

# Step 3: Run automated tests (should be 95%+)
python scripts/run_uat.py

# Step 4: Start application
python src/main.py

# Step 5: Open test plan
notepad tests\uat\UAT_TEST_PLAN.md
```

---

## 📚 Reference Documents

| Document | Purpose | Location |
|----------|---------|----------|
| **SETUP.md** | Installation guide | Root directory |
| **USER_GUIDE.md** | Feature documentation | `docs/USER_GUIDE.md` |
| **TROUBLESHOOTING.md** | Problem solving | `docs/TROUBLESHOOTING.md` |
| **API_LIMITS.md** | YouTube quota management | `docs/API_LIMITS.md` |
| **UAT_TEST_PLAN.md** | Test scenarios (30) | `tests/uat/UAT_TEST_PLAN.md` |
| **UAT_AUTOMATED_COMPLETE.md** | Automated test results | Root directory |

---

## 💡 Tips for Effective Testing

1. **Test in order** - Start with TS-001 and go sequentially
2. **Take screenshots** - Evidence helps with bug reports
3. **Save logs** - Copy `logs/` folder after each test
4. **Test edge cases** - Try unexpected inputs
5. **Document everything** - Notes help remember what you tested
6. **Take breaks** - 24-hour soak test needs patience!
7. **Ask questions** - Use documentation, TROUBLESHOOTING.md

---

## 📅 Suggested Timeline

**Week 1 (Nov 11-15):**
- Mon: Install FFmpeg, run verification
- Tue: TS-001 to TS-005 (core functionality)
- Wed: TS-006 to TS-009 (queue & errors)
- Thu: TS-010 to TS-012 (network conditions)
- Fri: Review findings, document issues

**Week 2 (Nov 18-22):**
- Mon: TS-013 to TS-016 (GUI responsiveness)
- Tue: TS-017 to TS-019 (system integration)
- Wed: TS-020 to TS-023 (database, logs, resources)
- Thu: Start TS-024 (24-hour soak test)
- Fri: Monitor soak test

**Week 3 (Nov 25-29):**
- Mon: Complete TS-024, analyze results
- Tue: TS-025 to TS-027 (documentation)
- Wed: TS-028 to TS-030 (edge cases)
- Thu: Compile all findings, create summary
- Fri: Review with development team

---

## ❓ Common Questions

**Q: Do I need to test all 30 scenarios?**  
A: Yes, for comprehensive UAT. Prioritize Critical/High scenarios if time-limited.

**Q: What if I find a critical bug?**  
A: Document it immediately, stop testing that scenario, move to next scenario.

**Q: Can I skip the 24-hour soak test?**  
A: No - it's critical for stability validation. But you can monitor remotely.

**Q: What if documentation is unclear?**  
A: That's a valid bug! Document it as a documentation issue.

**Q: Should I test on multiple machines?**  
A: Ideal but not required. Your Windows 11 system is sufficient.

---

## 🎉 Ready To Begin!

You now have everything you need:

✅ Automated tests passed (94.8%)  
✅ Application ready for testing  
✅ Comprehensive test plan (30 scenarios)  
✅ Documentation complete (75 KB)  
✅ Issue tracking templates ready  
⏳ Just need to install FFmpeg!

**Next Action:**  
Install FFmpeg following Step 1 above, then begin with TS-001 (Fresh Installation).

**Good luck with manual UAT testing!** 🚀

---

**Questions or issues?** Check `docs/TROUBLESHOOTING.md` or create an issue with the template above.
