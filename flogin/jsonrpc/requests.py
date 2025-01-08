from __future__ import annotations

from typing import Any

from .base_object import ToMessageBase

__all__ = ("Request",)


class Request(ToMessageBase):
    __slots__ = "id", "method", "params"

    def __init__(self, method: str, id: int, params: list[Any] | None = None) -> None:
        self.method = method
        self.id = id
        self.params = params

    def to_dict(self) -> dict:
        x = super().to_dict()
        x["jsonrpc"] = "2.0"
        return x
