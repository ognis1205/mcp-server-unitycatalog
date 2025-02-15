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
import random
import sys
import pytest
from pydantic import ValidationError
from unittest.mock import patch
from mcp_server_unitycatalog.cli import get_settings


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
    """Tests that missing required command-line arguments raise a ValidationError.

    This test ensures that if any of the required arguments (`--uc_server`,
    `--uc_catalog`, or `--uc_schema`) are missing from the command line input,
    the configuration validation fails as expected.

    Args:
        server (str): The Unity Catalog server URL.
        catalog (str): The catalog name within Unity Catalog.
        schema (str): The schema name within the catalog.

    Asserts:
        - A `ValidationError` is raised when one of the required arguments is missing.
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


def test_required_arguments(server: str, catalog: str, schema: str) -> None:
    """"""
    argv = random.choice(
        [
            ["mcp-server-unitycatalog", "--uc_catalog", catalog, "--uc_schema", schema],
            ["mcp-server-unitycatalog", "--uc_server", server, "--uc_schema", schema],
            ["mcp-server-unitycatalog", "--uc_server", server, "--uc_catalog", catalog],
        ]
    )
    with patch.object(sys, "argv", argv):
        with pytest.raises(ValidationError) as exc_info:
            settings = get_settings()
        assert "Field required" in str(exc_info.value)
