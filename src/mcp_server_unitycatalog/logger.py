"""Unity Catalog Model Context Protocol (MCP) Server Logger Utility Functions.

This module provides a decorator for logging function calls, enabling
automatic logging before execution, after execution, and upon exceptions.

Features:
- Logs function arguments, return values, and exceptions.
- Enhances debugging and observability.

License:
MIT License (c) 2025 Shingo OKAWA
"""

import functools
import time
import uuid
from enum import Enum
from logging import Logger
from pydantic import BaseModel, Field
from typing import Any, Callable, Optional, ParamSpec, TypeVar
from mcp_server_unitycatalog.utils import dump_json


class When(str, Enum):
    """Specifies when logging was performed in the `log` decorator.

    Attributes:
        BEFORE: Log before the function is called.
        AFTER: Log after the function has returned successfully.
        EXCEPTION: Log when an exception is raised during execution.
    """

    BEFORE = "before"
    AFTER = "after"
    EXCEPTION = "exception"


class Log(BaseModel):
    """Represents a structured log entry for function calls.

    This model captures details about function execution, including
    its arguments, results, and any exceptions that may occur.
    """

    id: str = Field(
        description="Unique identifier for the log entry.",
    )
    when: When = Field(
        description="Indicates when the log was generated (e.g., before, after, or on exception).",
    )
    name: str = Field(
        description="Name of the logged function.",
    )
    args: Optional[tuple] = Field(
        default=None,
        description="Positional arguments passed to the function.",
    )
    kwargs: Optional[dict] = Field(
        default=None,
        description="Keyword arguments passed to the function.",
    )
    result: Optional[Any] = Field(
        default=None,
        description="Return value of the function (if applicable).",
    )
    exception: Optional[str] = Field(
        default=None,
        description="Exception raised during function execution (if any).",
    )
    logged_at: int = Field(
        description="Timestamp (epoch time in seconds) when the log was created.",
    )


# `_Params` represents the parameter types of the function passed to `log`.
_Params = ParamSpec("_Params")
# `_ReturnType` represents the return type of the function passed to `log`.
_ReturnType = TypeVar("_ReturnType")


def observe(
    by: Logger,
    args: Optional[list[int]] = None,
    kwargs: Optional[list[str]] = None,
):
    """A decorator for logging function execution details.

    This decorator logs function calls before execution, after execution,
    and upon exceptions using a structured log format.

    Args:
        by (Logger): The logger instance to be used for logging.
        args (Optional[list[int]]): Indices of positional arguments to log.
            If None, all positional arguments are logged.
        kwargs (Optional[list[str]]): Keys of keyword arguments to log.
            If None, all keyword arguments are logged.

    Returns:
        Callable: A decorated function with logging behavior.

    Logs:
        - BEFORE: Logs the function name, arguments, and timestamp before execution.
        - AFTER: Logs the function name, return value, and timestamp after execution.
        - EXCEPTION: Logs the function name, exception details, and timestamp if an exception occurs.
    """

    def decorator(
        func: Callable[_Params, _ReturnType],
    ) -> Callable[_Params, _ReturnType]:
        @functools.wraps(func)
        def wrapper(*_args: _Params.args, **_kwargs: _Params.kwargs):
            id = str(uuid.uuid4())
            logger = by.getChild(func.__name__)
            before = Log(
                id=id,
                when=When.BEFORE,
                name=func.__name__,
                args=_args if args is None else tuple(_args[i] for i in args),
                kwargs=_kwargs if kwargs is None else {k: _kwargs[k] for k in kwargs},
                logged_at=time.time_ns(),
            )
            logger.info(dump_json(before))
            try:
                result = func(*_args, **_kwargs)
                after = Log(
                    id=id,
                    when=When.AFTER,
                    name=func.__name__,
                    result=result,
                    logged_at=time.time_ns(),
                )
                logger.info(dump_json(after))
            except Exception as e:
                exception = Log(
                    id=id,
                    when=When.EXCEPTION,
                    name=func.__name__,
                    exception=str(e),
                    logged_at=time.time_ns(),
                )
                logger.info(dump_json(exception))
                raise e
            return result

        return wrapper

    return decorator
