from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .enums import ErrorCode
from .responses import ErrorResponse

if TYPE_CHECKING:
    from .._types.jsonrpc.responses import ErrorPayload

__all__ = (
    "FlowError",
    "InternalError",
    "InvalidParams",
    "InvalidRequest",
    "JsonRPCException",
    "MethodNotFound",
    "ParserError",
)


class JsonRPCException(Exception):
    r"""This is a generic class representing a JsonRPCException

    Attributes
    ----------
    code: :class:`int`
        The JsonRPC Error Code

        .. versionadded: 2.0.0
    message: :class:`str`
        The message sent with the error

        .. versionadded: 2.0.0
    data: Optional[Any]
        Any data sent with the error

        .. versionadded: 2.0.0
    """

    code: int

    def __init__(self, message: str, data: Any | None = None) -> None:
        self.message = message
        self.data = data

    def to_response(self) -> ErrorResponse:
        return ErrorResponse(self.code, self.message, self.data)


class ParserError(JsonRPCException):
    r"""This is a specialized JsonRPCException specifically for the error code -32700, which should mean that flogin sent invalid data and flow was unable to parse it.

    .. versionadded: 2.0.0

    Attributes
    ----------
    code: :class:`int` = -32700
        The JsonRPC Error Code
    message: :class:`str`
        The message sent with the error
    data: Optional[Any]
        Any data sent with the error
    """

    code = ErrorCode.parser_error.value


class InvalidRequest(JsonRPCException):
    r"""This is a specialized JsonRPCException specifically for the error code -32600, which should mean that flogin sent an invalid request object.

    .. versionadded: 2.0.0

    Attributes
    ----------
    code: :class:`int` = -32600
        The JsonRPC Error Code
    message: :class:`str`
        The message sent with the error
    data: Optional[Any]
        Any data sent with the error
    """

    code = ErrorCode.invalid_request.value


class MethodNotFound(JsonRPCException):
    r"""This is a specialized JsonRPCException specifically for the error code -32601, which should mean that flogin is attempting to use a method that doesn't exist.

    .. versionadded: 2.0.0

    Attributes
    ----------
    code: :class:`int` = -32601
        The JsonRPC Error Code
    message: :class:`str`
        The message sent with the error
    data: Optional[Any]
        Any data sent with the error
    """

    code = ErrorCode.method_not_found.value


class InvalidParams(JsonRPCException):
    r"""This is a specialized JsonRPCException specifically for the error code -32602, which should mean that flogin is attempting to use a method, but is sending the wrong parameters.

    .. versionadded: 2.0.0

    Attributes
    ----------
    code: :class:`int` = -32602
        The JsonRPC Error Code
    message: :class:`str`
        The message sent with the error
    data: Optional[Any]
        Any data sent with the error
    """

    code = ErrorCode.invalid_params.value


class InternalError(JsonRPCException):
    r"""This is a specialized JsonRPCException specifically for the error code -32603, which should mean that flogin has received an error.

    .. versionadded: 2.0.0

    Attributes
    ----------
    code: :class:`int` = -32603
        The JsonRPC Error Code
    message: :class:`str`
        The message sent with the error
    data: Optional[Any]
        Any data sent with the error
    """

    code = ErrorCode.internal_error.value


class FlowError(JsonRPCException):
    r"""This is a specialized JsonRPCException specifically for error codes between -32000 and -32099, which means that flow has ran into an error.

    .. versionadded: 2.0.0

    Attributes
    ----------
    code: :class:`int`
        The JsonRPC Error Code
    message: :class:`str`
        The message sent with the error
    data: Optional[Any]
        Any data sent with the error
    """

    code = ErrorCode.server_error_start.value


def get_exception_from_json(data: ErrorPayload) -> JsonRPCException:
    code = data["code"]
    kwargs: dict[str, Any] = {"message": data["message"], "data": data.get("data")}

    for cls in (
        ParserError,
        InvalidParams,
        InvalidRequest,
        MethodNotFound,
        InternalError,
    ):
        if code == cls.code:
            return cls(**kwargs)

    if ErrorCode.server_error_start.value <= code <= ErrorCode.server_error_end.value:
        error = FlowError(**kwargs)
    else:
        error = JsonRPCException(**kwargs)

    error.code = code
    return error
