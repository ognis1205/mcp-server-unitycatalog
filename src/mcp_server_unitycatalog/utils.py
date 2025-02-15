"""Unity Catalog Model Context Protocol (MCP) Server Utilities.

This module provides utilities for handling execution contexts,
including temporary module creation and dynamic script execution.
These utilities enable runtime code evaluation in isolated environments,
which is particularly useful for function registration and execution.

Features:
- Dynamically creates temporary Python modules from scripts.
- Supports isolated execution of dynamically generated code.

License:
MIT License (c) 2025 Shingo Okawa
"""

import uuid
from contextlib import contextmanager
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Callable, Iterator, Optional, TypeVar
from types import ModuleType


# R represents the return type of the function passed to _fmap.
R = TypeVar("R")


def _fmap(func: Callable[..., Optional[R]], *maybe_nones: Optional[Any]) -> Optional[R]:
    """Applies a function to multiple Optional values, flattening the result.

    If any input is None, returns None. Otherwise, applies `func` to the
    unwrapped values and returns its result.

    Args:
        func: A function that takes multiple arguments of potentially different types
              and returns an Optional[R].
        *maybe_nones: A variable number of Optional values of different types.

    Returns:
        An Optional[R] resulting from applying `func` to the unwrapped values,
        or None if any input is None.
    """
    if any(maybe is None for maybe in maybe_nones):
        return None
    return func(*maybe_nones)  # Unwrap and apply


@contextmanager
def create_module(script: str) -> Iterator[Optional[ModuleType]]:
    """Creates a temporary Python module from a given script string.

    This context manager writes the provided script to a temporary file,
    loads it as a module, and yields it for use.

    Args:
        script (str): The Python script to be dynamically loaded.

    Yields:
        ModuleType: The loaded temporary module.
    """
    with NamedTemporaryFile(suffix=".py") as tmp:
        tmp.write(script.encode())
        tmp.flush()
        spec = spec_from_file_location(Path(tmp.name).stem, tmp.name)
        module = _fmap(module_from_spec, spec)
        loader = _fmap(lambda spec: spec.loader, spec)
        _ = _fmap(lambda loader, module: loader.exec_module(module), loader, module)
        yield module
