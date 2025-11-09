"""
Logger Setup
Configures application logging with file rotation and console output.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logger(
    name: str = "YouTubeBot",
    log_file: str = "logs/app.log",
    level: str = "INFO",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    console: bool = True
) -> logging.Logger:
    """
    Set up application logger with file rotation and console output.
    
    Args:
        name: Logger name
        log_file: Path to log file
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        console: Whether to also log to console
    
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create logs directory
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler (optional)
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    logger.info(f"Logger '{name}' initialized (Level: {level})")
    
    return logger


class LoggerAdapter:
    """Adapter to integrate Python logging with database logging."""
    
    def __init__(self, logger: logging.Logger, db_manager=None):
        """
        Initialize logger adapter.
        
        Args:
            logger: Python logger instance
            db_manager: Database manager for storing logs
        """
        self.logger = logger
        self.db_manager = db_manager
    
    def _log(self, level: str, message: str, **kwargs) -> None:
        """
        Log message to both file and database.
        
        Args:
            level: Log level
            message: Log message
            **kwargs: Additional context (module, details, video_id)
        """
        # Log to file/console
        log_method = getattr(self.logger, level.lower())
        log_method(message)
        
        # Log to database (errors only to avoid bloat)
        if self.db_manager and level in ('ERROR', 'CRITICAL'):
            self.db_manager.add_log(
                level=level,
                message=message,
                module=kwargs.get('module'),
                details=kwargs.get('details'),
                video_id=kwargs.get('video_id')
            )
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self._log('DEBUG', message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self._log('INFO', message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self._log('WARNING', message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self._log('ERROR', message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self._log('CRITICAL', message, **kwargs)
