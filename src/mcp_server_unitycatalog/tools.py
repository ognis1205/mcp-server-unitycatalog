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

from enum import Enum
from typing import List, Optional
from mcp.types import Tool
from pydantic import BaseModel, Field


class ListFunctions(BaseModel):
    """Represents a request to list Unity Catalog Functions.

    This model defines parameters for listing functions within a Unity Catalog
    schema, allowing pagination and optional result limits.

    Attributes:
        max_results (Optional[int]): Maximum number of functions to return.
            If not set, all available functions may be returned.
        page_token (Optional[str]): Opaque pagination token used to retrieve
            the next page of results based on a previous query.
        timeout (Optional[float]): Maximum time (in seconds) to wait for the
            request to complete.
    """

    max_results: Optional[int] = Field(
        default=None,
        description="Maximum number of functions to return.",
    )
    page_token: Optional[str] = Field(
        default=None,
        description="Opaque pagination token to go to next "
        "page based on previous query.",
    )
    timeout: Optional[float] = Field(
        default=None,
        description="maximum time (in seconds) to wait for the request to complete.",
    )


class UnityCatalogAiTools(Enum):
    """Enumeration of available Unity Catalog AI tools.

    This Enum defines various tools for interacting with Unity Catalog,
    including listing functions and other potential operations.

    Attributes:
        LIST_FUNCTIONS (tuple): A tool for listing functions within a specified catalog and schema.
            - Name: "list_functions"
            - Description: Lists functions under the given catalog and schema with no guaranteed order.
            - Model: ListFunctions (Defines the expected request parameters.)
    """

    LIST_FUNCTIONS = (
        "list_functions",
        "List functions within the specified parent catalog and schema. "
        "There is no guarantee of a specific ordering of the elements in the array.",
        ListFunctions,
    )


def list_unity_catalog_ai_tools() -> List[Tool]:
    """Returns a list of available Unity Catalog AI tools.

    This function generates a list of `Tool` instances based on the `UnityCatalogAiTools`
    enumeration, providing structured metadata for each tool.

    Returns:
        List[Tool]: A list of `Tool` objects, each containing:
    """
    return [
        Tool(
            name=name,
            description=description,
            inputSchema=model.schema(),
        )
        for name, description, model in list(
            map(lambda x: x.value, UnityCatalogAiTools)
        )
    ]
