from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

from ..utils import MISSING
from .base_object import ToMessageBase
from .enums import ErrorCode

if TYPE_CHECKING:
    from .._types.jsonrpc.responses import (
        ErrorPayload,
    )
    from .._types.jsonrpc.responses import (
        RawErrorResponse as ErrorResponsePayload,
    )
    from .._types.jsonrpc.responses import (
        RawExecuteResponse as ExecuteResponsePayload,
    )
    from .._types.jsonrpc.responses import (
        RawQueryResponse as QueryResponsePayload,
    )
    from .results import Result

T = TypeVar("T")

__all__ = (
    "ErrorResponse",
    "ExecuteResponse",
    "QueryResponse",
)


class BaseResponse(ToMessageBase[T], Generic[T]):
    r"""This represents a response to flow.

    .. WARNING::
        This class is NOT to be used as is. Use one of it's subclasses instead.
    """

    def to_message(self, id: int) -> bytes:
        return (
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": id,
                }
                | cast("dict[Any, Any]", self.to_dict())
            )
            + "\r\n"
        ).encode()


class ErrorResponse(BaseResponse["ErrorResponsePayload"]):
    r"""This represents an error sent to or from flow.

    Attributes
    --------
    code: :class:`int`
        The error code for the error
    message: :class:`str`
        The error's message
    data: Optional[Any]
        Any extra data
    """

    __slots__ = "code", "data", "message"

    def __init__(self, code: int, message: str, data: Any | None = None) -> None:
        self.code = code
        self.message = message
        self.data = data

    def to_dict(self) -> ErrorResponsePayload:
        data = self.data
        if isinstance(data, Exception):
            data = f"{data}"
        return {"error": {"code": self.code, "message": self.message, "data": data}}

    @classmethod
    def from_dict(
        cls: type[ErrorResponse], data: ErrorPayload | ErrorResponsePayload
    ) -> ErrorResponse:
        if "error" in data:
            data = data["error"]
        return cls(code=data["code"], message=data["message"], data=data.get("data"))

    @classmethod
    def internal_error(cls: type[ErrorResponse], data: Any = None) -> ErrorResponse:
        return cls(
            code=ErrorCode.server_error_start.value, message="Internal error", data=data
        )


class QueryResponse(BaseResponse["QueryResponsePayload"]):
    r"""This response represents the response from search handler's callbacks and context menus. See the :ref:`search handler section <search_handlers>` for more information about using search handlers.

    Attributes
    --------
    results: list[:class:`~flogin.jsonrpc.results.Result`]
        The results to be sent as the result of the query
    settings_changes: dict[:class:`str`, Any]
        Any changes to be made to the plugin's settings.
    debug_message: :class:`str`
        A debug message if you want
    """

    __slots__ = "debug_message", "results", "settings_changes"

    def __init__(
        self,
        results: list[Result],
        settings_changes: dict[str, Any] | None = None,
        debug_message: str = MISSING,
    ) -> None:
        self.results = results
        self.settings_changes = settings_changes or {}
        self.debug_message = debug_message or ""

    def to_dict(self) -> QueryResponsePayload:
        return {
            "result": {
                "settingsChange": self.settings_changes,
                "debugMessage": self.debug_message or "",
                "result": [res.to_dict() for res in self.results],
            }
        }


class ExecuteResponse(BaseResponse["ExecuteResponsePayload"]):
    r"""This response is a generic response for jsonrpc requests, most notably result callbacks.

    Attributes
    --------
    hide: :class:`bool`
        Whether to hide the flow menu after execution or not
    """

    __slots__ = ("hide",)

    def __init__(self, hide: bool = True) -> None:
        self.hide = hide

    def to_dict(self) -> ExecuteResponsePayload:
        return {"result": {"hide": self.hide}}
