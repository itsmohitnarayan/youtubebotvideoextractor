# Real YouTube API Integration Tests

These tests interact with the actual YouTube Data API v3, not mocked versions.

## ⚠️ Important Notes

- **These tests require valid YouTube API credentials**
- **They consume API quota** (be mindful of daily limits)
- **They are SLOW** (involve network calls and file operations)
- **Upload tests create and delete actual videos** on your YouTube channel

## Prerequisites

1. **Valid Credentials**:
   - `client_secrets.json` in project root (OAuth2 credentials from Google Cloud Console)
   - `token.json` in project root (run `python refresh_oauth.py` to generate)

2. **Test Video File**:
   - Place a small test video at `tests/fixtures/test_video.mp4`
   - Recommended: < 10MB, short duration (10-30 seconds)
   - Will be uploaded as PRIVATE and immediately deleted

3. **Internet Connection**: Required for API calls

4. **API Quota**: Daily limit is 10,000 units
   - Each test run uses approximately 50-200 units
   - Upload test uses 1,600 units per video

## Running Tests

### Run all real API tests:
```bash
pytest tests/test_youtube_api_real.py -v -s
```

### Run specific test class:
```bash
# Test only API client
pytest tests/test_youtube_api_real.py::TestRealYouTubeAPIClient -v

# Test only uploader
pytest tests/test_youtube_api_real.py::TestRealYouTubeUploader -v

# Test only monitor
pytest tests/test_youtube_api_real.py::TestRealChannelMonitor -v
```

### Run tests except slow ones:
```bash
pytest tests/ -v -m "not slow"
```

### Run only integration tests:
```bash
pytest tests/ -v -m integration
```

## Test Coverage

### ✅ TestRealYouTubeAPIClient
- API client initialization with real OAuth credentials
- Quota tracking and persistence
- Channel info retrieval
- Uploads playlist retrieval
- Recent videos fetching
- Quota limit checks

### ✅ TestRealYouTubeUploader
- **Upload real video** (PRIVATE, auto-deleted)
- Upload failure with invalid file
- Quota exhaustion handling
- Error message capturing

### ✅ TestRealChannelMonitor
- Monitor real YouTube channel
- Detect new videos
- Database integration

### ✅ TestRealDownloader
- Download real video from YouTube
- File validation
- Thumbnail download

### ✅ TestEndToEndWorkflow
- Quota persistence across sessions
- Error logging to database
- Complete workflow validation

## Markers

Tests use pytest markers for categorization:

- `@pytest.mark.slow` - Tests that take >5 seconds
- `@pytest.mark.requires_credentials` - Tests needing valid YouTube credentials
- `@pytest.mark.integration` - Integration tests with external services

## Expected Quota Usage

| Test | Quota Cost | Notes |
|------|-----------|-------|
| test_get_channel_info | 1 unit | Read operation |
| test_get_recent_uploads | 1 unit | Playlist read |
| test_upload_video_private | 1,600 units | Upload + delete |
| test_check_for_new_videos | 1-100 units | Depends on results |
| test_download_real_video | 0 units | No API calls |

**Total per full run: ~1,700 units** (17% of daily quota)

## Troubleshooting

### "client_secrets.json not found"
- Download OAuth2 credentials from Google Cloud Console
- Place in project root directory
- Ensure filename is exactly `client_secrets.json`

### "token.json not found"
- Run: `python refresh_oauth.py`
- Complete OAuth flow in browser
- Token will be saved to `token.json`

### "Insufficient quota for upload test"
- You've exceeded daily quota limit (10,000 units)
- Wait until midnight Pacific Time for reset
- Or run tests without upload: `pytest -v -k "not upload"`

### "Test video not found"
- Create `tests/fixtures/` directory
- Add a small video file named `test_video.mp4`
- Any valid video format works (MP4 recommended)

### Upload test fails but video not deleted
- Check YouTube Studio → Content
- Manually delete test videos (title starts with "[TEST]")
- Test video IDs are printed in console output

## CI/CD Integration

These tests should be run separately from unit tests:

```yaml
# .github/workflows/integration-tests.yml
name: Integration Tests
on:
  schedule:
    - cron: '0 2 * * *'  # Run nightly
  workflow_dispatch:  # Manual trigger

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - name: Install dependencies
        run: pip install -r requirements-dev.txt
      - name: Setup credentials
        env:
          CLIENT_SECRETS: ${{ secrets.YOUTUBE_CLIENT_SECRETS }}
          TOKEN: ${{ secrets.YOUTUBE_TOKEN }}
        run: |
          echo "$CLIENT_SECRETS" > client_secrets.json
          echo "$TOKEN" > token.json
      - name: Run integration tests
        run: pytest tests/test_youtube_api_real.py -v
```

## Best Practices

1. **Run locally before committing** - Don't waste CI quota
2. **Use separate test account** - Don't pollute production channel
3. **Monitor quota usage** - Check Google Cloud Console regularly
4. **Keep test videos small** - Faster uploads, less bandwidth
5. **Clean up failed tests** - Manually delete any leftover test videos

## Safety Features

- All uploads are **PRIVATE** by default
- Test videos are **auto-deleted** after verification
- Video titles are prefixed with **[TEST]** for easy identification
- Timestamp included in title for debugging
- Tests skip gracefully if credentials missing
- Quota checks before expensive operations

## Example Output

```
tests/test_youtube_api_real.py::TestRealYouTubeUploader::test_upload_video_private 
✅ Successfully uploaded test video: dQw4w9WgXcQ
✅ Verified video exists on YouTube
✅ Cleaned up test video: dQw4w9WgXcQ
PASSED
```

## Contributing

When adding new real API tests:
1. Add appropriate markers (`@pytest.mark.slow`, etc.)
2. Include cleanup logic (delete uploaded videos)
3. Use PRIVATE privacy status for uploads
4. Document quota cost in docstring
5. Add skip conditions for missing credentials
6. Print helpful progress messages

## References

- [YouTube Data API v3 Documentation](https://developers.google.com/youtube/v3)
- [API Quota Documentation](https://developers.google.com/youtube/v3/determine_quota_cost)
- [OAuth 2.0 Setup Guide](https://developers.google.com/youtube/v3/guides/auth/server-side-web-apps)
