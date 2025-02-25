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
import logging
from typing import Callable, Optional, Union, TypeAlias
from mcp.shared.context import RequestContext
from mcp.server.session import ServerSession
from mcp.types import (
    TextContent,
    ImageContent,
    EmbeddedResource,
    Tool,
)
from pydantic import BaseModel, Field
from unitycatalog.ai.core.client import UnitycatalogFunctionClient
from unitycatalog.ai.core.utils.function_processing_utils import (
    generate_function_input_params_schema,
)
from unitycatalog.client.models.function_info import FunctionInfo
from mcp_server_unitycatalog.cli import get_settings as Settings
from mcp_server_unitycatalog.logger import observe
from mcp_server_unitycatalog.utils import create_module, dump_json


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


class DeleteFunction(BaseModel):
    """Represents a request to delete a function in Unity Catalog.

    This model is used to define the parameters required for deleting
    a Python function within Unity Catalog.

    Attributes:
        name (str): The name of the function to be deleted.
    """

    name: str = Field(
        description="The name of the function to be deleted.",
    )


# Represents MCP tool response content.
Content: TypeAlias = Union[TextContent, ImageContent, EmbeddedResource]
# Represents MCP tool implementations.
UnityCatalogAiFunction: TypeAlias = Callable[
    [RequestContext[ServerSession], UnitycatalogFunctionClient, dict], list[Content]
]


@observe(by=LOGGER, args=[2])
def _list_functions(
    context: RequestContext[ServerSession],
    client: UnitycatalogFunctionClient,
    arguments: dict,
) -> list[Content]:
    """Lists functions within the configured Unity Catalog catalog and schema.

    This function retrieves a list of functions from the Unity Catalog
    using the preconfigured catalog and schema settings.

    Args:
        context (RequestContext[ServerSession]): The request context with session details.
        client (UnitycatalogFunctionClient): The client used to interact with Unity Catalog.
        arguments (dict): A dictionary of additional arguments (currently unused).

    Returns:
        list[Content]: A list of functions retrieved from Unity Catalog.
    """
    settings, model = Settings(), ListFunctions.model_validate(arguments)
    content = dump_json(
        client.list_functions(
            catalog=settings.uc_catalog, schema=settings.uc_schema
        ).to_list()
    )
    return [
        TextContent(
            type="text",
            text=content,
        )
    ]


@observe(by=LOGGER, args=[2])
def _get_function(
    context: RequestContext[ServerSession],
    client: UnitycatalogFunctionClient,
    arguments: dict,
) -> list[Content]:
    """Retrieves details of a specific Unity Catalog function.

    This function queries the Unity Catalog for a function specified by
    the provided arguments and returns its details as a JSON-formatted string.

    Args:
        context (RequestContext[ServerSession]): The request context with session details.
        client (UnitycatalogFunctionClient): The client used to interact with the Unity Catalog.
        arguments (dict): A dictionary containing the function name.

    Returns:
        list[Content]: A list containing a single TextContent object
        with the function details in JSON format.
    """
    settings, model = Settings(), GetFunction.model_validate(arguments)
    content = dump_json(
        client.get_function(
            function_name=f"{settings.uc_catalog}.{settings.uc_schema}.{model.name}",
        )
    )
    return [
        TextContent(
            type="text",
            text=content,
        )
    ]


@observe(by=LOGGER, args=[2])
def _create_function(
    context: RequestContext[ServerSession],
    client: UnitycatalogFunctionClient,
    arguments: dict,
) -> list[Content]:
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
        list[Content]: A list containing the JSON response of the created function.
    """
    settings, model = Settings(), CreateFunction.model_validate(arguments)
    # NOTE:
    # `inspect.getsourcelines` expects the argument to be a Python object defined in an actual
    # source file, meaning it does not work for objects that exist only in memory.
    # Hence, we provided a context manager responsible for handling temporary module creation.
    with create_module(model.script) as module:
        func = getattr(module, model.name)
        content = dump_json(
            client.create_python_function(
                catalog=settings.uc_catalog,
                schema=settings.uc_schema,
                func=func,
            )
        )
    asyncio.run(context.session.send_tool_list_changed())
    return [
        TextContent(
            type="text",
            text=content,
        )
    ]


@observe(by=LOGGER, args=[2])
def _delete_function(
    context: RequestContext[ServerSession],
    client: UnitycatalogFunctionClient,
    arguments: dict,
) -> list[Content]:
    """Deletes a function from Unity Catalog.

    This function removes a registered function from the Unity Catalog,
    and notifies the session that the available tools list has changed.

    Args:
        context (RequestContext[ServerSession]): The request context, which manages the session state.
        client (UnitycatalogFunctionClient): The client used to interact with Unity Catalog.
        arguments (dict): A dictionary containing the function name to be deleted.

    Returns:
        list[Content]: A list containing the deletion result as a text response.
    """
    settings, model = Settings(), DeleteFunction.model_validate(arguments)
    content = dump_json(
        client.delete_function(
            function_name=f"{settings.uc_catalog}.{settings.uc_schema}.{model.name}",
        )
    )
    asyncio.run(context.session.send_tool_list_changed())
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
    input_schema: dict = Field(
        description="The JSON schema representing the expected input format.",
    )
    func: UnityCatalogAiFunction = Field(
        description="The callable function implementing the tool's behavior.",
    )


# Enumeration of available Unity Catalog AI tools.
UNITY_CATALOG_AI_TOOLS: dict[str, UnityCatalogAiTool] = {
    "uc_list_functions": UnityCatalogAiTool(
        description="List Unity Catalog Functions within the specified parent catalog and schema. "
        "There is no guarantee of a specific ordering of the elements in the array.",
        input_schema=ListFunctions.model_json_schema(),
        func=_list_functions,
    ),
    "uc_get_function": UnityCatalogAiTool(
        description="Gets a Unity Catalog Function from within a parent catalog and schema.",
        input_schema=GetFunction.model_json_schema(),
        func=_get_function,
    ),
    "uc_create_function": UnityCatalogAiTool(
        description="Creates a Unity Catalog function. WARNING: This API is experimental and will "
        "change in future versions.",
        input_schema=CreateFunction.model_json_schema(),
        func=_create_function,
    ),
    "uc_delete_function": UnityCatalogAiTool(
        description="Delets a Unity Catalog function.",
        input_schema=DeleteFunction.model_json_schema(),
        func=_delete_function,
    ),
}


def list_tools() -> list[Tool]:
    """Returns a list of available Unity Catalog AI tools.

    This function generates a list of `Tool` instances based on the `UnityCatalogAiTools`
    enumeration, providing structured metadata for each tool.

    Returns:
        list[Tool]: A list of `Tool` objects, each containing:
    """
    return [
        Tool(
            name=name,
            description=tool.description,
            inputSchema=tool.input_schema,
        )
        for name, tool in UNITY_CATALOG_AI_TOOLS.items()
    ]


def list_udf_tools(client: UnitycatalogFunctionClient) -> list[Tool]:
    """Retrieves a list of user-defined functions (UDFs) registered in Unity Catalog.

    This function queries Unity Catalog for all available UDFs within the specified
    catalog and schema, then constructs a list of `Tool` objects representing these
    functions, excluding any predefined Unity Catalog AI tools.

    Args:
        client (UnitycatalogFunctionClient): The Unity Catalog function client used
        to query the available functions.

    Returns:
        list[Tool]: A list of `Tool` objects, each representing a UDF with its
        name, description, and input schema.
    """
    settings = Settings()
    return [
        Tool(
            name=func.name or "",
            description=func.comment or "",
            inputSchema=generate_function_input_params_schema(
                func
            ).pydantic_model.model_json_schema(),
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


@observe(by=LOGGER, args=[1, 2])
def execute_function(
    client: UnitycatalogFunctionClient,
    name: str,
    arguments: dict,
) -> list[Content]:
    """Executes a registered Unity Catalog function with the given parameters.

    This function invokes a function stored in Unity Catalog, passing in the
    specified arguments and returning the execution result.

    Args:
        client (UnitycatalogFunctionClient): The Unity Catalog function client.
        name (str): The name of the function to execute (not fully qualified).
        arguments (dict): A dictionary of parameters to pass to the function.

    Returns:
        list[Content]: The output of the function execution, wrapped in a
        list of `Content` objects.
    """
    settings = Settings()
    content = client.execute_function(
        function_name=f"{settings.uc_catalog}.{settings.uc_schema}.{name}",
        parameters=arguments,
    ).to_json()
    return [
        TextContent(
            type="text",
            text=content,
        )
    ]
