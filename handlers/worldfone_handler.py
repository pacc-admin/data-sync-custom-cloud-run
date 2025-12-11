"""WorldFone sync handler."""

from typing import Any, Dict
from logging import Logger
from handlers.base_handler import BaseSyncHandler
import importlib.util
import sys
from pathlib import Path


class WorldFoneHandler(BaseSyncHandler):
    """Handle WorldFone data synchronization."""
    
    # Script files for WorldFone
    SYNC_SCRIPTS = [
        "script_worldfone/cdrs_historical.py",
        "script_worldfone/cdrs.py",
    ]
    
    def __init__(self, logger: Logger, config: Any):
        super().__init__(logger, config)
        self.base_path = Path(__file__).parent.parent
    
    def handle_sync(self, sync_type: str = "all") -> Dict[str, Any]:
        """Handle WorldFone synchronization."""
        self.log_sync_start("worldfone")
        results = {}
        
        try:
            for script_path in self.SYNC_SCRIPTS:
                try:
                    result = self._run_script(script_path)
                    results[script_path] = result
                    self.logger.info(f"Script completed", extra={
                        "script": script_path,
                        "status": "success"
                    })
                except Exception as e:
                    error_msg = f"Script failed: {script_path} - {str(e)}"
                    self.logger.error(error_msg, extra={"script": script_path})
                    results[script_path] = {"status": "failed", "error": str(e)}
            
            self.log_sync_end("worldfone", "completed")
            return {
                "status": "success",
                "scripts_run": len(results),
                "results": results
            }
        
        except Exception as e:
            self.log_error("worldfone", e)
            return {
                "status": "failed",
                "error": str(e),
                "results": results
            }
    
    def _run_script(self, script_path: str) -> Dict[str, Any]:
        """
        Run a Python script dynamically.
        
        Args:
            script_path: Relative path to script from repo root
        
        Returns:
            Result dictionary
        """
        full_path = self.base_path / script_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")
        
        self.logger.debug(f"Running script", extra={"script": script_path})
        
        try:
            # Load and execute the module
            spec = importlib.util.spec_from_file_location(
                full_path.stem,
                full_path
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[full_path.stem] = module
            spec.loader.exec_module(module)
            
            return {
                "status": "success",
                "script": script_path
            }
        
        except Exception as e:
            self.logger.error(f"Script execution error", extra={
                "script": script_path,
                "error": str(e)
            })
            raise
