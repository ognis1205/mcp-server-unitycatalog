"""Unity Catalog Model Context Protocol (MCP) Server Utility Functions.

This module provides helper functions.

Features:
- Safely applying functions to multiple Optional values (`_fmap`).
- Serializing Pydantic models, lists, and dictionaries to JSON (`dump_json`).
- Dynamically creating and loading temporary Python modules (`create_module`).

License:
MIT License (c) 2025 Shingo Okawa
"""

import json
from contextlib import contextmanager
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Callable, Iterator, Optional, TypeVar, Union
from types import ModuleType
from pydantic import BaseModel
from pydantic.json import pydantic_encoder


# _ReturnType represents the return type of the function passed to `_fmap`.
_ReturnType = TypeVar("_ReturnType")


def _fmap(
    func: Callable[..., Optional[_ReturnType]], *maybe_nones: Optional[Any]
) -> Optional[_ReturnType]:
    """Applies a function to multiple Optional values, flattening the result.

    If any input is None, returns None. Otherwise, applies `func` to the
    unwrapped values and returns its result.

    Args:
        func: A function that takes multiple arguments of potentially different types
              and returns an Optional[R].
        *maybe_nones: A variable number of Optional values of different types.

    Returns:
        An Optional[_ReturnType] resulting from applying `func` to the unwrapped values,
        or None if any input is None.
    """
    if any(maybe is None for maybe in maybe_nones):
        return None
    return func(*maybe_nones)


def dump_json(maybe_model: Union[BaseModel, list, dict, None]) -> str:
    """Serializes a Pydantic model, list, or dictionary to a JSON string.

    This function ensures proper serialization using Pydantic's encoding utilities,
    handling both single model instances and lists/dicts of models.

    Args:
        maybe_model (Union[BaseModel, list, dict, None]): The object to serialize.

    Returns:
        str: A JSON string representation of the input, or an empty string if None
        is provided.
    """
    if maybe_model is None:
        return ""
    elif isinstance(maybe_model, list) or isinstance(maybe_model, dict):
        return json.dumps(maybe_model, default=pydantic_encoder, separators=(",", ":"))
    else:
        return maybe_model.model_dump_json(by_alias=True, exclude_unset=True)


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
