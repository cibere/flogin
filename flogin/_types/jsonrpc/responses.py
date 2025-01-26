from __future__ import annotations

from typing import Literal, NotRequired, TypedDict

from ..json import Jsonable
from ..settings import RawSettings
from .result import RawResult


class BaseResponse(TypedDict):
    id: int
    jsonrpc: Literal["2.0"]


class ErrorPayload(TypedDict):
    code: int
    message: str
    data: NotRequired[Jsonable]


class RawErrorResponse(TypedDict):
    error: ErrorPayload


class ErrorResponse(BaseResponse, RawErrorResponse):
    pass


class QueryPayload(TypedDict):
    settingsChange: RawSettings
    debugMessage: str
    result: list[RawResult]


class RawQueryResponse(TypedDict):
    result: QueryPayload


class QueryResponse(BaseResponse, RawQueryResponse):
    pass


class ExecutePayload(TypedDict):
    hide: bool


class RawExecuteResponse(TypedDict):
    result: ExecutePayload


class ExecuteResponse(BaseResponse, RawExecuteResponse):
    pass
