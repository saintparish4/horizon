import logging
import sys 
import json 
from datetime import datetime
from typing import Any, Dict 

class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno, 
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data)

def init_logging(service_name: str, log_level: str = "INFO") -> None:
    """
    Initialize structured logging for the service

    Args:
        service_name: Name of the service
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler with JSON formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)

    # Log Initialization
    logger.info(
        f"Logging initialized for {service_name}",
        extra={"extra_fields": {"service": service_name}}
    )

def get_logger(name: str) -> logging.Logger:
    """ Get a logger instance with the given name """
    return logging.getLogger(name)