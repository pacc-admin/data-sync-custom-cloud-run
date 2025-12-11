"""
Main entry point for Cloud Run application.
Handles HTTP requests and routes to appropriate handlers.
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify
from functools import wraps

# Add dbconnector and cloud_run_config to path
sys.path.insert(0, str(Path(__file__).parent / "dbconnector"))
sys.path.insert(0, str(Path(__file__).parent / "cloud_run_config"))

from cloud_run_config.logger import setup_logger
from cloud_run_config.config import get_config
from cloud_run_config.error_handler import CloudRunErrorHandler
from handlers.base_vn_handler import BaseVNHandler
from handlers.mssql_handler import MSSQLHandler
from handlers.ipos_handler import iPOSHandler
from handlers.worldfone_handler import WorldFoneHandler

# Initialize Flask app
app = Flask(__name__)
logger = setup_logger(__name__)
config = get_config()
error_handler = CloudRunErrorHandler()

# Initialize handlers
base_vn_handler = BaseVNHandler(logger, config)
mssql_handler = MSSQLHandler(logger, config)
ipos_handler = iPOSHandler(logger, config)
worldfone_handler = WorldFoneHandler(logger, config)


def require_auth(f):
    """Decorator to check Cloud Run authentication headers."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if config.get("DISABLE_AUTH", False):
            return f(*args, **kwargs)
        
        # In Cloud Run, check for identity token
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            logger.error("Missing or invalid authorization header")
            return jsonify({"error": "Unauthorized"}), 401
        
        # In production, verify the token with Cloud Identity
        # For now, just check its presence
        return f(*args, **kwargs)
    
    return decorated_function


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for Cloud Run."""
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()}), 200


@app.route("/sync/base-vn", methods=["POST"])
@require_auth
def sync_base_vn():
    """
    Trigger Base.vn synchronization.
    Request body: {"sync_type": "account|hrm|payroll|hiring|checkin|etc"}
    """
    try:
        data = request.get_json() or {}
        sync_type = data.get("sync_type", "all")
        
        logger.info(f"Starting Base.vn sync: {sync_type}")
        result = base_vn_handler.handle_sync(sync_type)
        
        return jsonify({
            "status": "success",
            "sync_type": sync_type,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        error_info = error_handler.handle_error(e, "base_vn_sync")
        logger.error(f"Base.vn sync failed: {error_info}")
        return jsonify(error_info), 500


@app.route("/sync/mssql", methods=["POST"])
@require_auth
def sync_mssql():
    """
    Trigger MSSQL synchronization.
    Request body: {"sync_type": "sale|warehouse|etc"}
    """
    try:
        data = request.get_json() or {}
        sync_type = data.get("sync_type", "all")
        
        logger.info(f"Starting MSSQL sync: {sync_type}")
        result = mssql_handler.handle_sync(sync_type)
        
        return jsonify({
            "status": "success",
            "sync_type": sync_type,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        error_info = error_handler.handle_error(e, "mssql_sync")
        logger.error(f"MSSQL sync failed: {error_info}")
        return jsonify(error_info), 500


@app.route("/sync/ipos", methods=["POST"])
@require_auth
def sync_ipos():
    """Trigger iPOS CRM synchronization."""
    try:
        data = request.get_json() or {}
        sync_type = data.get("sync_type", "all")
        
        logger.info(f"Starting iPOS sync: {sync_type}")
        result = ipos_handler.handle_sync(sync_type)
        
        return jsonify({
            "status": "success",
            "sync_type": sync_type,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        error_info = error_handler.handle_error(e, "ipos_sync")
        logger.error(f"iPOS sync failed: {error_info}")
        return jsonify(error_info), 500


@app.route("/sync/worldfone", methods=["POST"])
@require_auth
def sync_worldfone():
    """Trigger WorldFone synchronization."""
    try:
        data = request.get_json() or {}
        
        logger.info("Starting WorldFone sync")
        result = worldfone_handler.handle_sync()
        
        return jsonify({
            "status": "success",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        error_info = error_handler.handle_error(e, "worldfone_sync")
        logger.error(f"WorldFone sync failed: {error_info}")
        return jsonify(error_info), 500


@app.route("/sync/all", methods=["POST"])
@require_auth
def sync_all():
    """Trigger all synchronizations sequentially."""
    try:
        logger.info("Starting all syncs")
        results = {}
        
        # Run syncs sequentially
        try:
            results["base_vn"] = base_vn_handler.handle_sync("all")
        except Exception as e:
            results["base_vn"] = {"status": "failed", "error": str(e)}
            logger.error(f"Base.vn sync error: {e}")
        
        try:
            results["mssql"] = mssql_handler.handle_sync("all")
        except Exception as e:
            results["mssql"] = {"status": "failed", "error": str(e)}
            logger.error(f"MSSQL sync error: {e}")
        
        try:
            results["ipos"] = ipos_handler.handle_sync("all")
        except Exception as e:
            results["ipos"] = {"status": "failed", "error": str(e)}
            logger.error(f"iPOS sync error: {e}")
        
        try:
            results["worldfone"] = worldfone_handler.handle_sync()
        except Exception as e:
            results["worldfone"] = {"status": "failed", "error": str(e)}
            logger.error(f"WorldFone sync error: {e}")
        
        return jsonify({
            "status": "completed",
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        error_info = error_handler.handle_error(e, "all_sync")
        logger.error(f"All sync failed: {error_info}")
        return jsonify(error_info), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    logger.error(f"Server error: {error}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
