"""
Main Dashboard Window
Primary GUI for monitoring and control.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QPushButton, QListWidget, QListWidgetItem,
    QProgressBar, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QIcon, QFont
from datetime import datetime
from typing import Optional, Dict, Any
import logging


class MainWindow(QMainWindow):
    """Main dashboard window for monitoring and control."""
    
    # Custom signals
    pause_clicked = pyqtSignal()
    resume_clicked = pyqtSignal()
    check_now_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()
    logs_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        """
        Initialize main window.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger(__name__)
        
        # Window properties
        self.setWindowTitle("YouTube Video Replicator Bot")
        self.setMinimumSize(800, 600)
        self.resize(900, 700)
        
        # State tracking
        self.is_monitoring = False
        self.current_operation = None
        self.progress_value = 0
        
        # Create UI
        self._create_ui()
        
        # Update timer (refresh every second)
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._update_next_check_countdown)
        self.update_timer.start(1000)  # 1 second
        
        self.logger.info("Main window initialized")
    
    def _create_ui(self) -> None:
        """Create the user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Add components
        main_layout.addWidget(self._create_status_group())
        main_layout.addWidget(self._create_statistics_group())
        main_layout.addWidget(self._create_progress_group())
        main_layout.addWidget(self._create_recent_videos_group())
        main_layout.addWidget(self._create_control_panel())
    
    def _create_status_group(self) -> QGroupBox:
        """
        Create status information group.
        
        Returns:
            QGroupBox with status information
        """
        group = QGroupBox("Status")
        layout = QGridLayout()
        
        # Status
        layout.addWidget(QLabel("Status:"), 0, 0)
        self.status_label = QLabel("⚫ Idle")
        self.status_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.status_label, 0, 1)
        
        # Channel
        layout.addWidget(QLabel("Target Channel:"), 1, 0)
        self.channel_label = QLabel("Not configured")
        layout.addWidget(self.channel_label, 1, 1)
        
        # Last check
        layout.addWidget(QLabel("Last Checked:"), 2, 0)
        self.last_check_label = QLabel("Never")
        layout.addWidget(self.last_check_label, 2, 1)
        
        # Next check
        layout.addWidget(QLabel("Next Check:"), 3, 0)
        self.next_check_label = QLabel("--")
        layout.addWidget(self.next_check_label, 3, 1)
        
        group.setLayout(layout)
        return group
    
    def _create_statistics_group(self) -> QGroupBox:
        """
        Create statistics group.
        
        Returns:
            QGroupBox with statistics
        """
        group = QGroupBox("Today's Activity")
        layout = QGridLayout()
        
        # Videos detected
        layout.addWidget(QLabel("Videos Detected:"), 0, 0)
        self.detected_label = QLabel("0")
        self.detected_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
        layout.addWidget(self.detected_label, 0, 1)
        
        # Downloaded
        layout.addWidget(QLabel("Downloaded:"), 1, 0)
        self.downloaded_label = QLabel("0")
        self.downloaded_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        layout.addWidget(self.downloaded_label, 1, 1)
        
        # Uploaded
        layout.addWidget(QLabel("Uploaded:"), 2, 0)
        self.uploaded_label = QLabel("0")
        self.uploaded_label.setStyleSheet("font-weight: bold; color: #FF9800;")
        layout.addWidget(self.uploaded_label, 2, 1)
        
        # Errors
        layout.addWidget(QLabel("Errors:"), 3, 0)
        self.errors_label = QLabel("0")
        self.errors_label.setStyleSheet("font-weight: bold; color: #F44336;")
        layout.addWidget(self.errors_label, 3, 1)
        
        group.setLayout(layout)
        return group
    
    def _create_progress_group(self) -> QGroupBox:
        """
        Create current operation progress group.
        
        Returns:
            QGroupBox with progress information
        """
        group = QGroupBox("Current Operation")
        layout = QVBoxLayout()
        
        # Operation label
        self.operation_label = QLabel("Idle")
        self.operation_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.operation_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        layout.addWidget(self.progress_bar)
        
        # ETA label
        self.eta_label = QLabel("")
        self.eta_label.setStyleSheet("color: #757575;")
        layout.addWidget(self.eta_label)
        
        group.setLayout(layout)
        return group
    
    def _create_recent_videos_group(self) -> QGroupBox:
        """
        Create recent videos list group.
        
        Returns:
            QGroupBox with recent videos list
        """
        group = QGroupBox("Recent Videos")
        layout = QVBoxLayout()
        
        # List widget
        self.videos_list = QListWidget()
        self.videos_list.setAlternatingRowColors(True)
        layout.addWidget(self.videos_list)
        
        group.setLayout(layout)
        return group
    
    def _create_control_panel(self) -> QWidget:
        """
        Create control buttons panel.
        
        Returns:
            QWidget with control buttons
        """
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        # Pause/Resume button
        self.pause_resume_btn = QPushButton("⏸️ Pause")
        self.pause_resume_btn.setMinimumHeight(40)
        self.pause_resume_btn.clicked.connect(self._on_pause_resume_clicked)
        layout.addWidget(self.pause_resume_btn)
        
        # Check Now button
        check_now_btn = QPushButton("🔄 Check Now")
        check_now_btn.setMinimumHeight(40)
        check_now_btn.clicked.connect(self.check_now_clicked.emit)
        layout.addWidget(check_now_btn)
        
        # Settings button
        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.setMinimumHeight(40)
        settings_btn.clicked.connect(self.settings_clicked.emit)
        layout.addWidget(settings_btn)
        
        # View Logs button
        logs_btn = QPushButton("📋 View Logs")
        logs_btn.setMinimumHeight(40)
        logs_btn.clicked.connect(self.logs_clicked.emit)
        layout.addWidget(logs_btn)
        
        widget.setLayout(layout)
        return widget
    
    def _on_pause_resume_clicked(self) -> None:
        """Handle pause/resume button click."""
        if self.is_monitoring:
            self.pause_clicked.emit()
        else:
            self.resume_clicked.emit()
    
    def _update_next_check_countdown(self) -> None:
        """Update next check countdown (called every second)."""
        # This will be updated from external controller
        pass
    
    def set_monitoring_state(self, is_monitoring: bool) -> None:
        """
        Update monitoring state.
        
        Args:
            is_monitoring: True if monitoring is active
        """
        self.is_monitoring = is_monitoring
        
        if is_monitoring:
            self.status_label.setText("🟢 Monitoring Active")
            self.pause_resume_btn.setText("⏸️ Pause")
        else:
            self.status_label.setText("⚫ Paused")
            self.pause_resume_btn.setText("▶️ Resume")
    
    def set_channel_info(self, channel_name: str, channel_id: str) -> None:
        """
        Update channel information.
        
        Args:
            channel_name: Channel display name
            channel_id: Channel ID
        """
        self.channel_label.setText(f"{channel_name} ({channel_id[:10]}...)")
    
    def update_last_check_time(self, timestamp: str) -> None:
        """
        Update last check timestamp.
        
        Args:
            timestamp: Human-readable timestamp
        """
        self.last_check_label.setText(timestamp)
    
    def update_next_check_time(self, timestamp: str) -> None:
        """
        Update next check timestamp.
        
        Args:
            timestamp: Human-readable timestamp
        """
        self.next_check_label.setText(timestamp)
    
    def update_statistics(self, stats: Dict[str, int]) -> None:
        """
        Update statistics display.
        
        Args:
            stats: Dictionary with detected, downloaded, uploaded, errors counts
        """
        self.detected_label.setText(str(stats.get('detected', 0)))
        self.downloaded_label.setText(str(stats.get('downloaded', 0)))
        self.uploaded_label.setText(str(stats.get('uploaded', 0)))
        self.errors_label.setText(str(stats.get('errors', 0)))
    
    def set_current_operation(
        self,
        operation: str,
        progress: int = 0,
        eta: str = ""
    ) -> None:
        """
        Update current operation display.
        
        Args:
            operation: Operation description
            progress: Progress percentage (0-100)
            eta: Estimated time remaining
        """
        self.current_operation = operation
        self.operation_label.setText(operation)
        self.progress_bar.setValue(progress)
        self.eta_label.setText(eta)
    
    def clear_current_operation(self) -> None:
        """Clear current operation display."""
        self.operation_label.setText("Idle")
        self.progress_bar.setValue(0)
        self.eta_label.setText("")
    
    def add_recent_video(
        self,
        title: str,
        status: str,
        timestamp: str
    ) -> None:
        """
        Add video to recent videos list.
        
        Args:
            title: Video title
            status: Video status (✓, ⏳, ❌)
            timestamp: Timestamp string
        """
        item_text = f"{status} {title} - {timestamp}"
        item = QListWidgetItem(item_text)
        
        # Set color based on status
        if status == "✓":
            item.setForeground(Qt.darkGreen)
        elif status == "⏳":
            item.setForeground(Qt.darkYellow)
        elif status == "❌":
            item.setForeground(Qt.darkRed)
        
        # Add to top of list
        self.videos_list.insertItem(0, item)
        
        # Keep only last 20 videos
        while self.videos_list.count() > 20:
            self.videos_list.takeItem(20)
    
    def update_video_status(self, video_id: str, status: str) -> None:
        """
        Update status of a video in the list.
        
        Args:
            video_id: Video ID to update
            status: New status
        """
        # This can be enhanced to track video IDs and update specific items
        pass
    
    def closeEvent(self, event) -> None:
        """
        Handle window close event.
        
        Args:
            event: Close event
        """
        # Hide instead of close (minimize to tray)
        event.ignore()
        self.hide()
        self.logger.info("Main window hidden to tray")

