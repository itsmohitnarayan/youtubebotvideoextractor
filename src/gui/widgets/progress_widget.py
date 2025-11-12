"""
Progress Widget
Custom widget for displaying download/upload progress.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QProgressBar, QPushButton
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from typing import Optional
import logging


class ProgressWidget(QWidget):
    """Widget for displaying operation progress with details."""
    
    # Signal emitted when cancel is clicked
    cancel_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        """
        Initialize progress widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger(__name__)
        
        # State
        self.is_active = False
        self.current_operation = ""
        
        # Create UI
        self._create_ui()
        
        # Hide initially
        self.setVisible(False)
    
    def _create_ui(self) -> None:
        """Create the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Operation label
        self.operation_label = QLabel("Operation")
        font = QFont()
        font.setBold(True)
        self.operation_label.setFont(font)
        layout.addWidget(self.operation_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setMinimumHeight(25)
        layout.addWidget(self.progress_bar)
        
        # Details row (speed, ETA, cancel button)
        details_layout = QHBoxLayout()
        
        # Speed label
        self.speed_label = QLabel("Speed: --")
        self.speed_label.setStyleSheet("color: #757575;")
        details_layout.addWidget(self.speed_label)
        
        # ETA label
        self.eta_label = QLabel("ETA: --")
        self.eta_label.setStyleSheet("color: #757575;")
        details_layout.addWidget(self.eta_label)
        
        details_layout.addStretch()
        
        # Cancel button
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.setMaximumWidth(100)
        self.cancel_btn.clicked.connect(self._on_cancel_clicked)
        details_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(details_layout)
    
    def _on_cancel_clicked(self) -> None:
        """Handle cancel button click."""
        self.cancel_requested.emit()
        self.logger.info(f"Cancel requested for: {self.current_operation}")
    
    def start_operation(
        self,
        operation: str,
        show_cancel: bool = True
    ) -> None:
        """
        Start a new operation.
        
        Args:
            operation: Operation description
            show_cancel: Whether to show cancel button
        """
        self.is_active = True
        self.current_operation = operation
        
        self.operation_label.setText(operation)
        self.progress_bar.setValue(0)
        self.speed_label.setText("Speed: --")
        self.eta_label.setText("ETA: --")
        self.cancel_btn.setVisible(show_cancel)
        
        self.setVisible(True)
        self.logger.info(f"Started operation: {operation}")
    
    def update_progress(
        self,
        progress: int,
        speed: Optional[str] = None,
        eta: Optional[str] = None
    ) -> None:
        """
        Update progress information.
        
        Args:
            progress: Progress percentage (0-100)
            speed: Speed string (e.g., "1.5 MB/s")
            eta: ETA string (e.g., "2m 30s")
        """
        self.progress_bar.setValue(progress)
        
        if speed:
            self.speed_label.setText(f"Speed: {speed}")
        
        if eta:
            self.eta_label.setText(f"ETA: {eta}")
    
    def complete_operation(self, message: Optional[str] = None) -> None:
        """
        Mark operation as complete.
        
        Args:
            message: Optional completion message
        """
        self.progress_bar.setValue(100)
        
        if message:
            self.operation_label.setText(message)
        else:
            self.operation_label.setText(f"{self.current_operation} - Complete")
        
        self.speed_label.setText("Speed: --")
        self.eta_label.setText("ETA: --")
        self.cancel_btn.setVisible(False)
        
        self.is_active = False
        self.logger.info(f"Completed operation: {self.current_operation}")
    
    def error_operation(self, error_message: str) -> None:
        """
        Mark operation as failed.
        
        Args:
            error_message: Error description
        """
        self.operation_label.setText(f"Error: {error_message}")
        self.operation_label.setStyleSheet("color: #F44336;")
        self.progress_bar.setValue(0)
        self.speed_label.setText("")
        self.eta_label.setText("")
        self.cancel_btn.setVisible(False)
        
        self.is_active = False
        self.logger.error(f"Operation failed: {error_message}")
    
    def hide_widget(self) -> None:
        """Hide the widget."""
        self.setVisible(False)
        self.is_active = False
    
    def set_indeterminate(self, indeterminate: bool = True) -> None:
        """
        Set progress bar to indeterminate mode.
        
        Args:
            indeterminate: True for indeterminate (busy) mode
        """
        if indeterminate:
            self.progress_bar.setRange(0, 0)  # Indeterminate
        else:
            self.progress_bar.setRange(0, 100)  # Normal
