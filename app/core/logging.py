import json
import logging
import logging.handlers
import sys
from datetime import UTC, datetime
from pathlib import Path

from .config import logger_settings


class JsonFormatter(logging.Formatter):
    """A simple JSON formatter for logging."""

    def __init__(self, date_format: str = "%Y-%m-%d %H:%M:%S"):
        super().__init__()
        self.date_format = date_format

    def format(self, record: logging.LogRecord) -> str:
        # Create a simple dictionary with key log information
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).strftime(
                self.date_format
            ),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Convert dictionary to JSON string
        return json.dumps(log_data)


class CsvFormatter(logging.Formatter):
    """A simple CSV formatter for logging."""

    def __init__(self, date_format: str = "%Y-%m-%d %H:%M:%S"):
        super().__init__()
        self.date_format = date_format

    def format(self, record: logging.LogRecord) -> str:
        # Format the timestamp
        timestamp = datetime.fromtimestamp(record.created, tz=UTC).strftime(
            self.date_format
        )

        # Basic CSV escape - double any quotes in the message
        message = record.getMessage().replace('"', '""')

        # Create a simple CSV row with basic log information
        return f'"{timestamp}","{record.levelname}","{record.name}","{message}"'


class TextFormatter(logging.Formatter):
    """A simple text formatter for logging."""

    def __init__(self, date_format: str = "%Y-%m-%d %H:%M:%S"):
        super().__init__()
        self.date_format = date_format

    def format(self, record: logging.LogRecord) -> str:
        # Format the timestamp
        timestamp = datetime.fromtimestamp(record.created, tz=UTC).strftime(
            self.date_format
        )

        # Create a formatted text string with key log information
        log_text = f"{timestamp} | {record.levelname:<8} | {record.name} | {record.getMessage()}"

        # Add exception info if present
        if record.exc_info:
            log_text += f"\n{self.formatException(record.exc_info)}"

        return log_text


def get_formatter(format_type: str) -> logging.Formatter:
    """Get a formatter based on the format type."""
    if format_type.lower() == "json":
        return JsonFormatter(date_format=logger_settings.date_format)
    elif format_type.lower() == "csv":
        return CsvFormatter(date_format=logger_settings.date_format)
    else:
        # Default to text formatter
        return TextFormatter(date_format=logger_settings.date_format)


def get_console_handler() -> logging.Handler:
    """Create a console handler for logging."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(get_formatter(logger_settings.format))
    return handler


def get_file_handler() -> logging.Handler | None:
    """Create a file handler for logging if file path is specified."""
    if not logger_settings.file:
        return None

    # Ensure parent directory exists
    file_path = Path(logger_settings.file)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Parse rotation settings
    when, interval = logger_settings.parse_rotation()
    backup_count = logger_settings.parse_retention(when)

    # Create timed rotating file handler
    handler = logging.handlers.TimedRotatingFileHandler(
        filename=str(file_path),
        when=when,
        interval=interval,
        backupCount=backup_count,
        encoding="utf-8",
    )

    handler.setFormatter(get_formatter(logger_settings.format))
    return handler


def get_syslog_handler() -> logging.Handler:
    """Create a syslog handler for logging."""
    try:
        handler = logging.handlers.SysLogHandler(address="/dev/log")
    except (FileNotFoundError, OSError):
        # Fallback for Windows or systems without /dev/log
        handler = logging.handlers.SysLogHandler()
    handler.setFormatter(get_formatter(logger_settings.format))
    return handler


def get_logger(name: str) -> logging.Logger:
    """Configure and return a logger based on settings."""
    logger = logging.getLogger(name)
    # Clear any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Set the log level
    logger.setLevel(logger_settings.get_log_level_int())

    # Add default handlers from config
    for handler_type in logger_settings.get_default_handlers():
        if handler_type == "console":
            logger.addHandler(get_console_handler())
        elif handler_type == "file":
            file_handler = get_file_handler()
            if file_handler:
                logger.addHandler(file_handler)
        elif handler_type == "syslog":
            logger.addHandler(get_syslog_handler())

    return logger
