"""
System Tray Application
Main system tray icon and menu with status indicators.
"""

from PyQt5.QtWidgets import (
    QSystemTrayIcon, QMenu, QAction, QApplication
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, QObject
from pathlib import Path
from typing import Optional, Callable
import logging


class SystemTrayIcon(QSystemTrayIcon):
    """System tray icon with context menu and notifications."""
    
    # Custom signals
    show_dashboard_requested = pyqtSignal()
    pause_resume_requested = pyqtSignal()
    check_now_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    logs_requested = pyqtSignal()
    exit_requested = pyqtSignal()
    
    def __init__(self, app: QApplication, parent=None):
        """
        Initialize system tray icon.
        
        Args:
            app: QApplication instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.app = app
        self.logger = logging.getLogger(__name__)
        
        # Status tracking
        self.is_monitoring = False
        self.current_status = "idle"  # idle, downloading, uploading, error, paused
        self.last_check_time = None
        
        # Icon paths
        self.icon_dir = Path(__file__).parent.parent.parent / "resources" / "icons"
        self.icons = self._load_icons()
        
        # Create context menu (must be before set_status)
        self.menu = self._create_menu()
        self.setContextMenu(self.menu)
        
        # Set initial icon and status
        self.set_status("idle")
        
        # Connect signals
        self.activated.connect(self._on_activated)
        
        # Set tooltip
        self.setToolTip("YouTube Video Replicator Bot")
        
        self.logger.info("System tray icon initialized")
    
    def _load_icons(self) -> dict:
        """
        Load status icons.
        
        Returns:
            Dictionary of status -> QIcon
        """
        icons = {}
        
        # Try to load icons from resources
        icon_files = {
            'idle': 'icon_idle.png',
            'monitoring': 'icon_idle.png',  # Same as idle
            'downloading': 'icon_downloading.png',
            'uploading': 'icon_uploading.png',
            'error': 'icon_error.png',
            'paused': 'icon_paused.png',
        }
        
        for status, filename in icon_files.items():
            icon_path = self.icon_dir / filename
            if icon_path.exists():
                icons[status] = QIcon(str(icon_path))
            else:
                # Use default application icon
                icons[status] = self.app.style().standardIcon(
                    self.app.style().SP_ComputerIcon
                )
        
        return icons
    
    def _create_menu(self) -> QMenu:
        """
        Create context menu.
        
        Returns:
            QMenu instance
        """
        menu = QMenu()
        
        # Header (non-clickable)
        header_action = QAction("YouTube Bot", self)
        header_action.setEnabled(False)
        menu.addAction(header_action)
        
        menu.addSeparator()
        
        # Status info (non-clickable)
        self.status_action = QAction("● Idle", self)
        self.status_action.setEnabled(False)
        menu.addAction(self.status_action)
        
        self.last_check_action = QAction("Last Check: Never", self)
        self.last_check_action.setEnabled(False)
        menu.addAction(self.last_check_action)
        
        menu.addSeparator()
        
        # Show Dashboard
        show_action = QAction("🪟 Show Dashboard", self)
        show_action.triggered.connect(self.show_dashboard_requested.emit)
        menu.addAction(show_action)
        
        # Pause/Resume
        self.pause_resume_action = QAction("⏸️ Pause Monitoring", self)
        self.pause_resume_action.triggered.connect(self.pause_resume_requested.emit)
        menu.addAction(self.pause_resume_action)
        
        # Check Now
        check_action = QAction("🔄 Check Now", self)
        check_action.triggered.connect(self.check_now_requested.emit)
        menu.addAction(check_action)
        
        menu.addSeparator()
        
        # Settings
        settings_action = QAction("⚙️ Settings", self)
        settings_action.triggered.connect(self.settings_requested.emit)
        menu.addAction(settings_action)
        
        # View Logs
        logs_action = QAction("📋 View Logs", self)
        logs_action.triggered.connect(self.logs_requested.emit)
        menu.addAction(logs_action)
        
        menu.addSeparator()
        
        # Exit
        exit_action = QAction("❌ Exit", self)
        exit_action.triggered.connect(self.exit_requested.emit)
        menu.addAction(exit_action)
        
        return menu
    
    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """
        Handle tray icon activation.
        
        Args:
            reason: Activation reason
        """
        if reason == QSystemTrayIcon.DoubleClick:
            # Double-click opens dashboard
            self.show_dashboard_requested.emit()
        elif reason == QSystemTrayIcon.Trigger:
            # Single click shows menu (on some systems)
            pass
    
    def set_status(self, status: str) -> None:
        """
        Set current status and update icon.
        
        Args:
            status: Status name (idle, downloading, uploading, error, paused)
        """
        self.current_status = status
        
        # Update icon
        if status in self.icons:
            self.setIcon(self.icons[status])
        
        # Update status text in menu
        status_text_map = {
            'idle': '🟢 Monitoring Active',
            'monitoring': '🟢 Monitoring Active',
            'downloading': '🔵 Downloading Video',
            'uploading': '🟡 Uploading Video',
            'error': '🔴 Error Occurred',
            'paused': '⚫ Paused',
        }
        
        status_text = status_text_map.get(status, '⚫ Unknown')
        self.status_action.setText(status_text)
        
        # Update tooltip
        self.setToolTip(f"YouTube Bot - {status_text}")
        
        self.logger.debug(f"Status changed to: {status}")
    
    def set_monitoring_state(self, is_monitoring: bool) -> None:
        """
        Update monitoring state.
        
        Args:
            is_monitoring: True if monitoring is active
        """
        self.is_monitoring = is_monitoring
        
        # Update pause/resume button
        if is_monitoring:
            self.pause_resume_action.setText("⏸️ Pause Monitoring")
            if self.current_status == 'paused':
                self.set_status('idle')
        else:
            self.pause_resume_action.setText("▶️ Resume Monitoring")
            self.set_status('paused')
    
    def update_last_check_time(self, timestamp: str) -> None:
        """
        Update last check timestamp.
        
        Args:
            timestamp: Human-readable timestamp (e.g., "2 minutes ago")
        """
        self.last_check_time = timestamp
        self.last_check_action.setText(f"Last Check: {timestamp}")
    
    def show_notification(
        self,
        title: str,
        message: str,
        icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.Information
    ) -> None:
        """
        Show balloon notification.
        
        Args:
            title: Notification title
            message: Notification message
            icon: Icon type (Information, Warning, Critical)
        """
        self.showMessage(title, message, icon, 5000)  # 5 seconds
        self.logger.info(f"Notification: {title} - {message}")
    
    def show_info(self, title: str, message: str) -> None:
        """Show information notification."""
        self.show_notification(title, message, QSystemTrayIcon.Information)
    
    def show_warning(self, title: str, message: str) -> None:
        """Show warning notification."""
        self.show_notification(title, message, QSystemTrayIcon.Warning)
    
    def show_error(self, title: str, message: str) -> None:
        """Show error notification."""
        self.show_notification(title, message, QSystemTrayIcon.Critical)
    
    def show_video_detected(self, video_title: str) -> None:
        """Show notification for new video detection."""
        self.show_info(
            "New Video Detected",
            f"Processing: {video_title[:50]}..."
        )
    
    def show_download_complete(self, video_title: str) -> None:
        """Show notification for download completion."""
        self.show_info(
            "Download Complete",
            f"Downloaded: {video_title[:50]}..."
        )
    
    def show_upload_complete(self, video_title: str) -> None:
        """Show notification for upload completion."""
        self.show_info(
            "Upload Complete",
            f"Uploaded: {video_title[:50]}..."
        )
    
    def show_error_notification(self, error_message: str) -> None:
        """Show error notification."""
        self.show_error(
            "Error Occurred",
            error_message[:100]
        )

