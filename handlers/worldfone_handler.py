"""WorldFone sync handler."""

from typing import Any, Dict
from logging import Logger
from handlers.base_handler import BaseSyncHandler
import importlib.util
import sys
import time
from pathlib import Path


class WorldFoneHandler(BaseSyncHandler):
    """Handle WorldFone data synchronization."""
    
    # Script files for WorldFone
    SYNC_SCRIPTS = [
        "script_worldfone/cdrs_historical.py"
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
                    # log_script_end được gọi trong _run_script
                except Exception as e:
                    error_msg = f"✗ Script failed: {script_path} - {str(e)}"
                    self.logger.error(error_msg, extra={"script": script_path, "action": "script_error"})
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
        
        # Log script start
        self.log_script_start(script_path)
        start_time = time.time()
        
        try:
            # Load and execute the module
            spec = importlib.util.spec_from_file_location(
                full_path.stem,
                full_path
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[full_path.stem] = module
            spec.loader.exec_module(module)

            # Nếu script có hàm main(), gọi để đảm bảo logic chính được chạy
            if hasattr(module, "main") and callable(getattr(module, "main")):
                self.logger.debug("Calling script main()", extra={"script": script_path})
                module.main()
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log script end with timing
            self.log_script_end(script_path, duration_seconds=duration)
            
            return {
                "status": "success",
                "script": script_path,
                "duration_seconds": round(duration, 2)
            }
        
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"✗ Script execution error: {script_path} | Duration: {duration:.2f}s", extra={
                "script": script_path,
                "error": str(e),
                "duration_seconds": round(duration, 2),
                "action": "script_error"
            })
            raise
