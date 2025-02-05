"""Unity Catalog Model Context Protocol Server.

A Model Context Protocol (MCP) server enabling AI agents to execute Unity Catalog Functions seamlessly.

This module provides tools for integrating Unity Catalog AI, enabling AI agents to execute Unity Catalog
Functions on behalf of user agents.

License:
MIT License (c) 2025 Shingo OKAWA
"""

import click
import logging
import sys
from traceback import format_exc
from pydantic.networks import AnyHttpUrl
from .server import start


@click.command()
@click.option(
    "--url", "-u", required=True, type=AnyHttpUrl, help="Unity Catalog server url"
)
@click.option("--catalog", "-c", required=True, type=click.STRING, help="Catalog name")
@click.option("--schema", "-s", required=True, type=click.STRING, help="Schema name")
@click.option("--verbose", "-v", count=True)
def main(url: AnyHttpUrl, catalog: str, schema: str, verbose: int) -> None:
    """MCP Unity Catalog Server - Unity Catalog Functions I/F for MCP."""
    import asyncio

    level = logging.WARN
    if verbose == 1:
        level = logging.INFO
    elif verbose >= 2:
        level = logging.DEBUG
    logging.basicConfig(level=level, stream=sys.stderr)
    asyncio.run(start(url, catalog, schema))


if __name__ == "__main__":
    try:
        main()
    except Exception as _:
        print(format_exc(), file=sys.stderr)
