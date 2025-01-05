from enum import Enum


class ErrorCode(Enum):
    parser_error = -32700
    invalid_request = -32600
    method_not_found = -32601
    invalid_params = -32602
    internal_error = -32603

    # server error is a range, -32099 through -32000
    server_error_start = -32000
    server_error_end = -32099

    # alias for the start
    server_error = -32000
