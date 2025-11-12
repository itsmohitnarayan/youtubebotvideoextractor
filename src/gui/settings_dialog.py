"""
Settings Dialog
Configuration settings UI with tabbed interface.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QWidget, QLabel, QLineEdit, QPushButton, QComboBox,
    QSpinBox, QTimeEdit, QCheckBox, QFileDialog,
    QGroupBox, QGridLayout, QDialogButtonBox, QMessageBox
)
from PyQt5.QtCore import pyqtSignal, Qt, QTime
from PyQt5.QtGui import QFont
from pathlib import Path
from typing import Dict, Any, Optional
import logging


class SettingsDialog(QDialog):
    """Settings configuration dialog with multiple tabs."""
    
    # Signal emitted when settings are saved
    settings_saved = pyqtSignal(dict)
    
    def __init__(self, config_manager, parent=None):
        """
        Initialize settings dialog.
        
        Args:
            config_manager: ConfigManager instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        # Window properties
        self.setWindowTitle("Settings")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        # Track if settings were modified
        self.is_dirty = False
        
        # Create UI
        self._create_ui()
        
        # Load current settings
        self._load_settings()
        
        self.logger.info("Settings dialog initialized")
    
    def _create_ui(self) -> None:
        """Create the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Add tabs
        self.tab_widget.addTab(self._create_general_tab(), "General")
        self.tab_widget.addTab(self._create_download_tab(), "Download")
        self.tab_widget.addTab(self._create_upload_tab(), "Upload")
        self.tab_widget.addTab(self._create_youtube_api_tab(), "YouTube API")
        self.tab_widget.addTab(self._create_notifications_tab(), "Notifications")
        
        layout.addWidget(self.tab_widget)
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self._save_settings)
        button_box.rejected.connect(self._cancel)
        layout.addWidget(button_box)
    
    def _create_general_tab(self) -> QWidget:
        """
        Create General settings tab.
        
        Returns:
            QWidget with general settings
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Target Channel
        channel_group = QGroupBox("Target Channel")
        channel_layout = QGridLayout()
        
        channel_layout.addWidget(QLabel("Channel ID:"), 0, 0)
        self.channel_id_input = QLineEdit()
        self.channel_id_input.setPlaceholderText("UC...")
        channel_layout.addWidget(self.channel_id_input, 0, 1)
        
        channel_layout.addWidget(QLabel("Channel URL:"), 1, 0)
        self.channel_url_input = QLineEdit()
        self.channel_url_input.setPlaceholderText("https://www.youtube.com/@channel")
        channel_layout.addWidget(self.channel_url_input, 1, 1)
        
        channel_group.setLayout(channel_layout)
        layout.addWidget(channel_group)
        
        # Active Hours
        hours_group = QGroupBox("Active Hours")
        hours_layout = QGridLayout()
        
        hours_layout.addWidget(QLabel("Start Time:"), 0, 0)
        self.start_time_input = QTimeEdit()
        self.start_time_input.setDisplayFormat("HH:mm")
        hours_layout.addWidget(self.start_time_input, 0, 1)
        
        hours_layout.addWidget(QLabel("End Time:"), 1, 0)
        self.end_time_input = QTimeEdit()
        self.end_time_input.setDisplayFormat("HH:mm")
        hours_layout.addWidget(self.end_time_input, 1, 1)
        
        hours_group.setLayout(hours_layout)
        layout.addWidget(hours_group)
        
        # Monitoring
        monitoring_group = QGroupBox("Monitoring")
        monitoring_layout = QGridLayout()
        
        monitoring_layout.addWidget(QLabel("Check Interval (minutes):"), 0, 0)
        self.check_interval_input = QSpinBox()
        self.check_interval_input.setRange(1, 60)
        self.check_interval_input.setValue(10)
        monitoring_layout.addWidget(self.check_interval_input, 0, 1)
        
        self.catch_up_checkbox = QCheckBox("Catch up on start")
        monitoring_layout.addWidget(self.catch_up_checkbox, 1, 0, 1, 2)
        
        monitoring_group.setLayout(monitoring_layout)
        layout.addWidget(monitoring_group)
        
        layout.addStretch()
        return widget
    
    def _create_download_tab(self) -> QWidget:
        """
        Create Download settings tab.
        
        Returns:
            QWidget with download settings
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Download Directory
        dir_group = QGroupBox("Download Directory")
        dir_layout = QHBoxLayout()
        
        self.download_dir_input = QLineEdit()
        self.download_dir_input.setPlaceholderText("downloads")
        dir_layout.addWidget(self.download_dir_input)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_download_dir)
        dir_layout.addWidget(browse_btn)
        
        dir_group.setLayout(dir_layout)
        layout.addWidget(dir_group)
        
        # Quality Settings
        quality_group = QGroupBox("Quality Settings")
        quality_layout = QGridLayout()
        
        quality_layout.addWidget(QLabel("Video Quality:"), 0, 0)
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["best", "1080p", "720p", "480p"])
        quality_layout.addWidget(self.quality_combo, 0, 1)
        
        quality_layout.addWidget(QLabel("Format:"), 1, 0)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["mp4", "webm", "mkv"])
        quality_layout.addWidget(self.format_combo, 1, 1)
        
        quality_layout.addWidget(QLabel("Max File Size (MB):"), 2, 0)
        self.max_size_input = QSpinBox()
        self.max_size_input.setRange(0, 10000)
        self.max_size_input.setValue(2048)
        self.max_size_input.setSpecialValueText("Unlimited")
        quality_layout.addWidget(self.max_size_input, 2, 1)
        
        quality_group.setLayout(quality_layout)
        layout.addWidget(quality_group)
        
        layout.addStretch()
        return widget
    
    def _create_upload_tab(self) -> QWidget:
        """
        Create Upload settings tab.
        
        Returns:
            QWidget with upload settings
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Title Settings
        title_group = QGroupBox("Title Settings")
        title_layout = QGridLayout()
        
        title_layout.addWidget(QLabel("Title Prefix:"), 0, 0)
        self.title_prefix_input = QLineEdit()
        self.title_prefix_input.setPlaceholderText("[Reupload] ")
        title_layout.addWidget(self.title_prefix_input, 0, 1)
        
        title_layout.addWidget(QLabel("Title Suffix:"), 1, 0)
        self.title_suffix_input = QLineEdit()
        self.title_suffix_input.setPlaceholderText(" - Mirror")
        title_layout.addWidget(self.title_suffix_input, 1, 1)
        
        title_group.setLayout(title_layout)
        layout.addWidget(title_group)
        
        # Description Settings
        desc_group = QGroupBox("Description Settings")
        desc_layout = QGridLayout()
        
        desc_layout.addWidget(QLabel("Append to Description:"), 0, 0)
        self.desc_append_input = QLineEdit()
        self.desc_append_input.setPlaceholderText("Mirrored from original channel")
        desc_layout.addWidget(self.desc_append_input, 0, 1)
        
        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)
        
        # Upload Settings
        upload_group = QGroupBox("Upload Settings")
        upload_layout = QGridLayout()
        
        upload_layout.addWidget(QLabel("Privacy Status:"), 0, 0)
        self.privacy_combo = QComboBox()
        self.privacy_combo.addItems(["public", "unlisted", "private"])
        upload_layout.addWidget(self.privacy_combo, 0, 1)
        
        upload_layout.addWidget(QLabel("Category ID:"), 1, 0)
        self.category_input = QLineEdit()
        self.category_input.setText("22")
        self.category_input.setPlaceholderText("22 (People & Blogs)")
        upload_layout.addWidget(self.category_input, 1, 1)
        
        upload_group.setLayout(upload_layout)
        layout.addWidget(upload_group)
        
        layout.addStretch()
        return widget
    
    def _create_youtube_api_tab(self) -> QWidget:
        """
        Create YouTube API settings tab.
        
        Returns:
            QWidget with YouTube API settings
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Credentials
        cred_group = QGroupBox("API Credentials")
        cred_layout = QVBoxLayout()
        
        # Client secrets file
        secrets_layout = QHBoxLayout()
        secrets_layout.addWidget(QLabel("Client Secrets File:"))
        self.secrets_file_input = QLineEdit()
        self.secrets_file_input.setText("config/client_secrets.json")
        secrets_layout.addWidget(self.secrets_file_input)
        
        browse_secrets_btn = QPushButton("Browse...")
        browse_secrets_btn.clicked.connect(self._browse_secrets_file)
        secrets_layout.addWidget(browse_secrets_btn)
        cred_layout.addLayout(secrets_layout)
        
        # Token file
        token_layout = QHBoxLayout()
        token_layout.addWidget(QLabel("Token File:"))
        self.token_file_input = QLineEdit()
        self.token_file_input.setText("config/token.pickle")
        token_layout.addWidget(self.token_file_input)
        cred_layout.addLayout(token_layout)
        
        # Re-authenticate button
        reauth_btn = QPushButton("🔐 Re-authenticate with YouTube")
        reauth_btn.clicked.connect(self._reauth_youtube)
        cred_layout.addWidget(reauth_btn)
        
        cred_group.setLayout(cred_layout)
        layout.addWidget(cred_group)
        
        # Quota Display
        quota_group = QGroupBox("API Quota Usage")
        quota_layout = QVBoxLayout()
        
        self.quota_label = QLabel("Quota usage information will be displayed here")
        self.quota_label.setWordWrap(True)
        quota_layout.addWidget(self.quota_label)
        
        quota_group.setLayout(quota_layout)
        layout.addWidget(quota_group)
        
        layout.addStretch()
        return widget
    
    def _create_notifications_tab(self) -> QWidget:
        """
        Create Notifications settings tab.
        
        Returns:
            QWidget with notification settings
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Notification Settings
        notif_group = QGroupBox("Notification Settings")
        notif_layout = QVBoxLayout()
        
        self.notifications_enabled_checkbox = QCheckBox("Enable Notifications")
        self.notifications_enabled_checkbox.setChecked(True)
        notif_layout.addWidget(self.notifications_enabled_checkbox)
        
        self.notify_download_checkbox = QCheckBox("Notify on Download Complete")
        notif_layout.addWidget(self.notify_download_checkbox)
        
        self.notify_upload_checkbox = QCheckBox("Notify on Upload Complete")
        notif_layout.addWidget(self.notify_upload_checkbox)
        
        self.notify_error_checkbox = QCheckBox("Notify on Error")
        self.notify_error_checkbox.setChecked(True)
        notif_layout.addWidget(self.notify_error_checkbox)
        
        notif_group.setLayout(notif_layout)
        layout.addWidget(notif_group)
        
        layout.addStretch()
        return widget
    
    def _browse_download_dir(self) -> None:
        """Open directory browser for download directory."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Download Directory",
            self.download_dir_input.text()
        )
        if directory:
            self.download_dir_input.setText(directory)
            self.is_dirty = True
    
    def _browse_secrets_file(self) -> None:
        """Open file browser for client secrets file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Client Secrets File",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            self.secrets_file_input.setText(file_path)
            self.is_dirty = True
    
    def _reauth_youtube(self) -> None:
        """Handle YouTube re-authentication."""
        reply = QMessageBox.question(
            self,
            "Re-authenticate",
            "This will delete the current token and open a browser for re-authentication. Continue?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Delete token file
            token_path = Path(self.token_file_input.text())
            if token_path.exists():
                token_path.unlink()
                QMessageBox.information(
                    self,
                    "Token Deleted",
                    "Token file deleted. Please restart the application to re-authenticate."
                )
    
    def _load_settings(self) -> None:
        """Load current settings into UI."""
        try:
            # General
            self.channel_id_input.setText(
                self.config_manager.get("target_channel.channel_id", "")
            )
            self.channel_url_input.setText(
                self.config_manager.get("target_channel.channel_url", "")
            )
            
            start_time = self.config_manager.get("active_hours.start", "10:00")
            self.start_time_input.setTime(QTime.fromString(start_time, "HH:mm"))
            
            end_time = self.config_manager.get("active_hours.end", "22:00")
            self.end_time_input.setTime(QTime.fromString(end_time, "HH:mm"))
            
            self.check_interval_input.setValue(
                self.config_manager.get("monitoring.check_interval_minutes", 10)
            )
            self.catch_up_checkbox.setChecked(
                self.config_manager.get("monitoring.catch_up_on_start", True)
            )
            
            # Download
            self.download_dir_input.setText(
                self.config_manager.get("download.directory", "downloads")
            )
            self.quality_combo.setCurrentText(
                self.config_manager.get("download.video_quality", "best")
            )
            self.format_combo.setCurrentText(
                self.config_manager.get("download.format", "mp4")
            )
            self.max_size_input.setValue(
                self.config_manager.get("download.max_filesize_mb", 2048)
            )
            
            # Upload
            self.title_prefix_input.setText(
                self.config_manager.get("upload.title_prefix", "")
            )
            self.title_suffix_input.setText(
                self.config_manager.get("upload.title_suffix", "")
            )
            self.desc_append_input.setText(
                self.config_manager.get("upload.description_append", "")
            )
            self.privacy_combo.setCurrentText(
                self.config_manager.get("upload.privacy_status", "public")
            )
            self.category_input.setText(
                self.config_manager.get("upload.category_id", "22")
            )
            
            # YouTube API
            self.secrets_file_input.setText(
                self.config_manager.get("youtube_api.client_secrets_file", "config/client_secrets.json")
            )
            self.token_file_input.setText(
                self.config_manager.get("youtube_api.token_file", "config/token.pickle")
            )
            
            # Notifications
            self.notifications_enabled_checkbox.setChecked(
                self.config_manager.get("notifications.enabled", True)
            )
            self.notify_download_checkbox.setChecked(
                self.config_manager.get("notifications.on_download", True)
            )
            self.notify_upload_checkbox.setChecked(
                self.config_manager.get("notifications.on_upload", True)
            )
            self.notify_error_checkbox.setChecked(
                self.config_manager.get("notifications.on_error", True)
            )
            
            self.is_dirty = False
            self.logger.info("Settings loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
            QMessageBox.warning(
                self,
                "Load Error",
                f"Failed to load some settings: {e}"
            )
    
    def _save_settings(self) -> None:
        """Save settings from UI to config."""
        try:
            # General
            self.config_manager.set("target_channel.channel_id", self.channel_id_input.text())
            self.config_manager.set("target_channel.channel_url", self.channel_url_input.text())
            self.config_manager.set("active_hours.start", self.start_time_input.time().toString("HH:mm"))
            self.config_manager.set("active_hours.end", self.end_time_input.time().toString("HH:mm"))
            self.config_manager.set("monitoring.check_interval_minutes", self.check_interval_input.value())
            self.config_manager.set("monitoring.catch_up_on_start", self.catch_up_checkbox.isChecked())
            
            # Download
            self.config_manager.set("download.directory", self.download_dir_input.text())
            self.config_manager.set("download.video_quality", self.quality_combo.currentText())
            self.config_manager.set("download.format", self.format_combo.currentText())
            self.config_manager.set("download.max_filesize_mb", self.max_size_input.value())
            
            # Upload
            self.config_manager.set("upload.title_prefix", self.title_prefix_input.text())
            self.config_manager.set("upload.title_suffix", self.title_suffix_input.text())
            self.config_manager.set("upload.description_append", self.desc_append_input.text())
            self.config_manager.set("upload.privacy_status", self.privacy_combo.currentText())
            self.config_manager.set("upload.category_id", self.category_input.text())
            
            # YouTube API
            self.config_manager.set("youtube_api.client_secrets_file", self.secrets_file_input.text())
            self.config_manager.set("youtube_api.token_file", self.token_file_input.text())
            
            # Notifications
            self.config_manager.set("notifications.enabled", self.notifications_enabled_checkbox.isChecked())
            self.config_manager.set("notifications.on_download", self.notify_download_checkbox.isChecked())
            self.config_manager.set("notifications.on_upload", self.notify_upload_checkbox.isChecked())
            self.config_manager.set("notifications.on_error", self.notify_error_checkbox.isChecked())
            
            # Save to file
            self.config_manager.save_config()
            
            self.is_dirty = False
            self.logger.info("Settings saved successfully")
            
            # Emit signal
            self.settings_saved.emit(self.config_manager.config)
            
            # Show success message
            QMessageBox.information(
                self,
                "Settings Saved",
                "Settings have been saved successfully."
            )
            
            self.accept()
            
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save settings: {e}"
            )
    
    def _cancel(self) -> None:
        """Handle cancel button."""
        if self.is_dirty:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Discard them?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
        
        self.reject()
    
    def closeEvent(self, event) -> None:
        """
        Handle close event.
        
        Args:
            event: Close event
        """
        if self.is_dirty:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Discard them?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                event.ignore()
                return
        
        event.accept()

