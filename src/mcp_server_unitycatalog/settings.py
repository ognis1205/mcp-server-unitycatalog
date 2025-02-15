"""Unity Catalog Model Context Protocol (MCP) Server Configuration/CLI.

This module defines the server configuration/cli class for the Model Context Protocol (MCP) in Unity Catalog.

Features:
- Defines default values for the MCP server configuration.
- Supports automatic loading of environment variables.

License:
MIT License (c) 2025 Shingo Okawa
"""

from functools import lru_cache
from typing import Literal, Optional
from pathlib import Path
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for interacting with the Unity Catalog server.

    This class loads configuration values from environment variables and
    command-line arguments, enabling seamless integration with Unity Catalog.

    Attributes:
        uc_server (str): The base URL of the Unity Catalog server.
        uc_catalog (str): The name of the Unity Catalog catalog.
        uc_schema (str): The name of the schema within the catalog.
        uc_token (Optional[str]): The access token for authentication.
        uc_verbosity (Literal): The logging verbosity level (default: "warn").
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        cli_parse_args=True,
    )
    uc_server: str = Field(
        description="The base URL of the Unity Catalog server, "
        "used to interact with the Unity Catalog API.",
        validation_alias=AliasChoices("u", "uc_server"),
    )
    uc_catalog: str = Field(
        description="The name of the Unity Catalog catalog, "
        "which serves as the top-level container for schemas "
        "and assets within Unity Catalog.",
        validation_alias=AliasChoices("c", "uc_catalog"),
    )
    uc_schema: str = Field(
        description="The name of the schema within a Unity Catalog "
        "catalog. Schemas organize assets, providing a structured "
        "namespace for data objects.",
        validation_alias=AliasChoices("s", "uc_schema"),
    )
    uc_token: Optional[str] = Field(
        default=None,
        description="The access token used to authorize API requests "
        "to the Unity Catalog server.",
        validation_alias=AliasChoices("t", "uc_token"),
    )
    uc_verbosity: Literal["debug", "info", "warn", "error", "critical"] = Field(
        default="warn",
        description="The verbosity level for logging or debugging "
        "MCP Unity Catalog server.",
        validation_alias=AliasChoices("v", "uc_verbosity"),
    )
    uc_log_directory: Path = Field(
        default=Path(".mcp_server_unitycatalog"),
        description="The directory where log files for the MCP Unity "
        "Catalog server will be stored.",
        validation_alias=AliasChoices("l", "uc_log_directory"),
    )


@lru_cache
def get_settings():
    """Returns a cached instance of the Settings class.

    This function ensures that the configuration settings are loaded only once
    and reused across multiple calls, improving performance by avoiding redundant
    parsing of environment variables or CLI arguments.

    Returns:
        Settings: A singleton instance of the Settings class.
    """
    return Settings()  # pyright: ignore[reportCallIssue]
