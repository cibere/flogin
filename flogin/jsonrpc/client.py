from __future__ import annotations

import asyncio
import json
import logging
from typing import TYPE_CHECKING, Any

from .errors import (
    InternalError,
    MethodNotFound,
)
from .errors import (
    get_exception_from_json as _get_jsonrpc_error_from_json,
)
from .requests import Request
from .responses import BaseResponse, ErrorResponse

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from asyncio.streams import StreamReader, StreamWriter

    from .._types.jsonrpc.request import (
        Request as RequestPayload,
    )
    from .._types.jsonrpc.request import (
        RequestResult as RequestResultPayload,
    )
    from ..plugin import Plugin

__all__ = ("JsonRPCClient",)


class JsonRPCClient:
    reader: StreamReader
    writer: StreamWriter

    def __init__(self, plugin: Plugin[Any]) -> None:
        self.tasks: dict[int, asyncio.Task[BaseResponse[Any]]] = {}
        self.requests: dict[int, asyncio.Future[Any | ErrorResponse]] = {}
        self._current_request_id = 1
        self.plugin = plugin
        self.ignore_cancellations: bool = plugin.options.get(
            "ignore_cancellation_requests", False
        )

    @property
    def request_id(self) -> int:
        self._current_request_id += 1
        return self._current_request_id

    @request_id.setter
    def request_id(self, value: int) -> None:
        self._current_request_id = value

    async def request(self, method: str, params: list[Any] | None = None) -> Any:
        if params is None:
            params = []

        fut: asyncio.Future[Any] = asyncio.Future()
        rid = self.request_id
        self.requests[rid] = fut
        msg = Request(method, rid, params).to_message(rid)
        await self.write(msg, drain=False)
        return await fut

    async def handle_cancellation(self, id: int) -> None:
        if self.ignore_cancellations:
            return log.debug("Ignoring cancellation request of %r", id)

        if id in self.tasks:
            task = self.tasks.pop(id)
            success = task.cancel()
            if success:
                log.debug("Successfully cancelled task with id %r", id)
            else:
                log.exception("Failed to cancel task with id of %r, task=%r", id, task)
        else:
            log.exception(
                "Failed to cancel task with id of %r, could not find task.", id
            )

    async def handle_result(self, result: RequestResultPayload[Any]) -> None:
        rid = result["id"]

        log.debug("Result: %r, %r", rid, result)
        if rid in self.requests:
            try:
                self.requests.pop(rid).set_result(result)
            except asyncio.InvalidStateError:
                pass
        else:
            log.error(
                "Result from unknown request given. id=%r, result=%r", rid, result
            )

    async def handle_error(self, id: int, error: ErrorResponse) -> None:
        if id in self.requests:
            self.requests.pop(id).set_exception(
                _get_jsonrpc_error_from_json(error.to_dict()["error"])
            )
        else:
            log.error("Error response received for unknown request, id=%r", id)

    async def handle_notification(self, method: str, params: dict[str, Any]) -> None:
        if method == "$/cancelRequest":
            await self.handle_cancellation(params["id"])
        else:
            err = MethodNotFound(f"Notification Method {method!r} Not Found")

            log.exception(
                "Unknown notification method received: %r",
                method,
                exc_info=err,
            )

    async def handle_request(self, request: RequestPayload) -> None:
        method: str = request["method"]
        params: list[Any] = request.get("params", [])
        task = None

        self.request_id = request["id"]

        if method.startswith("flogin.action"):
            task = self.plugin.process_action(method)

        if task is None:
            task = self.plugin.dispatch(method, *params)
            if not task:
                err = MethodNotFound(f"Request method {method!r} was not found")
                log.exception(
                    "Unknown request method received: %r",
                    method,
                    exc_info=err,
                )
                return await self.write(err.to_response().to_message(id=request["id"]))

        self.tasks[request["id"]] = task
        result = await task

        if isinstance(result, BaseResponse):
            return await self.write(result.to_message(id=request["id"]))
        err = InternalError("Internal Error: Invalid Response Object", repr(result))
        log.exception(
            "Invalid Response Object: %r",
            result,
            exc_info=err,
        )
        return await self.write(err.to_response().to_message(id=request["id"]))

    async def process_input(self, line: str) -> None:
        message = json.loads(line)

        if "id" not in message:
            log.debug("Received notification: %r", message)
            await self.handle_notification(message["method"], message["params"])
        elif "method" in message:
            log.debug("Received request: %r", message)
            await self.handle_request(message)
        elif "result" in message:
            log.debug("Received result: %r", message)
            await self.handle_result(message)
        elif "error" in message:
            log.exception("Received error: %r", message)
            await self.handle_error(
                message["id"], ErrorResponse.from_dict(message["error"])
            )
        else:
            err = InternalError("Unknown message type received", line)
            log.exception(
                "Unknown message type received",
                exc_info=err,
            )

    async def start_listening(self, reader: StreamReader, writer: StreamWriter) -> None:
        self.reader = reader
        self.writer = writer

        stream_log = logging.getLogger("flogin.stream_reader")
        tasks: set[asyncio.Task[None]] = set()

        while 1:
            async for line in reader:
                stream_log.debug("Received line: %r", line)
                line = line.decode("utf-8")
                if line == "":
                    continue

                task = asyncio.create_task(self.process_input(line))
                tasks.add(task)
                task.add_done_callback(tasks.discard)

    async def write(self, msg: bytes, drain: bool = True) -> None:
        log.debug("Sending: %r", msg)
        self.writer.write(msg)
        if drain:
            await self.writer.drain()
