from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base_object import ToMessageBase

if TYPE_CHECKING:
    from .._types.jsonrpc.request import Request as RequestPayload

__all__ = ("Request",)


class Request(ToMessageBase["RequestPayload"]):
    __slots__ = "id", "method", "params"

    def __init__(self, method: str, id: int, params: list[Any] | None = None) -> None:
        self.method = method
        self.id = id
        self.params = params

    def to_dict(self) -> RequestPayload:
        x = super().to_dict()
        x["jsonrpc"] = "2.0"
        return x
