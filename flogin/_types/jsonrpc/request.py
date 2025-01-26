from typing import Generic, Literal, NotRequired, TypedDict, TypeVar

T = TypeVar("T")


class Request(TypedDict):
    id: int
    method: str
    params: NotRequired[list[str | int]]
    jsonrpc: Literal["2.0"]


class RequestResult(TypedDict, Generic[T]):
    id: int
    jsonrpc: Literal["2.0"]
    result: T
