"""Base.vn sync handler."""

from typing import Any, Dict
from logging import Logger
from handlers.base_handler import BaseSyncHandler
import importlib.util
import sys
import time
from pathlib import Path


class BaseVNHandler(BaseSyncHandler):
    """Handle Base.vn data synchronization."""
    
    # Map of sync types to script files
    SYNC_SCRIPTS = {
        "account": ["script_base_vn_account/users.py", "script_base_vn_account/groups.py"],
        "hrm": ["script_base_vn_hrm/employee.py", "script_base_vn_hrm/position.py", 
                "script_base_vn_hrm/team.py", "script_base_vn_hrm/office.py",
                "script_base_vn_hrm/area.py", "script_base_vn_hrm/contract_types.py",
                "script_base_vn_hrm/employee_types.py", "script_base_vn_hrm/employee_legals.py",
                "script_base_vn_hrm/insurance.py", "script_base_vn_hrm/tax.py",
                "script_base_vn_hrm/position_types.py", "script_base_vn_hrm/timesheet.py"],
        "payroll": ["script_base_vn_payroll/payroll.py", "script_base_vn_payroll/cycle.py",
                   "script_base_vn_payroll/record.py"],
        "hiring": ["script_base_vn_ehiring/candidate.py", "script_base_vn_ehiring/opening.py",
                  "script_base_vn_ehiring/pool.py", "script_base_vn_ehiring/interview.py",
                  "script_base_vn_ehiring/contact.py"],
        "checkin": ["script_base_vn_checkin/checkin.py"],
        "goal": ["script_base_vn_goal/goal.py", "script_base_vn_goal/cycle.py",
                "script_base_vn_goal/target.py", "script_base_vn_goal/goal_pd.py"],
        "timeoff": ["script_base_vn_timeoff/timeoff.py"],
        "schedule": ["script_base_vn_schedule/shift.py"],
    }
    
    def __init__(self, logger: Logger, config: Any):
        super().__init__(logger, config)
        self.base_path = Path(__file__).parent.parent
    
    def handle_sync(self, sync_type: str = "all") -> Dict[str, Any]:
        """Handle Base.vn synchronization."""
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
    
    def _get_all_scripts(self) -> list:
        """Get all Base.vn scripts."""
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
