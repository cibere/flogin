import pytest

from flogin import Plugin, Query, Result, SearchHandler
from flogin.testing import PluginTester


@pytest.fixture
def plugin():
    return Plugin()


@pytest.fixture
def metadata():
    return PluginTester.create_bogus_plugin_metadata()


@pytest.fixture
def tester(plugin, metadata):
    return PluginTester(plugin, metadata=metadata)


class ReturnSingleResultHandler(SearchHandler):
    async def callback(self, query: Query):
        return Result("Title")


class ReturnListResultHandler(SearchHandler):
    async def callback(self, query: Query):
        return [Result("Title")]


class ReturnSingleStrHandler(SearchHandler):
    async def callback(self, query: Query):
        return "Title"


class ReturnListStrHandler(SearchHandler):
    async def callback(self, query: Query):
        return ["Title"]


class YieldSingleStrHandler(SearchHandler):
    async def callback(self, query: Query):
        yield "Title"


class YieldSingleResultHandler(SearchHandler):
    async def callback(self, query: Query):
        yield Result("Title")


handlers = [
    ReturnSingleResultHandler(),
    ReturnListResultHandler(),
    ReturnSingleStrHandler(),
    ReturnListStrHandler(),
    YieldSingleStrHandler(),
    YieldSingleResultHandler(),
]


@pytest.fixture(params=handlers, ids=lambda h: h.__class__.__name__)
def handler(plugin: Plugin, request: pytest.FixtureRequest):
    h = request.param
    plugin.register_search_handler(h)
    return h


@pytest.mark.asyncio
async def test_handler_result(tester: PluginTester, handler: SearchHandler):
    response = await tester.test_query("bar", keyword="foo")
    result = response.results[0]
    assert result.title == "Title"


@pytest.mark.asyncio
async def test_handler_error(plugin: Plugin, tester: PluginTester):
    @plugin.search()
    async def handler(query: Query):
        raise TypeError("Boo")

    @handler.error
    async def error_handler(query: Query, error: Exception):
        assert isinstance(error, TypeError)
        assert str(error) == "Boo"

    await tester.test_query("bar")
