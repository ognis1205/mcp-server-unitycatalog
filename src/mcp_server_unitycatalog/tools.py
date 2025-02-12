"""Unity Catalog Model Context Protocol (MCP) Server Tools.

This module provides utility functions for interacting with the Unity Catalog AI MCP server.

Features:
- Lists Unity Catalog Functions.
- Retrieves information about a specific Unity Catalog Function.
- Creates Unity Catalog (Python) Functions.
- Executes Unity Catalog (Python) Functions.
- Deletes Unity Catalog Functions.

License:
MIT License (c) 2025 Shingo Okawa
"""

import json
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union, TypeAlias
from mcp.types import (
    TextContent,
    ImageContent,
    EmbeddedResource,
    Tool,
)
from pydantic import BaseModel, Field
from unitycatalog.ai.core.client import UnitycatalogFunctionClient
from unitycatalog.client import FunctionInfo
from .settings import get_settings as Settings


class ListFunctions(BaseModel):
    """Represents a request to list Unity Catalog Functions.

    This model defines parameters for listing functions within a Unity Catalog
    schema, allowing pagination and optional result limits.
    """

    pass


class GetFunction(BaseModel):
    """Represents a request to retrieve details of a Unity Catalog function.

    Attributes:
        name (str): The name of the function (not fully-qualified).
    """

    name: str = Field(
        description="The name of the function (not fully-qualified).",
    )


# Represents MCP tool response content.
Content: TypeAlias = Union[TextContent, ImageContent, EmbeddedResource]
# Represents MCP tool implementations.
UnityCatalogAiFunction: TypeAlias = Callable[
    [UnitycatalogFunctionClient, dict], List[Content]
]


def _list_functions(
    client: UnitycatalogFunctionClient, arguments: dict
) -> List[TextContent]:
    """Lists functions within the configured Unity Catalog catalog and schema.

    This function retrieves a list of functions from the Unity Catalog
    using the preconfigured catalog and schema settings.

    Args:
        client (UnitycatalogFunctionClient): The client used to interact with Unity Catalog.
        arguments (dict): A dictionary of additional arguments (currently unused).

    Returns:
        list: A list of functions retrieved from Unity Catalog.
    """
    settings = Settings()
    result = json.dumps(
        list(
            map(
                lambda f: f.to_json(),
                client.list_functions(
                    catalog=settings.uc_catalog, schema=settings.uc_schema
                ),
            )
        )
    )
    return [TextContent(type="text", text=result)]


def _get_function(
    client: UnitycatalogFunctionClient, arguments: dict
) -> List[TextContent]:
    """Lists functions within the configured Unity Catalog catalog and schema.

    This function retrieves a list of functions from the Unity Catalog
    using the preconfigured catalog and schema settings.

    Args:
        client (UnitycatalogFunctionClient): The client used to interact with Unity Catalog.
        arguments (dict): A dictionary of additional arguments (currently unused).

    Returns:
        list: A list of functions retrieved from Unity Catalog.
    """
    settings = Settings()
    result = json.dumps(
        client.get_function(
            name=f"{settings.uc_catalog}.{settings.uc_schema}.{arguments.name}",
        )
    )
    return [TextContent(type="text", text=result)]


class UnityCatalogAiTool(BaseModel):
    """Represents a Unity Catalog AI tool.

    This dictionary structure defines the metadata and execution function for a Unity Catalog AI tool.

    Attributes:
        name (str): The name of the tool.
        description (str): A brief description of the tool's purpose.
        input_schema (str): The JSON schema representing the expected input format.
        func (UnityCatalogAiFunction): The callable function implementing the tool's behavior.
    """

    description: str
    input_schema: Dict
    func: UnityCatalogAiFunction


# Enumeration of available Unity Catalog AI tools.
UNITY_CATALOG_AI_TOOLS: Dict[str, UnityCatalogAiTool] = {
    "uc_list_functions": UnityCatalogAiTool(
        description="List functions within the specified parent catalog and schema. "
        "There is no guarantee of a specific ordering of the elements in the array.",
        input_schema=ListFunctions.schema(),
        func=_list_functions,
    )
}


def list_tools() -> List[Tool]:
    """Returns a list of available Unity Catalog AI tools.

    This function generates a list of `Tool` instances based on the `UnityCatalogAiTools`
    enumeration, providing structured metadata for each tool.

    Returns:
        List[Tool]: A list of `Tool` objects, each containing:
    """
    return [
        Tool(
            name=name,
            description=tool.description,
            inputSchema=tool.input_schema,
        )
        for name, tool in UNITY_CATALOG_AI_TOOLS.items()
    ]


def dispatch_tool(name: str) -> Optional[UnityCatalogAiTool]:
    """Retrieves the Unity Catalog AI tool function by name.

    This function looks up and returns the corresponding function
    for a given tool name from the `UNITY_CATALOG_AI_TOOLS` registry.

    Args:
        name (str): The name of the Unity Catalog AI tool.

    Returns:
        Optional[UnityCatalogAiFunction]: The function corresponding to
        the specified tool name if found, otherwise `None`.
    """
    return UNITY_CATALOG_AI_TOOLS.get(name)
