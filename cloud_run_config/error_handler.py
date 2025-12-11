"""Error handling for Cloud Run."""

import traceback
from typing import Any, Dict
from datetime import datetime


class CloudRunErrorHandler:
    """Handle and format errors for Cloud Run."""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
    
    def handle_error(
        self,
        error: Exception,
        context: str = "unknown",
        extra_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Format error for Cloud Run response.
        
        Args:
            error: The exception that occurred
            context: Context about what operation failed
            extra_info: Additional information to include
        
        Returns:
            Formatted error dict
        """
        error_info = {
            "error": str(error),
            "error_type": type(error).__name__,
            "context": context,
            "timestamp": datetime.utcnow().isoformat(),
            "traceback": traceback.format_exc()
        }
        
        if extra_info:
            error_info.update(extra_info)
        
        return error_info
    
    def should_retry(self, error: Exception) -> bool:
        """
        Determine if an error is retryable.
        
        Args:
            error: The exception to check
        
        Returns:
            True if the error should be retried
        """
        retryable_errors = (
            ConnectionError,
            TimeoutError,
            IOError,
            OSError,
        )
        
        # Check error type
        if isinstance(error, retryable_errors):
            return True
        
        # Check error message for common retryable patterns
        error_str = str(error).lower()
        retryable_patterns = [
            "connection",
            "timeout",
            "temporarily unavailable",
            "try again",
            "429",  # Too many requests
            "503",  # Service unavailable
        ]
        
        return any(pattern in error_str for pattern in retryable_patterns)
    
    def format_retry_error(self, error: Exception, retry_count: int) -> Dict[str, Any]:
        """Format error after retries exhausted."""
        return {
            "error": str(error),
            "error_type": type(error).__name__,
            "retries_exhausted": retry_count,
            "message": f"Operation failed after {retry_count} retries",
            "timestamp": datetime.utcnow().isoformat()
        }
