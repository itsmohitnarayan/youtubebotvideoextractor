"""
Log Viewer Widget
Custom widget for viewing application logs with filtering and export.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QComboBox, QFileDialog,
    QLabel, QMessageBox
)
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QTextCursor, QColor, QTextCharFormat
from pathlib import Path
from typing import Optional
import logging


class LogViewer(QWidget):
    """Widget for viewing and filtering application logs."""
    
    def __init__(self, log_file_path: Optional[str] = None, parent=None):
        """
        Initialize log viewer.
        
        Args:
            log_file_path: Path to log file to monitor
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.log_file_path = Path(log_file_path) if log_file_path else None
        self.logger = logging.getLogger(__name__)
        
        # State
        self.current_filter = "ALL"
        self.auto_scroll = True
        self.last_position = 0
        
        # Color scheme for log levels
        self.level_colors = {
            'DEBUG': QColor(150, 150, 150),    # Gray
            'INFO': QColor(100, 180, 100),     # Green
            'WARNING': QColor(255, 165, 0),    # Orange
            'ERROR': QColor(220, 50, 50),      # Red
            'CRITICAL': QColor(139, 0, 0),     # Dark Red
        }
        
        # Create UI
        self._create_ui()
        
        # Auto-refresh timer
        if self.log_file_path:
            self.refresh_timer = QTimer(self)
            self.refresh_timer.timeout.connect(self._auto_refresh)
            self.refresh_timer.start(1000)  # Refresh every second
    
    def _create_ui(self) -> None:
        """Create the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Control panel
        control_layout = QHBoxLayout()
        
        # Filter combo
        control_layout.addWidget(QLabel("Filter:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.filter_combo.currentTextChanged.connect(self._on_filter_changed)
        control_layout.addWidget(self.filter_combo)
        
        control_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._manual_refresh)
        control_layout.addWidget(refresh_btn)
        
        # Export button
        export_btn = QPushButton("💾 Export")
        export_btn.clicked.connect(self._export_logs)
        control_layout.addWidget(export_btn)
        
        # Clear button
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.clicked.connect(self._clear_logs)
        control_layout.addWidget(clear_btn)
        
        layout.addLayout(control_layout)
        
        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setLineWrapMode(QTextEdit.NoWrap)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 10pt;
            }
        """)
        layout.addWidget(self.log_text)
        
        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #757575;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        self.line_count_label = QLabel("Lines: 0")
        self.line_count_label.setStyleSheet("color: #757575;")
        status_layout.addWidget(self.line_count_label)
        
        layout.addLayout(status_layout)
        
        # Load initial logs
        if self.log_file_path:
            self._load_logs()
    
    def _on_filter_changed(self, filter_level: str) -> None:
        """
        Handle filter level change.
        
        Args:
            filter_level: Selected filter level
        """
        self.current_filter = filter_level
        self._load_logs()
        self.logger.debug(f"Filter changed to: {filter_level}")
    
    def _load_logs(self) -> None:
        """Load and display logs from file."""
        if not self.log_file_path or not self.log_file_path.exists():
            self.log_text.setPlainText("Log file not found")
            return
        
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Filter lines
            filtered_lines = []
            for line in lines:
                if self.current_filter == "ALL":
                    filtered_lines.append(line)
                elif self.current_filter in line:
                    filtered_lines.append(line)
            
            # Clear and display
            self.log_text.clear()
            
            for line in filtered_lines:
                self._append_colored_line(line)
            
            # Update status
            self.line_count_label.setText(f"Lines: {len(filtered_lines)}")
            self.status_label.setText(f"Loaded {len(filtered_lines)} lines")
            
            # Auto-scroll to bottom
            if self.auto_scroll:
                self.log_text.moveCursor(QTextCursor.End)
            
        except Exception as e:
            self.logger.error(f"Error loading logs: {e}")
            self.log_text.setPlainText(f"Error loading logs: {e}")
    
    def _append_colored_line(self, line: str) -> None:
        """
        Append a line with color coding based on log level.
        
        Args:
            line: Log line to append
        """
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Determine color based on log level
        color = QColor(212, 212, 212)  # Default white
        for level, level_color in self.level_colors.items():
            if level in line:
                color = level_color
                break
        
        # Set text format
        fmt = QTextCharFormat()
        fmt.setForeground(color)
        
        # Insert text
        cursor.insertText(line, fmt)
        
        self.log_text.setTextCursor(cursor)
    
    def _auto_refresh(self) -> None:
        """Auto-refresh logs (called by timer)."""
        if not self.log_file_path or not self.log_file_path.exists():
            return
        
        try:
            # Check if file has new content
            current_size = self.log_file_path.stat().st_size
            if current_size > self.last_position:
                self._load_logs()
                self.last_position = current_size
        except Exception as e:
            self.logger.error(f"Error in auto-refresh: {e}")
    
    def _manual_refresh(self) -> None:
        """Manual refresh triggered by button."""
        self._load_logs()
        self.status_label.setText("Refreshed")
        self.logger.info("Logs manually refreshed")
    
    def _export_logs(self) -> None:
        """Export logs to a file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Logs",
            f"logs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Logs exported to:\n{file_path}"
                )
                self.logger.info(f"Logs exported to: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Failed",
                    f"Failed to export logs: {e}"
                )
                self.logger.error(f"Error exporting logs: {e}")
    
    def _clear_logs(self) -> None:
        """Clear the log display."""
        reply = QMessageBox.question(
            self,
            "Clear Logs",
            "Clear the log display? (This will not delete the log file)",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.log_text.clear()
            self.line_count_label.setText("Lines: 0")
            self.status_label.setText("Display cleared")
            self.logger.info("Log display cleared")
    
    def append_log(self, message: str, level: str = "INFO") -> None:
        """
        Append a log message directly to the viewer.
        
        Args:
            message: Log message
            level: Log level
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}\n"
        self._append_colored_line(log_line)
        
        # Auto-scroll
        if self.auto_scroll:
            self.log_text.moveCursor(QTextCursor.End)
    
    def set_log_file(self, log_file_path: str) -> None:
        """
        Set a new log file to monitor.
        
        Args:
            log_file_path: Path to log file
        """
        self.log_file_path = Path(log_file_path)
        self.last_position = 0
        self._load_logs()
        self.logger.info(f"Log file set to: {log_file_path}")


# Import datetime for export filename
from datetime import datetime
