import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
import logging.config
import json
from typing import Optional

from infrastructure.config.app_config import AppConfig

# Proje kök dizinini bularak 'logs' klasörünün yolunu doğru bir şekilde belirle
# __file__ -> src_clean/infrastructure/logging/logger_setup.py
# dirname(__file__) -> src_clean/infrastructure/logging
# dirname(dirname(dirname...))) -> edevlet-automazition
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'logs')

# Log klasörü yoksa oluştur
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Okunabilir JSON formatlayıcısı - insan dostu zaman formatı ile."""
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # İnsan dostu zaman formatı ekle
        from datetime import datetime
        dt = datetime.fromtimestamp(record.created)
        log_record['time'] = dt.strftime('%Y-%m-%d %H:%M:%S')
        log_record['unix_timestamp'] = record.created
        
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname

def _create_handler(filename: str, max_bytes: int = 10*1024*1024, backup_count: int = 5) -> RotatingFileHandler:
    """Belirtilen dosya için bir RotatingFileHandler oluşturur."""
    handler = RotatingFileHandler(
        os.path.join(LOG_DIR, filename),
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    formatter = CustomJsonFormatter(
        '%(time)s %(level)s %(name)s %(message)s'
    )
    handler.setFormatter(formatter)
    return handler

def setup_logging(log_path: Optional[str] = None) -> None:
    """
    Set up application-wide logging with JSON format.

    Args:
        log_path: Optional path to a specific log file.
                  If not provided, defaults to 'app.log' in the configured LOGS_DIR.
    """
    # Ensure logs directory exists
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR, exist_ok=True)
        
    # Determine log file path
    if log_path:
        default_log_file = log_path
    else:
        default_log_file = os.path.join(LOG_DIR, "app.log")

    # Base logging configuration
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json_formatter": {
                "()": CustomJsonFormatter,
                "format": "%(time)s %(level)s %(name)s %(message)s"
            }
        },
        "handlers": {
            "console": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "json_formatter"
            },
            "file": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": default_log_file,
                "maxBytes": 10*1024*1024,
                "backupCount": 5,
                "formatter": "json_formatter"
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["console", "file"]
        }
    }

    logging.config.dictConfig(logging_config)

    logging.getLogger('root').info("Yapılandırılmış, çoklu dosya loglama sistemi başarıyla kuruldu.") 