"""Unity Catalog Model Context Protocol Server.

This module provides tools for integrating Unity Catalog AI, enabling AI agents to execute Unity Catalog
Functions on behalf of user agents.

License:
MIT License (c) 2025 Shingo OKAWA
"""

import logging
import sys
from traceback import format_exc
from pydantic.networks import AnyHttpUrl
from .loggings import configure as configure_logging
from .settings import get_settings as Settings
from .server import start as start_server


def main() -> None:
    """Starts the MCP Unity Catalog Server.

    This function initializes the logging configuration based on the
    verbosity level, retrieves settings, and starts the Unity Catalog
    server using the specified endpoint, catalog, and schema.

    Returns:
        None
    """
    import asyncio

    settings = Settings()
    level = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warn": logging.WARN,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }.get(settings.uc_verbosity, logging.INFO)
    configure_logging(level)
    asyncio.run(
        start_server(
            endpoint=f"{settings.uc_server}/api/2.1/unity-catalog",
            catalog=settings.uc_catalog,
            schema=settings.uc_schema,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as _:
        print(format_exc(), file=sys.stderr)
