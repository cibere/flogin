from __future__ import annotations

import asyncio
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Coroutine,
    Generator,
    Generic,
    ParamSpec,
    TypeVar,
)

if TYPE_CHECKING:
    from .api import FlowLauncherAPI

P = ParamSpec("P")
CT = TypeVar("CT")


class FlowAPIMethod(Generic[CT]):
    def __init__(
        self,
        callback: Callable[P, Generator[Any, Any, CT]],
        *args: P.args,
        **kwargs: P.kwargs,
    ):
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.api_requester: Callable[..., Awaitable[Any]] | None = None

    async def __call__(self) -> CT:
        gen = self.callback(*self.args, **self.kwargs)
        data = next(gen)

        if self.api_requester is None:
            raise RuntimeError("No API Endpoint has been set")

        raw_resp = await self.api_requester(*data)

        try:
            gen.send(raw_resp)
        except StopIteration as e:
            resp = e.value
        else:
            raise RuntimeError("Something went wrong")

        return resp

    def __await__(self):
        return self.__call__().__await__()

    def _prep_batch(self) -> tuple[asyncio.Future, asyncio.Future, asyncio.Task]:
        api_future = asyncio.Future()
        data_future = asyncio.Future()

        async def api_requester(method: str, params: list[Any]):
            data = {}
            data["method"] = method
            data["params"] = params
            data_future.set_result(data)
            return await api_future

        self.api_requester = api_requester

        return (
            api_future,
            data_future,
            asyncio.create_task(self(), name="flogin.flowapi"),
        )


class _flow_api_method(Generic[CT]):
    def __init__(
        self, func: Callable[P, Generator[tuple[str, list[Any]], Any, CT]]
    ) -> None:
        self.func = func
        self.parent: FlowLauncherAPI | None = None

    def __call__(self, *args, **kwargs) -> FlowAPIMethod[CT]:
        endpoint = FlowAPIMethod(self.func, *args, **kwargs)
        if self.parent is not None:
            endpoint.args = (self.parent, *args)  # type: ignore
            endpoint.api_requester = self.parent.jsonrpc.request
        return endpoint


if TYPE_CHECKING:

    def flow_api_method(
        gen: Callable[P, Generator[tuple[str, list[Any]], Any, CT]]
    ) -> Callable[P, FlowAPIMethod[CT]]:
        return gen  # type: ignore

else:
    flow_api_method = _flow_api_method

T = TypeVar("T")

Gen = Generator[tuple[str, list[Any]], Any, T]
