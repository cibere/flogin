from __future__ import annotations
from typing import Any
from .responses import ErrorResponse

__all__ = (
    "JsonRPCException",
    "ParserError",
    "InvalidRequest",
    "MethodNotFound",
    "InvalidParams",
    "InternalError",
    "FlowError",
)


class JsonRPCException(Exception):
    r"""This is a generic class representing a JsonRPCException

    Attributes
    ----------
    code: :class:`int`
        The JsonRPC Error Code
    message: :class:`str`
        The message sent with the error
    data: Optional[Any]
        Any data sent with the error
    """

    code: int

    def __init__(self, message: str, data: Any | None = None) -> None:
        self.message = message
        self.data = data

    def to_response(self) -> ErrorResponse:
        return ErrorResponse(self.code, self.message, self.data)


class ParserError(JsonRPCException):
    r"""This is a specialized JsonRPCException specifically for the error code -32700, which should mean that flogin sent invalid data and flow was unable to parse it.

    Attributes
    ----------
    code: :class:`int` = -32700
        The JsonRPC Error Code
    message: :class:`str`
        The message sent with the error
    data: Optional[Any]
        Any data sent with the error
    """

    code = -32700


class InvalidRequest(JsonRPCException):
    r"""This is a specialized JsonRPCException specifically for the error code -32600, which should mean that flogin sent an invalid request object.

    Attributes
    ----------
    code: :class:`int` = -32600
        The JsonRPC Error Code
    message: :class:`str`
        The message sent with the error
    data: Optional[Any]
        Any data sent with the error
    """

    code = -32600


class MethodNotFound(JsonRPCException):
    r"""This is a specialized JsonRPCException specifically for the error code -32601, which should mean that flogin is attempting to use a method that doesn't exist.

    Attributes
    ----------
    code: :class:`int` = -32601
        The JsonRPC Error Code
    message: :class:`str`
        The message sent with the error
    data: Optional[Any]
        Any data sent with the error
    """

    code = -32601


class InvalidParams(JsonRPCException):
    r"""This is a specialized JsonRPCException specifically for the error code -32602, which should mean that flogin is attempting to use a method, but is sending the wrong parameters.

    Attributes
    ----------
    code: :class:`int` = -32602
        The JsonRPC Error Code
    message: :class:`str`
        The message sent with the error
    data: Optional[Any]
        Any data sent with the error
    """

    code = -32602


class InternalError(JsonRPCException):
    r"""This is a specialized JsonRPCException specifically for the error code -32603, which should mean that flogin has received an error.

    Attributes
    ----------
    code: :class:`int` = -32603
        The JsonRPC Error Code
    message: :class:`str`
        The message sent with the error
    data: Optional[Any]
        Any data sent with the error
    """

    code = -32603


class FlowError(JsonRPCException):
    r"""This is a specialized JsonRPCException specifically for error codes between -32000 and -32099, which means that flow has ran into an error.

    Attributes
    ----------
    code: :class:`int` = -32603
        The JsonRPC Error Code
    message: :class:`str`
        The message sent with the error
    data: Optional[Any]
        Any data sent with the error
    """

    ...


def get_exception_from_json(data: dict[str, Any]) -> JsonRPCException:
    code = data["code"]
    kwargs = {"message": data["message"], "data": data.get("data")}

    for cls in (
        ParserError,
        InvalidParams,
        InvalidRequest,
        MethodNotFound,
        InternalError,
    ):
        if code == cls.code:
            return cls(**kwargs)

    if -32099 <= code <= -32000:
        error = FlowError(**kwargs)
    else:
        error = JsonRPCException(**kwargs)

    error.code = code
    return error
