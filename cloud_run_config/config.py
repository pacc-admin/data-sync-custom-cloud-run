"""Configuration management for Cloud Run."""

import os
import json
from typing import Any, Dict, Optional

try:
    from google.cloud import secretmanager
except ImportError:
    secretmanager = None


class CloudRunConfig:
    """Centralized configuration management."""
    
    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from environment variables and Secret Manager."""
        # Load from environment
        self._config = dict(os.environ)
        
        # Try to load from Secret Manager if in Cloud Run
        if os.getenv("CLOUD_RUN", False):
            self._load_from_secret_manager()
    
    def _load_from_secret_manager(self):
        """Load secrets from Google Secret Manager."""
        if not secretmanager:
            return
        
        try:
            project_id = os.getenv("GCP_PROJECT_ID")
            if not project_id:
                return
            
            client = secretmanager.SecretManagerServiceClient()
            
            # List of secrets to load
            secrets = [
                "base-vn-token",
                "worldfone-key",
                "mssql-connection",
                "bq-project-id"
            ]
            
            for secret_name in secrets:
                try:
                    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
                    response = client.access_secret_version(request={"name": name})
                    self._config[secret_name] = response.payload.data.decode("UTF-8")
                except Exception as e:
                    print(f"Warning: Could not load secret {secret_name}: {e}")
        
        except Exception as e:
            print(f"Warning: Could not connect to Secret Manager: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)
    
    def get_json(self, key: str, default: Optional[Dict] = None) -> Dict:
        """Get configuration value as JSON."""
        value = self._config.get(key)
        if not value:
            return default or {}
        
        try:
            if isinstance(value, str):
                return json.loads(value)
            return value
        except (json.JSONDecodeError, ValueError):
            return default or {}
    
    def __getitem__(self, key: str) -> Any:
        """Support dict-style access."""
        return self._config.get(key)
    
    def __setitem__(self, key: str, value: Any):
        """Support dict-style assignment."""
        self._config[key] = value


def get_config() -> CloudRunConfig:
    """Get or create the global config instance."""
    global _config_instance
    if '_config_instance' not in globals():
        _config_instance = CloudRunConfig()
    return _config_instance


# Default configuration
DEFAULT_CONFIG = {
    "LOG_LEVEL": "INFO",
    "CLOUD_RUN": True,
    "DISABLE_AUTH": False,
    "MAX_RETRIES": 3,
    "RETRY_DELAY": 5,
    "REQUEST_TIMEOUT": 300,
    "BATCH_SIZE": 1000,
}
