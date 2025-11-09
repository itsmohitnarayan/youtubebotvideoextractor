"""
Main application entry point.
Initializes and starts the YouTube Bot Video Extractor.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Import core components (will be implemented in Phase 1)
# from core.config import ConfigManager
# from core.database import DatabaseManager
# from core.logger import setup_logger
# from gui.system_tray import SystemTrayApp


def main():
    """Main application entry point."""
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("YouTube Bot Video Extractor")
    app.setApplicationVersion("1.0.0")
    app.setQuitOnLastWindowClosed(False)  # Keep running in system tray
    
    # TODO: Phase 1 - Initialize core components
    # logger = setup_logger()
    # config = ConfigManager()
    # database = DatabaseManager()
    
    # TODO: Phase 3 - Initialize GUI
    # tray_app = SystemTrayApp(config, database)
    # tray_app.show()
    
    print("YouTube Bot Video Extractor - Phase 0 Setup Complete")
    print("GUI and backend will be implemented in subsequent phases.")
    
    # Start Qt event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
