"""Unity Catalog Model Context Protocol (MCP) Server Bootstrap Utilities.

This module provides functions and configurations for setting up configurations
throughout the application.

Features:
- Configures logging with different verbosity levels.

License:
MIT License (c) 2025 Shingo OKAWA
"""

import logging
import sys
from datetime import datetime
from logging import FileHandler, Formatter, StreamHandler
from pathlib import Path
from .settings import Settings


# Defines logging format.
FORMAT = "%(asctime)s,%(msecs)d - %(name)s - %(levelname)s - %(message)s"
# Defines logging date format.
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def bootstrap(settings: Settings) -> None:
    """Initializes the logging configuration by setting up both file and stream handlers.

    This function configures the logging system with a file handler that writes logs
    to a specified directory and a stream handler that outputs logs to the standard error stream.
    It uses the verbosity level specified in the settings to set the logging level and ensures
    the log directory exists before creating the log file. The file handler logs messages to a daily
    log file named with the current date, while the stream handler outputs log messages to stderr.

    Args:
        settings (Settings): A settings object containing configuration for
        the Unity Catalog MCP server.

    Returns:
        None
    """
    # Initializes logging directory.
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
    level = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warn": logging.WARN,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }.get(settings.uc_verbosity, logging.INFO)
    logging.basicConfig(handlers=(stream_handler, file_handler), level=level)
