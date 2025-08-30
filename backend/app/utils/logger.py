import sys
import json
from pathlib import Path
from loguru import logger
from app.core.config import settings

class InterceptHandler:
    """Intercept standard logging messages and redirect them to loguru"""
    
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == __file__:
            frame = frame.f_back
            depth += 1
        
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

def setup_logging():
    """Setup structured logging with Loguru"""
    
    # Remove default handler
    logger.remove()
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Console logging with colors
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO" if not settings.DEBUG else "DEBUG",
        colorize=True
    )
    
    # File logging for all levels
    logger.add(
        log_dir / "dristhi.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        serialize=False
    )
    
    # Error logging with detailed information
    logger.add(
        log_dir / "errors.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="5 MB",
        retention="90 days",
        compression="zip",
        serialize=False
    )
    
    # JSON logging for production
    if not settings.DEBUG:
        logger.add(
            log_dir / "dristhi.json",
            format=lambda record: json.dumps({
                "timestamp": record["time"].isoformat(),
                "level": record["level"].name,
                "logger": record["name"],
                "function": record["function"],
                "line": record["line"],
                "message": record["message"],
                "extra": record["extra"]
            }),
            level="INFO",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            serialize=True
        )
    
    # Intercept standard logging
    import logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Intercept specific loggers
    for logger_name in ("uvicorn", "uvicorn.error", "fastapi", "sqlalchemy"):
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]
    
    return logger

def get_logger(name: str):
    """Get a logger instance for a specific module"""
    return logger.bind(name=name)

# Contextual logging for user actions
def log_user_action(user_id: int, action: str, details: dict = None):
    """Log user actions with context"""
    extra = {"user_id": user_id, "action": action}
    if details:
        extra.update(details)
    
    logger.info(f"User action: {action}", extra=extra)

def log_api_request(method: str, path: str, user_id: int = None, status_code: int = None, duration: float = None):
    """Log API requests with performance metrics"""
    extra = {
        "method": method,
        "path": path,
        "user_id": user_id,
        "status_code": status_code,
        "duration_ms": duration * 1000 if duration else None
    }
    
    logger.info(f"API Request: {method} {path}", extra=extra)

def log_ai_interaction(user_id: int, interaction_type: str, model: str, duration: float, success: bool):
    """Log AI service interactions"""
    extra = {
        "user_id": user_id,
        "interaction_type": interaction_type,
        "model": model,
        "duration_ms": duration * 1000,
        "success": success
    }
    
    logger.info(f"AI Interaction: {interaction_type} with {model}", extra=extra)

def log_database_operation(operation: str, table: str, user_id: int = None, duration: float = None):
    """Log database operations"""
    extra = {
        "operation": operation,
        "table": table,
        "user_id": user_id,
        "duration_ms": duration * 1000 if duration else None
    }
    
    logger.info(f"Database: {operation} on {table}", extra=extra)

def log_security_event(event_type: str, user_id: int = None, ip_address: str = None, details: dict = None):
    """Log security-related events"""
    extra = {
        "event_type": event_type,
        "user_id": user_id,
        "ip_address": ip_address
    }
    if details:
        extra.update(details)
    
    logger.warning(f"Security Event: {event_type}", extra=extra)

def log_performance_metric(metric_name: str, value: float, unit: str = None, tags: dict = None):
    """Log performance metrics"""
    extra = {
        "metric_name": metric_name,
        "value": value,
        "unit": unit,
        "tags": tags or {}
    }
    
    logger.info(f"Performance: {metric_name} = {value}{unit or ''}", extra=extra)

# Initialize logging
setup_logging()
