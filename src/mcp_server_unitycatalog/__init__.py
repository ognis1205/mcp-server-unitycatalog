"""Unity Catalog Model Context Protocol Server.

This module provides tools for integrating Unity Catalog AI, enabling AI agents to execute Unity Catalog
Functions on behalf of user agents.

License:
MIT License (c) 2025 Shingo OKAWA
"""

import logging
import sys
from traceback import format_exc
from mcp_server_unitycatalog.cli import get_settings as Cli
from mcp_server_unitycatalog.config import configure
from mcp_server_unitycatalog.server import start


def main() -> None:
    """Starts the MCP Unity Catalog Server.

    This function initializes the logging configuration based on the
    verbosity level, retrieves settings, and starts the Unity Catalog
    server using the specified endpoint, catalog, and schema.

    Returns:
        None
    """
    import asyncio

    cli = Cli()
    configure(cli)
    asyncio.run(
        start(
            endpoint=f"{cli.uc_server}/api/2.1/unity-catalog",
            catalog=cli.uc_catalog,
            schema=cli.uc_schema,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as _:
        print(format_exc(), file=sys.stderr)
