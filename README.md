# YouTube Bot Video Extractor

A Windows desktop application that automatically monitors a YouTube channel, downloads newly uploaded videos with thumbnails and metadata, and re-uploads them to your channel within a 15-minute window.

## 📊 Project Status

**Current Phase:** Phase 5 - Testing & Optimization  
**Project Progress:** 90% (5 of 6 phases complete)

```
Phase 0: Setup & Foundation          ✅ 100% COMPLETE
Phase 1: Core Backend Logic          ✅ 100% COMPLETE (102 tests passing)
Phase 2: YouTube Integration         ✅ 100% COMPLETE (1,190 lines)
Phase 3: GUI Development             ✅ 100% COMPLETE (1,183 lines)
Phase 4: System Integration          ✅ 100% COMPLETE (Event Bus, Queue, Workers)
Phase 5: Testing & Optimization      ⏳ 90% Complete (UAT automated ✅, manual UAT in progress)
Phase 6: Packaging & Deployment      ⏳ Pending
```

### Recent Milestones
- ✅ **Automated UAT Complete** (Nov 10, 2025) - 94.8% pass rate (91/96 tests)
- ✅ **Security Fixes Applied** (Nov 10, 2025) - HTTPS enforcement, path validation
- ✅ **Database Schema Initialized** (Nov 10, 2025) - 4 tables, full integrity
- ✅ **Phase 5 User Documentation Complete** (Nov 10, 2025) - 75KB across 5 docs
- ✅ **Phase 5 Security Audit Complete** (Nov 10, 2025) - 0 Critical/High issues
- ✅ **Phase 5 Performance Profiling** (Nov 10, 2025) - All targets exceeded
  - Startup: 0.002s (target: <3s) - 1500x better ⚡
  - Memory: 26MB (target: <150MB) - 5.7x better 💾
  - CPU: 0% idle (target: <5%) - Optimal ✨
- ✅ **211 Tests Passing** - Unit, Integration, & Workflow tests

See [**UAT_AUTOMATED_COMPLETE.md**](UAT_AUTOMATED_COMPLETE.md) for automated testing details.

## ⚠️ Legal Disclaimer

**This software is provided for legitimate content management purposes only.**

- ✅ Use ONLY with **explicit permission** from the content owner
- ✅ Comply with **YouTube's Terms of Service**
- ✅ Respect **copyright laws** and intellectual property rights
- ⚠️ Misuse may result in account termination, DMCA claims, or legal action

**By using this software, you acknowledge that you are solely responsible for ensuring you have the legal right to download and re-upload content.**

---

## 🚀 Features

- **Automated Monitoring**: Checks target channel every 10 minutes (configurable)
- **Fast Replication**: Downloads and uploads within 15 minutes of source publication
- **Active Hours Support**: Operates only during specified hours (e.g., 10 AM - 10 PM)
- **Catch-up Mechanism**: Processes videos uploaded during downtime
- **System Tray Application**: Minimizes to tray, non-intrusive operation
- **Metadata Preservation**: Copies title, description, tags, and thumbnail
- **Progress Tracking**: Real-time download/upload progress with ETA
- **Error Handling**: Automatic retry logic for network failures
- **Comprehensive Logging**: Detailed logs for debugging and monitoring

## 📋 Requirements

- **OS**: Windows 10/11 (64-bit)
- **Python**: 3.11 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 500MB for app + space for downloads
- **Internet**: Broadband connection required
- **YouTube Account**: For uploading videos

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Language** | Python 3.11+ |
| **GUI** | PyQt5 |
| **Video Download** | yt-dlp |
| **YouTube API** | google-api-python-client |
| **Scheduling** | APScheduler |
| **Database** | SQLite |
| **Packaging** | PyInstaller |

## 📦 Installation

### Quick Start

1. **Clone repository**:
   ```powershell
   git clone https://github.com/itsmohitnarayan/youtubebotvideoextractor.git
   cd youtubebotvideoextractor
   ```

2. **Run setup script**:
   ```powershell
   .\scripts\setup_env.ps1
   ```

3. **Configure YouTube API credentials** (see [SETUP.md](docs/SETUP.md))

4. **Edit configuration**:
   - `.env` - API credentials
   - `config.json` - Target channel and settings

5. **Run application**:
   ```powershell
   .\venv\Scripts\Activate.ps1
   python src/main.py
   ```

For detailed installation instructions, see [**SETUP.md**](docs/SETUP.md).

## 🎯 How It Works

```
┌─────────────────────────────────────────────┐
│   10:00 AM - PC Starts & App Auto-runs     │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│   Monitor Target Channel Every 10 Minutes  │
│   (YouTube Data API v3)                     │
└────────────────┬────────────────────────────┘
                 │ New video detected!
                 ▼
┌─────────────────────────────────────────────┐
│   Download Video + Thumbnail + Metadata    │
│   (yt-dlp)                                  │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│   Upload to Your Channel                   │
│   - Apply metadata (title, desc, tags)     │
│   - Set custom thumbnail                   │
│   - Publish with privacy settings          │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│   Log Success & Notify User                │
│   (System tray notification)               │
└─────────────────────────────────────────────┘
```

## 📖 Usage

### System Tray Menu

Right-click the system tray icon:
- **Show Dashboard** - View monitoring status and statistics
- **Pause/Resume Monitoring** - Control monitoring
- **Check Now** - Force immediate check for new videos
- **Settings** - Configure application
- **View Logs** - Open log viewer
- **Exit** - Close application

### Dashboard

Double-click the tray icon to open the dashboard:
- **Status Panel**: Current monitoring state, last check time
- **Statistics**: Videos detected/downloaded/uploaded today
- **Progress**: Real-time progress of current operation
- **Recent Videos**: List of recently processed videos

## ⚙️ Configuration

### Active Hours
Edit `config.json`:
```json
{
  "active_hours": {
    "start": "10:00",
    "end": "22:00"
  }
}
```

### Check Interval
```json
{
  "monitoring": {
    "check_interval_minutes": 10
  }
}
```

### Upload Settings
```json
{
  "upload": {
    "title_prefix": "[Mirror] ",
    "privacy_status": "public",
    "category_id": "22"
  }
}
```

See [config.example.json](config.example.json) for all options.

## 📊 Project Status

**Current Phase**: Phase 0 - Setup & Foundation ✅

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 0 | ✅ Complete | Setup & Foundation |
| Phase 1 | 🔲 Pending | Core Backend Logic |
| Phase 2 | 🔲 Pending | YouTube Integration |
| Phase 3 | 🔲 Pending | GUI Development |
| Phase 4 | 🔲 Pending | System Integration |
| Phase 5 | 🔲 Pending | Testing & Optimization |
| Phase 6 | 🔲 Pending | Packaging & Deployment |

See [PLAN.md](PLAN.md) for detailed implementation roadmap.

## 🗂️ Project Structure

```
youtubebotvideoextractor/
├── src/
│   ├── core/              # Core components (config, database, logging)
│   ├── youtube/           # YouTube API, downloader, uploader
│   ├── gui/               # PyQt5 GUI components
│   ├── utils/             # Helper functions and validators
│   └── main.py            # Application entry point
├── resources/
│   ├── icons/             # System tray icons
│   ├── ui/                # Qt Designer UI files
│   └── styles/            # QSS stylesheets
├── tests/                 # Unit tests
├── docs/                  # Documentation
├── scripts/               # Setup and build scripts
├── config.json            # Application configuration
├── .env                   # Environment variables (API keys)
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## 🧪 Testing

Run tests:
```powershell
pytest tests/ -v
```

Run with coverage:
```powershell
pytest tests/ --cov=src --cov-report=html
```

## 📝 Documentation

- [**SETUP.md**](docs/SETUP.md) - Detailed setup instructions
- [**PRD.md**](PRD.md) - Product Requirements Document
- [**PLAN.md**](PLAN.md) - Implementation plan and roadmap
- **USER_GUIDE.md** - User manual (coming in Phase 3)
- **TROUBLESHOOTING.md** - Common issues (coming in Phase 5)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [PLAN.md](PLAN.md) for development guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Additional Terms**:
- This software is for legitimate content management only
- Users must have explicit permission from content owners
- Authors are not responsible for misuse

## 👨‍💻 Author

**Mohit Narayan**
- GitHub: [@itsmohitnarayan](https://github.com/itsmohitnarayan)

## 🙏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Excellent video downloader
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework
- [Google YouTube API](https://developers.google.com/youtube/v3) - YouTube integration
- [APScheduler](https://apscheduler.readthedocs.io/) - Task scheduling

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/itsmohitnarayan/youtubebotvideoextractor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/itsmohitnarayan/youtubebotvideoextractor/discussions)

---

**⭐ If you find this project useful, please give it a star!**

**Remember**: Only use this software with proper authorization and in compliance with all applicable laws and terms of service.