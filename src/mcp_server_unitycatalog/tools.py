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

import asyncio
import json
import logging
from typing import Any, Callable, Dict, List, Optional, Union, TypeAlias
from mcp.shared.context import RequestContext
from mcp.server.session import ServerSession
from mcp.types import (
    TextContent,
    ImageContent,
    EmbeddedResource,
    Tool,
)
from pydantic import BaseModel, Field
from pydantic.json import pydantic_encoder
from unitycatalog.ai.core.client import UnitycatalogFunctionClient
from unitycatalog.ai.core.utils.function_processing_utils import (
    generate_function_input_params_schema,
)
from unitycatalog.client import FunctionInfo
from .context import tempmodule
from .settings import get_settings as Settings


# The logger instance for this module.
LOGGER = logging.getLogger(__name__)


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


class CreateFunction(BaseModel):
    """Represents a request to create a new function in Unity Catalog.

    This model is used to define the parameters required for registering
    a Python function within Unity Catalog.

    Attributes:
        name (str): The name of the function to be registered.
        script (str): The Python script containing the function definition.
    """

    name: str = Field(
        description="The name of the function to be registered in the given script.",
    )
    script: str = Field(
        description="The Python script including the function to be registered.",
    )


# Represents MCP tool response content.
Content: TypeAlias = Union[TextContent, ImageContent, EmbeddedResource]
# Represents MCP tool implementations.
UnityCatalogAiFunction: TypeAlias = Callable[
    [RequestContext[ServerSession], UnitycatalogFunctionClient, dict], List[Content]
]


def _model_dump_json(maybe_model: Union[BaseModel, List[BaseModel], Dict]) -> str:
    """Serializes a Pydantic model or a list of Pydantic models into a JSON string.

    This function ensures proper serialization using Pydantic's encoding utilities,
    handling both single model instances and lists of models.

    Args:
        model_or_list (Union[BaseModel, List[BaseModel]]): A Pydantic model instance
            or a list of Pydantic models to be serialized.

    Returns:
        str: A JSON-formatted string representation of the input model or list.
    """
    if isinstance(maybe_model, list) or isinstance(maybe_model, dict):
        return json.dumps(maybe_model, default=pydantic_encoder, separators=(",", ":"))
    else:
        return maybe_model.model_dump_json(by_alias=True, exclude_unset=True)


def _list_functions(
    context: RequestContext[ServerSession],
    client: UnitycatalogFunctionClient,
    arguments: dict,
) -> List[TextContent]:
    """Lists functions within the configured Unity Catalog catalog and schema.

    This function retrieves a list of functions from the Unity Catalog
    using the preconfigured catalog and schema settings.

    Args:
        context (RequestContext[ServerSession]): The request context with session details.
        client (UnitycatalogFunctionClient): The client used to interact with Unity Catalog.
        arguments (dict): A dictionary of additional arguments (currently unused).

    Returns:
        List[TextContent]: A list of functions retrieved from Unity Catalog.
    """
    settings, arguments = Settings(), ListFunctions(**arguments)
    LOGGER.info(f"uc_list_functions: arguments: {_model_dump_json(arguments)}")
    content = _model_dump_json(
        client.list_functions(catalog=settings.uc_catalog, schema=settings.uc_schema)
    )
    LOGGER.info(f"uc_list_functions: content: {content}")
    return [
        TextContent(
            type="text",
            text=content,
        )
    ]


def _get_function(
    context: RequestContext[ServerSession],
    client: UnitycatalogFunctionClient,
    arguments: dict,
) -> List[TextContent]:
    """Retrieves details of a specific Unity Catalog function.

    This function queries the Unity Catalog for a function specified by
    the provided arguments and returns its details as a JSON-formatted string.

    Args:
        context (RequestContext[ServerSession]): The request context with session details.
        client (UnitycatalogFunctionClient): The client used to interact with the Unity Catalog.
        arguments (dict): A dictionary containing the function name.

    Returns:
        List[TextContent]: A list containing a single TextContent object
        with the function details in JSON format.
    """
    settings, arguments = Settings(), GetFunction(**arguments)
    LOGGER.info(f"uc_get_function: arguments: {_model_dump_json(arguments)}")
    content = _model_dump_json(
        client.get_function(
            function_name=f"{settings.uc_catalog}.{settings.uc_schema}.{arguments.name}",
        )
    )
    LOGGER.info(f"uc_get_function: content: {content}")
    return [
        TextContent(
            type="text",
            text=content,
        )
    ]


def _create_function(
    context: RequestContext[ServerSession],
    client: UnitycatalogFunctionClient,
    arguments: dict,
) -> List[TextContent]:
    """Creates a new Python function in Unity Catalog based on the provided script.

    This function extracts a specified function from the given script,
    registers it in Unity Catalog, and notifies the session of changes.

    Args:
        context (RequestContext[ServerSession]): The request context with session details.
        client (UnitycatalogFunctionClient): The client for interacting with Unity Catalog.
        arguments (dict): A dictionary containing:
            - "name" (str): The function name to register.
            - "script" (str): The Python script containing the function definition.

    Returns:
        List[TextContent]: A list containing the JSON response of the created function.
    """
    settings, arguments = Settings(), CreateFunction(**arguments)
    LOGGER.info(f"uc_create_function: arguments: {_model_dump_json(arguments)}")
    with tempmodule(arguments.script) as module:
        func = getattr(module, arguments.name)
        content = _model_dump_json(
            client.create_python_function(
                catalog=settings.uc_catalog,
                schema=settings.uc_schema,
                func=func,
            )
        )
    asyncio.run(context.session.send_tool_list_changed())
    LOGGER.info(f"uc_create_function: content: {content}")
    return [
        TextContent(
            type="text",
            text=content,
        )
    ]


class UnityCatalogAiTool(BaseModel):
    """Represents a Unity Catalog AI tool.

    This dictionary structure defines the metadata and execution function for a Unity Catalog AI tool.

    Attributes:
        description (str): A brief description of the tool's purpose.
        input_schema (str): The JSON schema representing the expected input format.
        func (UnityCatalogAiFunction): The callable function implementing the tool's behavior.
    """

    description: str = Field(
        description="A brief description of the tool's purpose.",
    )
    input_schema: Dict = Field(
        description="The JSON schema representing the expected input format.",
    )
    func: UnityCatalogAiFunction = Field(
        description="The callable function implementing the tool's behavior.",
    )


# Enumeration of available Unity Catalog AI tools.
UNITY_CATALOG_AI_TOOLS: Dict[str, UnityCatalogAiTool] = {
    "uc_list_functions": UnityCatalogAiTool(
        description="List Unity Catalog Functions within the specified parent catalog and schema. "
        "There is no guarantee of a specific ordering of the elements in the array.",
        input_schema=ListFunctions.schema(),
        func=_list_functions,
    ),
    "uc_get_function": UnityCatalogAiTool(
        description="Gets a Unity Catalog Function from within a parent catalog and schema.",
        input_schema=GetFunction.schema(),
        func=_get_function,
    ),
    "uc_create_function": UnityCatalogAiTool(
        description="Creates a Unity Catalog function. WARNING: This API is experimental and will "
        "change in future versions.",
        input_schema=CreateFunction.schema(),
        func=_create_function,
    ),
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


def list_udf_tools(client: UnitycatalogFunctionClient) -> List[Tool]:
    """Retrieves a list of user-defined functions (UDFs) registered in Unity Catalog.

    This function queries Unity Catalog for all available UDFs within the specified
    catalog and schema, then constructs a list of `Tool` objects representing these
    functions, excluding any predefined Unity Catalog AI tools.

    Args:
        client (UnitycatalogFunctionClient): The Unity Catalog function client used
        to query the available functions.

    Returns:
        List[Tool]: A list of `Tool` objects, each representing a UDF with its
        name, description, and input schema.
    """
    settings = Settings()
    return [
        Tool(
            name=func.name,
            description=func.comment or "",
            inputSchema=generate_function_input_params_schema(
                func
            ).pydantic_model.schema(),
        )
        for func in client.list_functions(
            catalog=settings.uc_catalog, schema=settings.uc_schema
        ).to_list()
        if func.name not in UNITY_CATALOG_AI_TOOLS
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


def execute_function(
    client: UnitycatalogFunctionClient,
    name: str,
    arguments: dict,
) -> List[TextContent]:
    """Executes a registered Unity Catalog function with the given parameters.

    This function invokes a function stored in Unity Catalog, passing in the
    specified arguments and returning the execution result.

    Args:
        client (UnitycatalogFunctionClient): The Unity Catalog function client.
        name (str): The name of the function to execute (not fully qualified).
        arguments (dict): A dictionary of parameters to pass to the function.

    Returns:
        List[TextContent]: The output of the function execution, wrapped in a
        list of `TextContent` objects.
    """
    settings = Settings()
    LOGGER.info(f"{name}: arguments: {_model_dump_json(arguments)}")
    content = client.execute_function(
        function_name=f"{settings.uc_catalog}.{settings.uc_schema}.{name}",
        parameters=arguments,
    ).to_json()
    LOGGER.info(f"{name}: content: {content}")
    return [
        TextContent(
            type="text",
            text=content,
        )
    ]
