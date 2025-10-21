"""Logger configuration with loguru and colorful output."""

from loguru import logger
from pydantic import BaseModel, Field

from synx.config import LogLevel


class LogConfig(BaseModel):
    """Logger configuration model."""

    level: LogLevel = Field(default=LogLevel.INFO, description="Log level")
    format: str = Field(
        default="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        description="Log format string",
    )
    colorize: bool = Field(default=True, description="Enable colorized output")

    def __str__(self) -> str:
        """String representation of LogConfig."""
        return f"LogConfig(level={self.level}, format='{self.format[:50]}...', colorize={self.colorize})"


def setup_logger(config: LogConfig | None = None) -> None:
    """Configure loguru logger with custom colors and formatting.

    Args:
        config: Optional logger configuration. If None, uses default settings.
    """
    if config is None:
        config = LogConfig()

    # Remove default handler
    logger.remove()

    # Add console handler with custom colors
    logger.add(
        sink=lambda msg: print(msg, end=""),
        level=config.level.value,
        format=config.format,
        colorize=config.colorize,
        backtrace=True,
        diagnose=True,
    )


def get_logger():
    """Get configured logger instance.

    Returns:
        Configured loguru logger instance.
    """
    return logger


# Initialize logger with default configuration
setup_logger()
