"""
Logging configuration for Kong Auth Service
Provides structured JSON logging with Sentry integration
"""

import json
import logging
import logging.config
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from pythonjsonlogger import jsonlogger

from .config import settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields"""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        """Add custom fields to log records"""
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp in ISO format
        if not log_record.get('timestamp'):
            log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Add service information
        log_record['service'] = settings.SERVICE_NAME
        log_record['environment'] = settings.ENVIRONMENT
        log_record['release'] = settings.APP_RELEASE
        
        # Add log level
        log_record['level'] = record.levelname
        
        # Add logger name
        log_record['logger'] = record.name
        
        # Add process and thread information
        log_record['process_id'] = record.process
        log_record['thread_id'] = record.thread
        
        # Add module and function information
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line_number'] = record.lineno
        
        # Add request context if available
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        
        if hasattr(record, 'path'):
            log_record['path'] = record.path
        
        if hasattr(record, 'method'):
            log_record['method'] = record.method
        
        if hasattr(record, 'status_code'):
            log_record['status_code'] = record.status_code
        
        if hasattr(record, 'duration_ms'):
            log_record['duration_ms'] = record.duration_ms
        
        if hasattr(record, 'client_ip'):
            log_record['client_ip'] = record.client_ip
        
        # Add user context if available
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id
        
        if hasattr(record, 'tenant_id'):
            log_record['tenant_id'] = record.tenant_id


class RequestIdFilter(logging.Filter):
    """Filter to add request ID to log records"""
    
    def __init__(self, name: str = ""):
        super().__init__(name)
        self.request_id = None
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add request ID to log record if available"""
        if hasattr(record, 'request_id'):
            record.request_id = getattr(record, 'request_id', 'unknown')
        return True


class SentryLoggingFilter(logging.Filter):
    """Filter to ensure ERROR and above logs are captured by Sentry"""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Ensure Sentry integration captures important logs"""
        # Sentry will automatically capture ERROR and above logs
        # This filter ensures proper context is available
        return True


def setup_logging() -> None:
    """Setup logging configuration"""
    
    # Determine log level
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Ensure logs directory exists
    import os
    logs_dir = settings.LOGS_DIR
    if not os.path.exists(logs_dir):
        try:
            os.makedirs(logs_dir, exist_ok=True)
            print(f"Created logs directory: {logs_dir}")
        except Exception as e:
            print(f"Warning: Could not create logs directory {logs_dir}: {e}")
            # Fall back to console-only logging if directory creation fails
            logs_dir = None
    
    # Configure logging
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": CustomJsonFormatter,
                "format": "%(timestamp)s %(level)s %(name)s %(message)s"
            },
            "simple": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "filters": {
            "request_id": {
                "()": RequestIdFilter
            },
            "sentry": {
                "()": SentryLoggingFilter
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "json" if settings.LOG_FORMAT == "json" else "simple",
                "filters": ["request_id", "sentry"],
                "stream": sys.stdout
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "json" if settings.LOG_FORMAT == "json" else "simple",
                "filters": ["request_id", "sentry"],
                "filename": f"{logs_dir}/app.log" if logs_dir else None,
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": logging.ERROR,
                "formatter": "json" if settings.LOG_FORMAT == "json" else "simple",
                "filters": ["request_id", "sentry"],
                "filename": f"{logs_dir}/error.log" if logs_dir else None,
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            }
        },
        "loggers": {
            "": {  # Root logger
                "level": log_level,
                "handlers": ["console", "file", "error_file"] if logs_dir else ["console"],
                "propagate": False
            },
            "app": {  # Application logger
                "level": log_level,
                "handlers": ["console", "file", "error_file"] if logs_dir else ["console"],
                "propagate": False
            },
            "uvicorn": {  # Uvicorn logger
                "level": log_level,
                "handlers": ["console", "file"] if logs_dir else ["console"],
                "propagate": False
            },
            "uvicorn.access": {  # Uvicorn access logger
                "level": log_level,
                "handlers": ["console", "file"] if logs_dir else ["console"],
                "propagate": False
            },
            "uvicorn.error": {  # Uvicorn error logger
                "level": log_level,
                "handlers": ["console", "file", "error_file"] if logs_dir else ["console"],
                "propagate": False
            },
            "fastapi": {  # FastAPI logger
                "level": log_level,
                "handlers": ["console", "file"] if logs_dir else ["console"],
                "propagate": False
            },
            "httpx": {  # HTTPX logger
                "level": logging.WARNING,
                "handlers": ["console", "file"] if logs_dir else ["console"],
                "propagate": False
            },
            "casdoor": {  # Casdoor logger
                "level": log_level,
                "handlers": ["console", "file"] if logs_dir else ["console"],
                "propagate": False
            }
        }
    }
    
    # Apply configuration
    logging.config.dictConfig(logging_config)
    
    # Set root logger level
    logging.getLogger().setLevel(log_level)
    
    # Ensure uvicorn access logs include request context
    _setup_uvicorn_access_logging()
    
    logger = logging.getLogger(__name__)
    logger.info(
        "Logging configured successfully",
        extra={
            "log_level": settings.LOG_LEVEL,
            "log_format": settings.LOG_FORMAT,
            "environment": settings.ENVIRONMENT
        }
    )


def _setup_uvicorn_access_logging() -> None:
    """Setup custom uvicorn access logging with request context"""
    
    class CustomAccessLogger:
        """Custom access logger that includes request context"""
        
        def __init__(self):
            self.logger = logging.getLogger("uvicorn.access")
        
        def log(self, request, response, duration: float):
            """Log request with additional context"""
            try:
                # Extract request information
                method = request.method
                path = request.url.path
                status_code = response.status_code
                duration_ms = round(duration * 1000, 2)
                
                # Get client IP
                client_ip = _get_client_ip(request)
                
                # Get request ID if available
                request_id = getattr(request.state, 'request_id', 'unknown') if hasattr(request, 'state') else 'unknown'
                
                # Get user context if available
                user_id = None
                tenant_id = None
                if hasattr(request, 'state') and hasattr(request.state, 'user') and request.state.user:
                    user = request.state.user
                    user_id = getattr(user, 'id', None)
                    tenant_id = getattr(user, 'organization', None)
                
                # Log the access
                self.logger.info(
                    f"{method} {path} {status_code}",
                    extra={
                        "request_id": request_id,
                        "method": method,
                        "path": path,
                        "status_code": status_code,
                        "duration_ms": duration_ms,
                        "client_ip": client_ip,
                        "user_id": user_id,
                        "tenant_id": tenant_id,
                        "user_agent": request.headers.get("user-agent", ""),
                        "content_length": len(response.body) if hasattr(response, 'body') else 0
                    }
                )
                
            except Exception as e:
                # Fallback to basic logging if context extraction fails
                self.logger.info(f"{request.method} {request.url.path} {response.status_code}")
    
    # Replace uvicorn's default access logger
    try:
        import uvicorn.logging
        uvicorn.logging.AccessLogger = CustomAccessLogger
    except ImportError:
        pass


def _get_client_ip(request) -> str:
    """Extract client IP address from request"""
    try:
        # Check various headers for client IP
        headers_to_check = [
            'X-Forwarded-For',
            'X-Real-IP',
            'X-Client-IP',
            'CF-Connecting-IP',  # Cloudflare
            'True-Client-IP',    # Akamai
        ]
        
        for header in headers_to_check:
            if header in request.headers:
                ip = request.headers[header].split(',')[0].strip()
                if ip and ip != 'unknown':
                    return ip
        
        # Fallback to direct connection
        if hasattr(request, 'client') and request.client:
            return request.client.host
        
        return "unknown"
        
    except Exception:
        return "unknown"


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def log_request_start(request, logger: Optional[logging.Logger] = None) -> None:
    """
    Log the start of a request
    
    Args:
        request: FastAPI request object
        logger: Optional logger instance
    """
    if logger is None:
        logger = get_logger(__name__)
    
    try:
        request_id = getattr(request.state, 'request_id', 'unknown') if hasattr(request, 'state') else 'unknown'
        client_ip = _get_client_ip(request)
        
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client_ip": client_ip,
                "user_agent": request.headers.get("user-agent", ""),
                "query_params": dict(request.query_params),
                "headers": dict(request.headers)
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to log request start: {e}")


def log_request_end(request, response, duration: float, logger: Optional[logging.Logger] = None) -> None:
    """
    Log the end of a request
    
    Args:
        request: FastAPI request object
        response: FastAPI response object
        duration: Request duration in seconds
        logger: Optional logger instance
    """
    if logger is None:
        logger = get_logger(__name__)
    
    try:
        request_id = getattr(request.state, 'request_id', 'unknown') if hasattr(request, 'state') else 'unknown'
        duration_ms = round(duration * 1000, 2)
        
        logger.info(
            f"Request completed: {request.method} {request.url.path} {response.status_code}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "content_length": len(response.body) if hasattr(response, 'body') else 0
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to log request end: {e}")


def log_error(error: Exception, request=None, logger: Optional[logging.Logger] = None) -> None:
    """
    Log an error with context
    
    Args:
        error: The exception that occurred
        request: Optional FastAPI request object for context
        logger: Optional logger instance
    """
    if logger is None:
        logger = get_logger(__name__)
    
    try:
        extra = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "exception_type": type(error).__name__,
            "exception_message": str(error)
        }
        
        if request:
            extra.update({
                "request_id": getattr(request.state, 'request_id', 'unknown') if hasattr(request, 'state') else 'unknown',
                "method": request.method,
                "path": request.url.path,
                "client_ip": _get_client_ip(request)
            })
        
        logger.error(
            f"Error occurred: {type(error).__name__}: {str(error)}",
            extra=extra,
            exc_info=True
        )
        
    except Exception as e:
        logger.error(f"Failed to log error: {e}")


# Initialize logging when module is imported
setup_logging() 