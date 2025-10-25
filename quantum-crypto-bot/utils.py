import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging():
    """Profesyonel log sistemi"""
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    log_filename = f"logs/bot_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.handlers.RotatingFileHandler(
                log_filename, maxBytes=5*1024*1024, backupCount=5
            ),
            logging.StreamHandler()
        ]
    )

def log_performance(func):
    """Performans logger decorator"""
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.now()
        logging.info(f"⏱️ {func.__name__} - Süre: {(end_time - start_time).total_seconds():.2f}s")
        return result
    return wrapper