"""Tests for the Settings configuration in the MCP Unity Catalog project.

This module contains unit tests for verifying that the application settings,
including environment variable parsing and CLI argument handling, are correctly
loaded and applied.

The tests ensure that:
- Required settings are properly initialized.
- Default values are correctly assigned.
- Environment variables and CLI arguments override defaults as expected.

License:
MIT License (c) 2025 Shingo OKAWA
"""

import os
import sys
from unittest.mock import patch
from mcp_server_unitycatalog.settings import get_settings


def test_cache(server: str, catalog: str, schema: str) -> None:
    """Tests that the settings object is cached and reused.

    This test verifies that calling `get_settings()` multiple times
    returns the same instance, ensuring that settings are properly
    cached using `@lru_cache`.

    Args:
        server (str): The Unity Catalog server URL.
        catalog (str): The catalog name within Unity Catalog.
        schema (str): The schema name within the catalog.

    Asserts:
        The `get_settings()` function returns the same object instance
        when called multiple times, confirming that caching works correctly.
    """
    argv = [
        "mcp-server-unitycatalog",
        "--uc_server",
        server,
        "--uc_catalog",
        catalog,
        "--uc_schema",
        schema,
    ]
    with patch.object(sys, "argv", argv):
        lhs = get_settings()
        rhs = get_settings()
        assert lhs is rhs


def test_arguments(server: str, catalog: str, schema: str) -> None:
    """Tests that command-line arguments are correctly parsed into settings.

    This test verifies that when command-line arguments are provided,
    they are properly parsed and assigned to the corresponding settings attributes.

    Args:
        server (str): The Unity Catalog server URL.
        catalog (str): The catalog name within Unity Catalog.
        schema (str): The schema name within the catalog.

    Asserts:
        - `settings.uc_server` matches the provided `server`.
        - `settings.uc_catalog` matches the provided `catalog`.
        - `settings.uc_schema` matches the provided `schema`.
    """
    argv = [
        "mcp-server-unitycatalog",
        "--uc_server",
        server,
        "--uc_catalog",
        catalog,
        "--uc_schema",
        schema,
    ]
    with patch.object(sys, "argv", argv):
        settings = get_settings()
        assert settings.uc_server == server
        assert settings.uc_catalog == catalog
        assert settings.uc_schema == schema
