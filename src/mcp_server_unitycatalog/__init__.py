"""Unity Catalog Model Context Protocol Server.

A Model Context Protocol (MCP) server enabling AI agents to execute Unity Catalog Functions seamlessly.

This module provides tools for integrating Unity Catalog AI, enabling AI agents to execute Unity Catalog
Functions on behalf of user agents.

License:
MIT License (c) 2025 Shingo OKAWA
"""

import logging
import sys
from traceback import format_exc
from pydantic.networks import AnyHttpUrl
from .settings import get_settings
from .server import start


def main() -> None:
    """MCP Unity Catalog Server - Unity Catalog Functions I/F for MCP."""
    import asyncio

    settings = get_settings()
    level = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warn": logging.WARN,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }[settings.uc_verbosity]
    logging.basicConfig(level=level, stream=sys.stderr)
    asyncio.run(
        start(
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
