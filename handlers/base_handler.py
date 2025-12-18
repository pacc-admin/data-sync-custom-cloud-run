"""Base handler for all sync operations."""

import os
import sys
import time
from abc import ABC, abstractmethod
from typing import Any, Dict
from logging import Logger
from pathlib import Path


class BaseSyncHandler(ABC):
    """Abstract base class for sync handlers."""
    
    def __init__(self, logger: Logger, config: Any):
        self.logger = logger
        self.config = config
        self._setup_path()
    
    def _setup_path(self):
        """Add dbconnector to path if needed."""
        dbconnector_path = Path(__file__).parent.parent / "dbconnector"
        if str(dbconnector_path) not in sys.path:
            sys.path.insert(0, str(dbconnector_path))
    
    @abstractmethod
    def handle_sync(self, sync_type: str = "all") -> Dict[str, Any]:
        """
        Handle synchronization.
        
        Args:
            sync_type: Type of sync to perform
        
        Returns:
            Result dictionary with status and details
        """
        pass
    
    def log_sync_start(self, sync_type: str):
        """Log sync start."""
        self.logger.info(f"=== Starting sync ===", extra={
            "sync_type": sync_type,
            "handler": self.__class__.__name__
        })
    
    def log_sync_end(self, sync_type: str, status: str = "success"):
        """Log sync end."""
        self.logger.info(f"=== Sync completed ===", extra={
            "sync_type": sync_type,
            "status": status,
            "handler": self.__class__.__name__
        })
    
    def log_script_start(self, script_path: str):
        """Log script execution start."""
        self.logger.info(f"▶ Starting script: {script_path}", extra={
            "script": script_path,
            "action": "script_start"
        })
    
    def log_script_end(self, script_path: str, duration_seconds: float = None, rows_loaded: int = None):
        """Log script execution end."""
        extra = {
            "script": script_path,
            "action": "script_end",
            "status": "success"
        }
        if duration_seconds is not None:
            extra["duration_seconds"] = round(duration_seconds, 2)
        if rows_loaded is not None:
            extra["rows_loaded"] = rows_loaded
        
        msg = f"✓ Script completed: {script_path}"
        if rows_loaded is not None:
            msg += f" | Rows loaded: {rows_loaded:,}"
        if duration_seconds is not None:
            msg += f" | Duration: {duration_seconds:.2f}s"
        
        self.logger.info(msg, extra=extra)
    
    def log_error(self, sync_type: str, error: Exception):
        """Log sync error."""
        self.logger.error(f"Sync failed", extra={
            "sync_type": sync_type,
            "error": str(error),
            "handler": self.__class__.__name__
        })
