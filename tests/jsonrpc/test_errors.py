# pyright: basic

from typing import TYPE_CHECKING, Any

import pytest

from flogin.jsonrpc.errors import (
    ErrorCode,
    FlowError,
    InternalError,
    InvalidParams,
    InvalidRequest,
    JsonRPCException,
    MethodNotFound,
    ParserError,
    get_exception_from_json,
)

if TYPE_CHECKING:
    from flogin._types.jsonrpc.responses import ErrorPayload
else:
    ErrorPayload = dict[str, Any]


def test_base_exception():
    error = JsonRPCException("message", "data")
    error.code = 0
    assert error.message == "message"
    assert error.data == "data"

    resp = error.to_response()
    assert resp.code == 0
    assert resp.message == "message"
    assert resp.data == "data"


"""
FlowError
InternalError
InvalidParams
InvalidRequest
JsonRPCException
MethodNotFound
ParserError
"""

_get_exception_cases: list[tuple[int, type[JsonRPCException]]] = [
    (ErrorCode.parser_error.value, ParserError),
    (ErrorCode.method_not_found.value, MethodNotFound),
    (ErrorCode.invalid_params.value, InvalidParams),
    (ErrorCode.invalid_request.value, InvalidRequest),
    (ErrorCode.internal_error.value, InternalError),
    (ErrorCode.server_error.value, FlowError),
    (0, JsonRPCException),
]
_get_exception_cases.extend(
    (num, FlowError)
    for num in range(
        ErrorCode.server_error_end.value, ErrorCode.server_error_start.value
    )
)


@pytest.fixture(params=_get_exception_cases)
def get_exception_case(
    request: pytest.FixtureRequest,
) -> tuple[ErrorPayload, type[JsonRPCException]]:
    return ({"code": request.param[0], "message": "msg"}, request.param[1])


def test_get_exception(get_exception_case: tuple[ErrorPayload, type[JsonRPCException]]):
    payload, error_type = get_exception_case

    error = get_exception_from_json(payload)
    # assert type(error) is error_type
    assert isinstance(error, error_type)
