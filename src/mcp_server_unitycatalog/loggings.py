"""Unity Catalog Model Context Protocol (MCP) Server Logging Utilities.

This module provides functions and configurations for setting up logging
throughout the application. It ensures that logs are consistently formatted
and handled according to the specified verbosity levels.

Features:
- Configures logging with different verbosity levels.
- Provides utility functions for structured logging.
- Ensures logs are written to the appropriate output streams.

License:
MIT License (c) 2025 Shingo OKAWA
"""

import logging
import sys
from datetime import datetime
from logging import FileHandler, Formatter, StreamHandler
from pathlib import Path
from .settings import get_settings as Settings


FORMAT = "%(asctime)s,%(msecs)d - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure(level: int) -> None:
    """Configures logging for the application, setting up both file-based and console-based handlers.

    This function creates a log file in the specified directory and logs
    messages to both the console and the file, using the specified log
    level.

    Args:
        level (int): The logging level to be used for both the file and console handlers.

    Returns:
        None
    """
    # Initializes logging directory.
    settings = Settings()
    log_directory = settings.uc_log_directory
    log_directory.mkdir(parents=True, exist_ok=True)
    # Configures file logger.
    file_handler = FileHandler(
        filename=f"{log_directory}/{datetime.now().strftime('%Y-%m-%d')}.log",
        encoding="utf-8",
        mode="a",
    )
    file_handler.setFormatter(Formatter(FORMAT, datefmt=DATE_FORMAT))
    # Configures stream logger.
    stream_handler = StreamHandler(sys.stderr)
    stream_handler.setFormatter(Formatter(FORMAT, datefmt=DATE_FORMAT))
    # Set up logging with both file and stream handlers.
    logging.basicConfig(handlers=(stream_handler, file_handler), level=level)
