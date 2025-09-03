# application/app/settings/base.py
import logging
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings as BASettings, SettingsConfigDict

# Compute root dir (application/)
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


class BaseConfigSettings(BASettings):
    """Base settings with shared configuration"""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_prefix="APP_",
    )


class AppSettings(BaseConfigSettings):
    """Application settings configuration."""

    # Basic app info
    name: str = Field(default="FastAPI Tutorial")
    version: str = Field(default="0.1.0")
    description: str = Field(default="A simple FastAPI application")
    debug: bool = Field(default=True)

    # Server settings
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000)
    reload: bool = Field(default=True)

    # API documentation URLs
    api_docs_url: str = Field(default="/docs")
    redoc_url: str = Field(default="/redoc")
    scalar_url: str = Field(default="/scalar")
    openapi_url: str = Field(default="/openapi.json")

    # ✅ Pydantic v2 way: model_config replaces `class Config`
    model_config = BaseConfigSettings.model_config | SettingsConfigDict(
        env_prefix="APP_",  # specific to this class
    )


class LoggerSettings(BaseConfigSettings):
    """Logger settings configuration loaded from LOG_* env vars."""

    # LOG_LEVEL
    level: Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"] = Field(
        default="INFO"
    )

    # LOG_FORMAT: 'json', 'text', or 'csv'
    format: Literal["json", "text", "csv"] = Field(default="text")

    # LOG_FILE: filesystem path or None
    file: Path | None = Field(default=None)

    # LOG_RETENTION, LOG_ROTATION: e.g. '7d', '1d'
    retention: str | None = Field(default=None)
    rotation: str | None = Field(default=None)

    # LOG_HANDLERS: e.g. 'console,file'
    @staticmethod
    def get_default_handlers() -> list[Literal["console", "file", "syslog"]]:
        return ["console"]

    # Accept a comma-separated string (e.g., "console,file") or a list
    handlers: list[Literal["console", "file", "syslog"]] | str = Field(
        default_factory=get_default_handlers
    )

    # LOG_DATE_FORMAT: e.g. '%Y-%m-%d %H:%M:%S'
    date_format: str = Field(default="%Y-%m-%d %H:%M:%S")

    # Optional text log message format
    message_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Apply LOG_ prefix
    model_config = BaseConfigSettings.model_config | SettingsConfigDict(
        env_prefix="LOG_",
    )

    @field_validator("level", mode="before")
    @classmethod
    def _normalize_level(cls, v: str) -> str:
        if isinstance(v, str):
            return v.upper()
        return v

    @field_validator("handlers", mode="before")
    @classmethod
    def _parse_handlers(cls, v: str | list[str] | None) -> list[str]:
        """Allow LOG_HANDLERS to be provided as a comma-separated string or a JSON list."""
        if isinstance(v, str):
            return [h.strip() for h in v.split(",") if h.strip()]
        return v if isinstance(v, list) else []

    @field_validator("file", mode="before")
    @classmethod
    def _pathify(cls, v: str | Path | None) -> Path | None:
        if isinstance(v, str) and v.strip():
            return Path(v)
        if isinstance(v, Path):
            return v
        return None

    def get_log_level_int(self) -> int:
        """Convert string log level to Python logging level integer."""
        log_levels = {
            "CRITICAL": logging.CRITICAL,
            "ERROR": logging.ERROR,
            "WARNING": logging.WARNING,
            "INFO": logging.INFO,
            "DEBUG": logging.DEBUG,
            "NOTSET": logging.NOTSET,
        }
        return log_levels.get(self.level, logging.INFO)

    def parse_rotation(self) -> tuple[str, int]:
        """
        Parse rotation setting (e.g., '1d', '7d', '12h')
        Returns:
            Tuple of (when, interval) for TimedRotatingFileHandler
        """
        if not self.rotation:
            return ("D", 1)  # Default: daily rotation

        s = self.rotation.strip().lower()
        if not s or not s[:-1].isdigit() or s[-1] not in {"s", "m", "h", "d", "w"}:
            return ("D", 1)  # Invalid format, use default

        n = int(s[:-1])
        unit = s[-1]

        if unit == "s":
            return ("S", n)  # Seconds
        if unit == "m":
            return ("M", n)  # Minutes
        if unit == "h":
            return ("H", n)  # Hours
        if unit == "d":
            return ("D", n)  # Days
        if unit == "w":
            return ("W0", n)  # Weeks (0=Monday)

        return ("D", 1)  # Default: daily rotation

    def parse_retention(self, rotation_when: str) -> int:
        """
        Parse retention setting (e.g., '7d', '30d')
        Returns:
            Number of backup files to keep
        """
        if not self.retention:
            return 7  # Default: keep 7 backup files

        s = self.retention.strip().lower()
        if not s or not s[:-1].isdigit() or s[-1] not in {"s", "m", "h", "d", "w"}:
            return 7  # Invalid format, use default

        n = int(s[:-1])
        return n


class DatabaseSettings(BaseConfigSettings):
    """Database settings configuration."""

    host: str = Field(default="localhost")
    port: int = Field(default=27019)
    name: str = Field(default="mydb")
    user: str = Field(default="root")
    password: str = Field(default="example")
    auth_source: str = Field(default="admin")

    @property
    def collection_name(self) -> str:
        """Return the name of the MongoDB collection."""
        return self.name

    @property
    def connection_url(self) -> str:
        """Return MongoDB connection URL."""
        return f"mongodb://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}?authSource={self.auth_source}"

    #  Pydantic v2 way: model_config replaces `class Config`
    model_config = BaseConfigSettings.model_config | SettingsConfigDict(
        env_prefix="DATABASE_",
    )


# Create settings instance
database_settings = DatabaseSettings()

# Create logger settings instance
logger_settings = LoggerSettings()

# Create settings instance
app_settings = AppSettings()
