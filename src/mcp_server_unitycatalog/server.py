"""Unity Catalog Model Context Protocol Server Implementation.

This module implements the Model Context Protocol (MCP) server, which enables AI agents to
execute Unity Catalog Functions on behalf of user agents.

Features:
- Implements an MCP server for Unity Catalog Functions execution.

License:
MIT License (c) 2025 Shingo OKAWA
"""

import logging
from typing import Optional
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool
from pydantic.networks import AnyHttpUrl
from unitycatalog.ai.core.client import UnitycatalogFunctionClient
from unitycatalog.client.api_client import ApiClient
from unitycatalog.client.configuration import Configuration
from mcp_server_unitycatalog.tools import (
    Content,
    list_tools as list_ucai_tools,
    list_udf_tools,
    dispatch_tool as dispatch_ucai_tool,
    execute_function,
)


# The logger instance for this module.
LOGGER = logging.getLogger(__name__)


async def start(endpoint: str, catalog: str, schema: str) -> None:
    """Starts the MCP Unity Catalog server and initializes the API client.

    This function sets up the server and logs the connection details.

    Args:
        endpoint (str): The base URL of the Unity Catalog API server.
        catalog (str): The name of the Unity Catalog catalog.
        schema (str): The name of the schema within the catalog.

    Returns:
        None
    """
    server = Server("mcp-unitycatalog")
    client = UnitycatalogFunctionClient(
        api_client=ApiClient(configuration=Configuration(host=endpoint))
    )

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return list_udf_tools(client) + list_ucai_tools()

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[Content]:
        tool = dispatch_ucai_tool(name)
        if tool is not None:
            return tool.func(server.request_context, client, arguments)
        else:
            return execute_function(client, name, arguments)

    options = server.create_initialization_options(
        notification_options=NotificationOptions(
            resources_changed=True, tools_changed=True
        )
    )
    LOGGER.info(f"start serving: options: {options}")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)
