"""Unity Catalog Model Context Protocol Server Implementation.

This module implements the Model Context Protocol (MCP) server, which enables AI agents to
execute Unity Catalog Functions on behalf of user agents.

Features:
- Implements an MCP server for Unity Catalog Functions execution.

License:
MIT License (c) 2025 Shingo OKAWA
"""

import logging
from typing import Optional, List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
)
from pydantic import BaseModel
from pydantic.networks import AnyHttpUrl
from unitycatalog.ai.core.client import UnitycatalogFunctionClient
from unitycatalog.ai.core.utils.function_processing_utils import (
    generate_function_input_params_schema,
    get_tool_name,
)
from unitycatalog.client import ApiClient, Configuration
from .tools import (
    Content,
    list_tools as list_ucai_tools,
    dispatch_tool as dispatch_ucai_tool,
)


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
    logger = logging.getLogger(__name__)
    client = UnitycatalogFunctionClient(
        api_client=ApiClient(configuration=Configuration(host=endpoint))
    )

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        functions = client.list_functions(catalog=catalog, schema=schema)
        logger.debug(f"list_tools: {functions}")
        return [
            Tool(
                name=func.name,
                description=func.comment or "",
                inputSchema=generate_function_input_params_schema(
                    func
                ).pydantic_model.schema(),
            )
            for func in functions.to_list()
        ] + list_ucai_tools()

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> List[Content]:
        tool = dispatch_ucai_tool(name)
        if tool is not None:
            contents = tool.func(client, arguments)
            logger.debug(f"call_tool: {contents}")
            return contents
        else:
            result = client.execute_function(
                function_name=f"{catalog}.{schema}.{name}",
                parameters=arguments,
            )
            logger.debug(f"call_tool: {result}")
            return [TextContent(type="text", text=result.to_json())]

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)
