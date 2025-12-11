"""Centralized logging for Cloud Run."""

import logging
import json
import sys
from datetime import datetime
from typing import Optional


class CloudLoggingFormatter(logging.Formatter):
    """Format logs as JSON for Google Cloud Logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, "extra"):
            log_obj.update(record.extra)
        
        return json.dumps(log_obj)


def setup_logger(name: str, log_level: Optional[str] = None) -> logging.Logger:
    """Setup logger with Cloud Logging formatter."""
    logger = logging.getLogger(name)
    
    # Get log level
    if log_level is None:
        import os
        log_level = os.getenv("LOG_LEVEL", "INFO")
    
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Use JSON formatter for Cloud Logging
    formatter = CloudLoggingFormatter()
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    logger.propagate = False
    
    return logger


class StructuredLogger:
    """Wrapper for structured logging."""
    
    def __init__(self, logger: logging.Logger):
        self._logger = logger
    
    def info(self, message: str, **kwargs):
        """Log info message with structured data."""
        extra = {"extra": kwargs} if kwargs else {}
        self._logger.info(message, extra=extra)
    
    def error(self, message: str, **kwargs):
        """Log error message with structured data."""
        extra = {"extra": kwargs} if kwargs else {}
        self._logger.error(message, extra=extra)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with structured data."""
        extra = {"extra": kwargs} if kwargs else {}
        self._logger.warning(message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with structured data."""
        extra = {"extra": kwargs} if kwargs else {}
        self._logger.debug(message, extra=extra)
