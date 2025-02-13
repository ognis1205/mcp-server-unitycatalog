"""Context management utilities.

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
from importlib import util as import_util
from pathlib import Path
from tempfile import NamedTemporaryFile
from types import ModuleType


@contextmanager
def tempmodule(script: str) -> ModuleType:
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
        spec = import_util.spec_from_file_location(Path(temp.name).stem, tmp.name)
        module = import_util.module_from_spec(spec)
        spec.loader.exec_module(module)
        yield module
