import os
import sys

from loguru import logger as _logger


class Logger:
    _instance = None

    @classmethod
    def get_logger(cls):
        """Get or create singleton logger instance"""
        if cls._instance is None:
            # Configure logger with default settings
            _logger.remove()  # Remove default handler
            _logger.add(
                sink=sys.stdout,
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
                colorize=True,
                level=os.getenv("LOG_LEVEL", "INFO").upper(),
            )
            cls._instance = _logger

        return cls._instance


# Create global logger instance
logger = Logger.get_logger()
