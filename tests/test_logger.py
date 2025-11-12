"""
Test suite for logger.
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import sys
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.logger import setup_logger, LoggerAdapter, close_logger


class TestLogger:
    """Tests for logger module."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup - wait for Windows to release file handles
        import time
        time.sleep(0.1)
        try:
            shutil.rmtree(temp_dir)
        except PermissionError:
            time.sleep(0.5)
            try:
                shutil.rmtree(temp_dir)
            except:
                pass  # Ignore if still can't delete
    
    def test_setup_logger_creates_log_file(self, temp_dir):
        """Test that logger creates log file."""
        log_file = Path(temp_dir) / "test.log"
        logger = setup_logger(log_file=str(log_file))
        
        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert log_file.exists()
        
        # Close logger to release file handle
        close_logger(logger)
    
    def test_logger_writes_to_file(self, temp_dir):
        """Test that logger writes messages to file."""
        log_file = Path(temp_dir) / "test.log"
        logger = setup_logger(log_file=str(log_file), console=False)
        
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")
        
        # Close logger before reading
        close_logger(logger)
        
        # Read log file
        content = log_file.read_text()
        
        assert "Test info message" in content
        assert "Test warning message" in content
        assert "Test error message" in content
    
    def test_logger_levels(self, temp_dir):
        """Test different log levels."""
        log_file = Path(temp_dir) / "test.log"
        logger = setup_logger(log_file=str(log_file), level="DEBUG", console=False)
        
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
        
        # Close logger before reading
        close_logger(logger)
        
        content = log_file.read_text()
        
        assert "[DEBUG]" in content
        assert "[INFO]" in content
        assert "[WARNING]" in content
        assert "[ERROR]" in content
        assert "[CRITICAL]" in content
    
    def test_logger_format(self, temp_dir):
        """Test log message format."""
        log_file = Path(temp_dir) / "test.log"
        logger = setup_logger(log_file=str(log_file), console=False)
        
        logger.info("Test message")
        
        # Close logger before reading
        close_logger(logger)
        
        content = log_file.read_text()
        
        # Should contain timestamp, level, and message
        assert "[INFO]" in content
        assert "Test message" in content
        # Should contain date/time
        assert "2025" in content or "202" in content
    
    def test_logger_adapter_info(self, temp_dir):
        """Test LoggerAdapter info logging."""
        log_file = Path(temp_dir) / "test.log"
        base_logger = setup_logger(log_file=str(log_file), console=False)
        adapter = LoggerAdapter(base_logger)
        
        adapter.info("Adapter test message")
        
        # Close logger before reading
        close_logger(base_logger)
        
        content = log_file.read_text()
        assert "Adapter test message" in content
    
    def test_logger_adapter_all_levels(self, temp_dir):
        """Test LoggerAdapter with all log levels."""
        log_file = Path(temp_dir) / "test.log"
        base_logger = setup_logger(log_file=str(log_file), level="DEBUG", console=False)
        adapter = LoggerAdapter(base_logger)
        
        adapter.debug("Debug via adapter")
        adapter.info("Info via adapter")
        adapter.warning("Warning via adapter")
        adapter.error("Error via adapter")
        adapter.critical("Critical via adapter")
        
        # Close logger before reading
        close_logger(base_logger)
        
        content = log_file.read_text()
        
        assert "Debug via adapter" in content
        assert "Info via adapter" in content
        assert "Warning via adapter" in content
        assert "Error via adapter" in content
        assert "Critical via adapter" in content
