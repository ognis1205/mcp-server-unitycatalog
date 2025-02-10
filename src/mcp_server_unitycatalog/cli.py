"""Unity Catalog Model Context Protocol (MCP) Server Configuration/CLI.

This module defines the server configuration/cli class for the Model Context Protocol (MCP) in Unity Catalog.

Features:
- Defines default values for the MCP server configuration.
- Supports automatic loading of environment variables.

License:
MIT License (c) 2025 Shingo Okawa
"""

from typing import Literal, Optional
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Cli(BaseSettings):
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
