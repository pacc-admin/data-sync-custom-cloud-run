"""MSSQL sync handler."""

from typing import Any, Dict
from logging import Logger
from handlers.base_handler import BaseSyncHandler
import importlib.util
import sys
from pathlib import Path


class MSSQLHandler(BaseSyncHandler):
    """Handle MSSQL data synchronization."""
    
    # Map of sync types to script files
    SYNC_SCRIPTS = {
        "sale": [
            "script_mssql_sale/sale.py",
            "script_mssql_sale/sale_detail.py",
            "script_mssql_sale/dm_item.py",
            "script_mssql_sale/dm_membership_type.py",
            "script_mssql_sale/dm_membership_discount.py",
            "script_mssql_sale/order_menu_log.py",
            "script_mssql_sale/dm_extra_2.py",
        ],
        "dedup": [
            "script_dedup_mssql_acc/sale_detail_dedup.py",
            "script_dedup_mssql_acc/ledger_dedup.py",
            "script_dedup_mssql_acc/warehouse_dedup.py",
        ]
    }
    
    def __init__(self, logger: Logger, config: Any):
        super().__init__(logger, config)
        self.base_path = Path(__file__).parent.parent
    
    def handle_sync(self, sync_type: str = "all") -> Dict[str, Any]:
        """Handle MSSQL synchronization."""
        self.log_sync_start(sync_type)
        results = {}
        
        try:
            if sync_type == "all":
                scripts = self._get_all_scripts()
            else:
                scripts = self.SYNC_SCRIPTS.get(sync_type, [])
            
            if not scripts:
                raise ValueError(f"Unknown sync type: {sync_type}")
            
            for script_path in scripts:
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
            
            # Nếu có script nào failed, trả về failed
            failed_scripts = [s for s, r in results.items() if r.get("status") != "success"]
            if failed_scripts:
                self.log_sync_end(sync_type, "failed")
                return {
                    "status": "failed",
                    "sync_type": sync_type,
                    "scripts_run": len(results),
                    "results": results
                }
            
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
    
    def _get_all_scripts(self) -> list:
        """Get all MSSQL scripts."""
        scripts = []
        for script_list in self.SYNC_SCRIPTS.values():
            scripts.extend(script_list)
        return scripts
    
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
