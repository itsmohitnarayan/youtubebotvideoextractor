# YouTube API Quota Management Guide

Complete guide to understanding and managing YouTube Data API v3 quota limits.

---

## Table of Contents

1. [Understanding YouTube API Quotas](#understanding-youtube-api-quotas)
2. [Quota Costs by Operation](#quota-costs-by-operation)
3. [Daily Quota Limit](#daily-quota-limit)
4. [Quota Calculation Examples](#quota-calculation-examples)
5. [Monitoring Quota Usage](#monitoring-quota-usage)
6. [Quota Optimization Strategies](#quota-optimization-strategies)
7. [Handling Quota Exceeded](#handling-quota-exceeded)
8. [Increasing Quota Limits](#increasing-quota-limits)

---

## Understanding YouTube API Quotas

### What is a Quota?

YouTube Data API v3 uses a **quota system** to manage API usage. Each API request consumes a certain number of "units" from your daily quota.

### Default Quota

- **10,000 units per day** (free tier)
- Resets at **midnight Pacific Time (PT)**
- Shared across all API calls for your project

### Why Quotas Exist

- Prevent API abuse
- Ensure fair usage across all users
- Protect YouTube infrastructure
- Encourage efficient API usage

---

## Quota Costs by Operation

### Read Operations (Low Cost)

| Operation | Cost | Description |
|-----------|------|-------------|
| **channels.list** | 1 | Get channel information |
| **playlists.list** | 1 | List playlists |
| **playlistItems.list** | 1 | Get playlist videos |
| **search.list** | 100 | Search for videos/channels |
| **videos.list** | 1 | Get video details |

### Write Operations (High Cost)

| Operation | Cost | Description |
|-----------|------|-------------|
| **videos.insert** | **1,600** | Upload a video 🔴 |
| **videos.update** | 50 | Update video metadata |
| **thumbnails.set** | 50 | Set custom thumbnail |
| **videos.delete** | 50 | Delete a video |
| **playlists.insert** | 50 | Create a playlist |
| **playlists.update** | 50 | Update playlist |

### **⚠️ Video Upload = 1,600 units!**

This is the most expensive operation and will be your primary quota consumer.

---

## Daily Quota Limit

### Maximum Videos Per Day

With 10,000 units daily quota:

```
Max uploads = 10,000 ÷ 1,600 = 6.25 videos/day
```

**Realistically: 5-6 videos/day maximum**

### Quota Breakdown Example

Uploading **1 video** with this application consumes:

| Operation | Units | Purpose |
|-----------|-------|---------|
| search.list | 100 | Find new videos on channel |
| videos.list | 1 | Get video details |
| videos.insert | 1,600 | Upload video |
| thumbnails.set | 50 | Set custom thumbnail |
| **TOTAL** | **1,751** | Per video workflow |

**With 10,000 units: ~5 videos/day**

---

## Quota Calculation Examples

### Example 1: Light Usage (1 video/day)

**Configuration**:
- Check every 15 minutes (96 checks/day)
- Upload 1 video

**Daily consumption**:
```
Monitoring: 96 checks × 100 units = 9,600 units
Upload: 1 video × 1,750 units = 1,750 units (over quota!)
```

**Problem**: Monitoring alone uses 96% of quota!

**Solution**: Reduce monitoring frequency or use webhooks (not available for all users)

### Example 2: Optimized Usage (3 videos/day)

**Configuration**:
- Check every 30 minutes (48 checks/day)
- Upload 3 videos

**Daily consumption**:
```
Monitoring: 48 checks × 100 units = 4,800 units
Uploads: 3 videos × 1,750 units = 5,250 units
TOTAL: 10,050 units (slightly over)
```

**Status**: At limit, may need to skip some monitoring checks

### Example 3: Production Usage (5 videos/day)

**Configuration**:
- Check every 2 hours (12 checks/day)
- Upload 5 videos

**Daily consumption**:
```
Monitoring: 12 checks × 100 units = 1,200 units
Uploads: 5 videos × 1,750 units = 8,750 units
TOTAL: 9,950 units
```

**Status**: ✅ Within quota with 50 units buffer

---

## Monitoring Quota Usage

### In Application

The application tracks quota automatically:

```json
// Check logs/app.log
INFO: Quota usage: 1650/10000 units (16.5%)
WARNING: Quota usage: 8000/10000 units (80%) - Approaching limit
ERROR: Quota exceeded: 10000/10000 units (100%)
```

### Quota Warnings

| Threshold | Action |
|-----------|--------|
| **80%** | ⚠️ Warning logged |
| **95%** | 🛑 Monitoring pauses |
| **100%** | 🚫 All API calls blocked |

### Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. **APIs & Services** → **Dashboard**
3. Click **YouTube Data API v3**
4. View **Quotas** tab

Shows:
- Current usage
- Historical usage (graphs)
- Quota limit
- Time until reset

---

## Quota Optimization Strategies

### 1. Reduce Monitoring Frequency ⏱️

**Default: Every 10 minutes**
```json
{
  "monitoring": {
    "check_interval_minutes": 10
  }
}
```

**Optimized: Every 30 minutes**
```json
{
  "monitoring": {
    "check_interval_minutes": 30  // 66% reduction in API calls!
  }
}
```

**Impact**:
- 10 min: 144 checks/day × 100 = 14,400 units ❌ (over quota)
- 30 min: 48 checks/day × 100 = 4,800 units ✅

### 2. Use Active Hours 🕐

Only monitor during specific hours:

```json
{
  "active_hours": {
    "enabled": true,
    "start": "09:00",  // 9 AM
    "end": "21:00"     // 9 PM
  },
  "monitoring": {
    "check_interval_minutes": 15
  }
}
```

**Impact**:
- 24 hours: 96 checks/day × 100 = 9,600 units
- 12 hours: 48 checks/day × 100 = 4,800 units ✅ (50% reduction)

### 3. Limit Videos Per Check 📹

```json
{
  "monitoring": {
    "max_videos_per_check": 3  // Instead of 5
  }
}
```

**Impact**:
- Reduces processing load
- Faster API responses
- Lower quota risk per check

### 4. Use Catch-Up Mechanism 📅

Instead of frequent checks, use a daily catch-up:

```json
{
  "monitoring": {
    "check_interval_minutes": 120,  // Every 2 hours
    "lookback_hours": 24,
    "max_videos_per_check": 10
  }
}
```

**Impact**:
- 12 checks/day × 100 = 1,200 units (vs 14,400)
- Catches up on missed videos
- More quota available for uploads

### 5. Batch Video Details 📦

Instead of calling `videos.list` for each video individually, batch them:

```python
# Bad: 5 API calls (5 units)
for video_id in video_ids:
    video = api.videos().list(id=video_id, part='snippet').execute()

# Good: 1 API call (1 unit)
videos = api.videos().list(id=','.join(video_ids), part='snippet').execute()
```

**Impact**: Up to 5x reduction in quota for video details

### 6. Minimize Parts Requested 🎯

Only request needed information:

```python
# Bad: Requests everything (higher cost)
part='snippet,contentDetails,statistics,status'

# Good: Only what's needed
part='snippet,status'
```

**Impact**: 10-20% quota reduction

### 7. Cache Video Metadata 💾

Store video details in database instead of re-fetching:

```python
# Check database first
video = db.get_video(video_id)
if not video:
    # Only call API if not cached
    video = api.videos().list(id=video_id).execute()
    db.save_video(video)
```

**Impact**: Eliminates duplicate API calls

---

## Handling Quota Exceeded

### What Happens When Quota is Exceeded?

1. API returns `403 Forbidden` error:
   ```
   "quotaExceeded": "The request cannot be completed because you have exceeded your quota."
   ```

2. Application behavior:
   - ✅ Logs error
   - ✅ Pauses monitoring
   - ✅ Queues videos for tomorrow
   - ✅ Shows notification to user
   - ✅ Resumes at midnight PT

### Recovery Actions

**Automatic (Built-in)**:
- Application detects quota exceeded
- Pauses all API calls
- Waits for quota reset (midnight PT)
- Automatically resumes

**Manual**:
```powershell
# Check when quota resets
python -c "from datetime import datetime, timezone; import pytz; print('Next reset:', datetime.now(pytz.timezone('US/Pacific')).replace(hour=0, minute=0, second=0, microsecond=0))"
```

### Emergency Strategies

If you must continue:

1. **Use backup Google Cloud project**:
   - Create new project
   - Enable YouTube API
   - New 10,000 units quota
   - Switch `client_secrets.json`

2. **Request quota increase** (see next section)

---

## Increasing Quota Limits

### When to Request an Increase

- Uploading >5 videos/day regularly
- Business/commercial use case
- Well-established channel
- Legitimate high-volume need

### How to Request Increase

1. **Optimize first**: Follow all optimization strategies above

2. **Go to Quotas page**:
   - [Google Cloud Console](https://console.cloud.google.com)
   - **APIs & Services** → **Enabled APIs**
   - **YouTube Data API v3** → **Quotas**

3. **Click "APPLY FOR HIGHER QUOTA"**

4. **Fill out form**:
   - Explain use case
   - Show optimization efforts
   - Demonstrate legitimate need
   - Provide channel information

5. **Wait for approval** (1-2 weeks)

### Approval Tips

✅ **Good reasons**:
- "Automated backup of 20+ educational videos/day"
- "Multi-channel content migration project"
- "Business content distribution system"

❌ **Poor reasons**:
- "I want to upload more videos"
- "I didn't optimize my code"
- "I'm reuploading someone else's content"

### Typical Quota Increases

- **Standard increase**: 1,000,000 units/day
- **With justification**: 10,000,000+ units/day
- **YouTube Partner** verified channels may get higher limits

---

## Best Practices Summary

### ✅ DO:

1. **Monitor quota usage** in real-time
2. **Use active hours** to limit monitoring
3. **Increase check interval** (30+ minutes)
4. **Batch API requests** when possible
5. **Cache video metadata** in database
6. **Request only needed parts**
7. **Handle quota exceeded** gracefully
8. **Plan uploads** based on quota availability

### ❌ DON'T:

1. **Call API unnecessarily** (check cache first)
2. **Monitor 24/7** if not needed
3. **Use 10-minute intervals** (too frequent)
4. **Request all video parts** (only get what you need)
5. **Ignore quota warnings** (80% threshold)
6. **Upload without checking quota** first
7. **Make duplicate API calls** for same data

---

## Quota-Aware Configuration Examples

### Conservative (2-3 videos/day)

```json
{
  "monitoring": {
    "enabled": true,
    "check_interval_minutes": 60,
    "max_videos_per_check": 3,
    "lookback_hours": 24
  },
  "active_hours": {
    "enabled": true,
    "start": "08:00",
    "end": "22:00"
  },
  "quota": {
    "warn_at_percent": 80,
    "pause_at_percent": 95
  }
}
```

**Expected quota**: ~3,000 units/day

### Balanced (4-5 videos/day)

```json
{
  "monitoring": {
    "enabled": true,
    "check_interval_minutes": 120,
    "max_videos_per_check": 5,
    "lookback_hours": 48
  },
  "active_hours": {
    "enabled": true,
    "start": "06:00",
    "end": "23:00"
  }
}
```

**Expected quota**: ~9,000 units/day

### Aggressive (5-6 videos/day) - Requires increased quota

```json
{
  "monitoring": {
    "enabled": true,
    "check_interval_minutes": 180,
    "max_videos_per_check": 10,
    "lookback_hours": 72
  },
  "active_hours": {
    "enabled": false
  }
}
```

**Expected quota**: ~10,500 units/day (exceeds default)

---

## Monitoring Dashboard

The application provides a quota dashboard:

### System Tray Icon

- 🟢 **Green**: <50% quota used
- 🟡 **Yellow**: 50-80% quota used
- 🟠 **Orange**: 80-95% quota used
- 🔴 **Red**: >95% quota used or exceeded

### Main Window Stats

```
Quota Usage Today
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Used: 7,250 units
Limit: 10,000 units
Remaining: 2,750 units (27.5%)

Videos uploaded today: 4
Quota per upload: ~1,812 units
Can upload: 1 more video
Resets in: 7h 23m
```

---

## Emergency Quota Reset

If you absolutely must reset quota immediately (not recommended):

### Option 1: Create New Project

1. Create new Google Cloud project
2. Enable YouTube Data API v3
3. Create new OAuth credentials
4. Update `client_secrets.json`
5. Re-authenticate

**New quota**: Fresh 10,000 units

### Option 2: Use Multiple Projects

Rotate between multiple projects (not recommended for production):

```json
{
  "api": {
    "projects": [
      "project1_client_secrets.json",
      "project2_client_secrets.json",
      "project3_client_secrets.json"
    ],
    "rotate_on_quota_exceeded": true
  }
}
```

**Total quota**: 30,000 units/day across 3 projects

**⚠️ Warning**: May violate YouTube TOS if abused

---

## Frequently Asked Questions

### Q: Can I pay to increase quota?

**A**: No, YouTube API quotas are not for sale. You must request an increase with justification.

### Q: When exactly does quota reset?

**A**: Midnight Pacific Time (PT/PST/PDT), regardless of your location.

### Q: Does quota reset immediately?

**A**: Usually within 1-2 minutes of midnight PT. Sometimes takes up to 5 minutes.

### Q: Can I see historical quota usage?

**A**: Yes, in [Google Cloud Console](https://console.cloud.google.com) → APIs & Services → Dashboard → YouTube Data API v3 → Quotas

### Q: What counts as "exceeded" vs "approaching limit"?

**A**: 
- **80%**: Warning ⚠️
- **95%**: Pause monitoring 🛑
- **100%**: Exceeded, all calls fail 🚫

### Q: Can I request quota increase for personal use?

**A**: Yes, but justify your need. Personal backups of your own content are usually approved.

### Q: Does deleting videos refund quota?

**A**: No, quota is consumed on API call, not refunded on delete.

### Q: Can multiple apps share the same quota?

**A**: Yes, all apps using the same Google Cloud project share the quota.

---

## Resources

- **Official Quota Documentation**: https://developers.google.com/youtube/v3/getting-started#quota
- **Quota Calculator**: https://developers.google.com/youtube/v3/determine_quota_cost
- **Google Cloud Console**: https://console.cloud.google.com
- **YouTube API Forum**: https://support.google.com/youtube/community

---

**Last Updated**: November 10, 2025  
**Version**: 1.0.0  
**API Version**: YouTube Data API v3
