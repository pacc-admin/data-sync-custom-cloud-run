import argparse
import logging
import sys
import os
from pathlib import Path

# Add paths for modules
sys.path.insert(0, str(Path(__file__).parent / "dbconnector"))
sys.path.insert(0, str(Path(__file__).parent / "cloud_run_config"))

from cloud_run_config.logger import setup_logger
from cloud_run_config.config import get_config
from handlers.base_vn_handler import BaseVNHandler
from handlers.mssql_handler import MSSQLHandler
from handlers.ipos_handler import iPOSHandler
from handlers.worldfone_handler import WorldFoneHandler
from handlers.google_sheet_handler import GoogleSheetHandler
from handlers.minvoice_handler import MinvoiceHandler

# Setup Logger
# Lưu ý: Cloud Run Jobs sẽ hứng log từ stdout/stderr
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("JobRunner")

def main():
    # 1. Cấu hình nhận tham số từ dòng lệnh
    parser = argparse.ArgumentParser(description='Cloud Run Job Entrypoint')
    parser.add_argument('--handler', required=True, help='Tên handler: mssql, ipos, base_vn, worldfone, google_sheet, minvoice')
    parser.add_argument('--type', default='all', help='Loại sync (vd: all, sale, crm...)')
    
    args = parser.parse_args()
    
    # Load Config
    config = get_config()
    
    logger.info(f"--- STARTING JOB ---")
    logger.info(f"Handler: {args.handler}")
    logger.info(f"Sync Type: {args.type}")

    try:
        result = None
        
        # 2. Router: Chọn Handler dựa vào tham số --handler
        if args.handler == 'base_vn':
            handler = BaseVNHandler(logger, config)
            result = handler.handle_sync(sync_type=args.type)
            
        elif args.handler == 'mssql':
            handler = MSSQLHandler(logger, config)
            result = handler.handle_sync(sync_type=args.type)
            
        elif args.handler == 'ipos':
            handler = iPOSHandler(logger, config)
            result = handler.handle_sync(sync_type=args.type)
            
        elif args.handler == 'worldfone':
            handler = WorldFoneHandler(logger, config)
            # Worldfone handler trong code cũ của bạn không nhận tham số sync_type
            result = handler.handle_sync()

        elif args.handler == 'google_sheet':
            handler = GoogleSheetHandler(logger, config)
            result = handler.handle_sync(sync_type=args.type)
            
        elif args.handler == 'minvoice':
            handler = MinvoiceHandler(logger, config)
            result = handler.handle_sync(sync_type=args.type)
            
        else:
            logger.error(f"Unknown handler specified: {args.handler}")
            sys.exit(1) # Thoát với lỗi

        # 3. Kết thúc
        logger.info(f"Job Finished Successfully. Result: {result}")
        sys.exit(0) # Thoát thành công

    except Exception as e:
        logger.exception(f"CRITICAL ERROR: Job failed - {str(e)}")
        sys.exit(1) # Thoát với lỗi để Cloud Run báo đỏ

if __name__ == "__main__":
    main()