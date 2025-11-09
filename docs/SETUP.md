# YouTube Bot Video Extractor - Setup Guide

## Prerequisites

- **Operating System**: Windows 10/11 (64-bit)
- **Python**: 3.11 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 500MB for application + space for downloads
- **Internet**: Broadband connection required

## Installation Steps

### 1. Install Python

1. Download Python 3.11+ from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **Important**: Check "Add Python to PATH" during installation
4. Verify installation:
   ```powershell
   python --version
   ```

### 2. Clone or Download Repository

```powershell
git clone https://github.com/itsmohitnarayan/youtubebotvideoextractor.git
cd youtubebotvideoextractor
```

### 3. Run Setup Script

```powershell
.\scripts\setup_env.ps1
```

This will:
- Create virtual environment
- Install all dependencies
- Create necessary directories
- Copy configuration templates

### 4. Configure YouTube API Credentials

#### 4.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **YouTube Data API v3**:
   - Navigate to "APIs & Services" → "Library"
   - Search for "YouTube Data API v3"
   - Click "Enable"

#### 4.2 Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Configure consent screen if prompted
4. Application type: **Desktop app**
5. Download credentials as `client_secrets.json`
6. Place file in project root directory

### 5. Configure Application Settings

#### 5.1 Edit `.env` file

```env
YOUTUBE_CLIENT_SECRETS_FILE=client_secrets.json
YOUTUBE_TOKEN_FILE=oauth_token.json
LOG_LEVEL=INFO
ACTIVE_START=10:00
ACTIVE_END=22:00
```

#### 5.2 Edit `config.json`

```json
{
  "target_channel": {
    "channel_id": "UC_YOUR_TARGET_CHANNEL_ID"
  },
  "active_hours": {
    "start": "10:00",
    "end": "22:00"
  },
  "download": {
    "directory": "downloads"
  }
}
```

**To find Channel ID:**
1. Go to target YouTube channel
2. View page source (Ctrl+U)
3. Search for "channelId"
4. Copy the ID (starts with "UC")

### 6. First Run

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run application
python src/main.py
```

On first run, a browser window will open for OAuth authentication:
1. Sign in to your YouTube account
2. Grant requested permissions
3. Token will be saved to `oauth_token.json`

## Troubleshooting

### Python not found
- Ensure Python is added to PATH
- Restart terminal after installing Python

### Module import errors
- Make sure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### OAuth authentication fails
- Check `client_secrets.json` is valid
- Ensure YouTube Data API v3 is enabled
- Try deleting `oauth_token.json` and re-authenticating

### API quota exceeded
- Default quota: 10,000 units/day
- Request quota increase from Google Cloud Console
- Reduce check frequency in config

## Next Steps

- See [USER_GUIDE.md](USER_GUIDE.md) for usage instructions
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues

## Support

For issues and questions:
- GitHub Issues: https://github.com/itsmohitnarayan/youtubebotvideoextractor/issues
- Documentation: [docs/](docs/)
