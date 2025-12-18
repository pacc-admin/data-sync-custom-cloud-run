"""iPOS CRM sync handler."""

from typing import Any, Dict
from logging import Logger
from handlers.base_handler import BaseSyncHandler
import importlib.util
import sys
import time
from pathlib import Path


class iPOSHandler(BaseSyncHandler):
    """Handle iPOS CRM data synchronization."""
    
    # Script files for iPOS
    SYNC_SCRIPTS = {
        "all": [
            "script_ipos_crm/campaigns.py",
            "script_ipos_crm/membership_insert_bgn.py",
            "script_ipos_crm/membership_insert_5wine.py",
            "script_ipos_crm/voucher_insert_bgn.py",
            "script_ipos_crm/voucher_insert_5wine.py",
        ]
    }
    
    def __init__(self, logger: Logger, config: Any):
        super().__init__(logger, config)
        self.base_path = Path(__file__).parent.parent
    
    def handle_sync(self, sync_type: str = "all") -> Dict[str, Any]:
        """Handle iPOS synchronization."""
        self.log_sync_start(sync_type)
        results = {}
        
        try:
            scripts = self.SYNC_SCRIPTS.get(sync_type, self.SYNC_SCRIPTS.get("all", []))
            
            if not scripts:
                raise ValueError(f"Unknown sync type: {sync_type}")
            
            for script_path in scripts:
                try:
                    result = self._run_script(script_path)
                    results[script_path] = result
                    # log_script_end được gọi trong _run_script
                except Exception as e:
                    error_msg = f"✗ Script failed: {script_path} - {str(e)}"
                    self.logger.error(error_msg, extra={"script": script_path, "action": "script_error"})
                    results[script_path] = {"status": "failed", "error": str(e)}
            
            self.log_sync_end(sync_type, "completed")
            return {
                "status": "success",
                "sync_type": sync_type,
                "scripts_run": len(results),
                "results": results
            }
        
        except Exception as e:
            self.log_error(sync_type, e)
            return {
                "status": "failed",
                "sync_type": sync_type,
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

            # Một số script iPOS dùng hàm `__main__`, một số có thể dùng `main`
            # Khi import thì block `if __name__ == '__main__':` không chạy,
            # nên ta chủ động gọi hàm chính nếu có.
            if hasattr(module, "main") and callable(getattr(module, "main")):
                self.logger.debug("Calling script main()", extra={"script": script_path})
                module.main()
            elif hasattr(module, "__main__") and callable(getattr(module, "__main__")):
                self.logger.debug("Calling script __main__()", extra={"script": script_path})
                module.__main__()
            
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
