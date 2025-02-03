# pyright: basic

import copy
import secrets

import pytest

from flogin import Plugin, Query, Result
from flogin.utils import MISSING


def _create_query(
    text: str, plugin: Plugin, keyword: str = "*", is_requery: bool = False
):
    return Query(
        {
            "rawQuery": f"{keyword} {text}",
            "search": text,
            "actionKeyword": keyword,
            "isReQuery": False,
        },
        plugin,
    )


@pytest.fixture
def randquery(plugin: Plugin):
    keyword = secrets.token_hex(5)
    text = secrets.token_hex(10)

    return _create_query(text=text, plugin=plugin, keyword=keyword)


@pytest.fixture
def fooquery(plugin: Plugin):
    return _create_query(text="foo", plugin=plugin, keyword="bar")


@pytest.fixture
def fooquery2(plugin: Plugin):
    return _create_query(text="foo", plugin=plugin, keyword="bar")


@pytest.fixture
def plugin() -> Plugin:
    return Plugin()


def test_props(plugin: Plugin) -> None:
    raw_query = "raw query"
    text = "search text"
    keyword = "action keyword"
    requery = True

    query = Query(
        {
            "rawQuery": raw_query,
            "search": text,
            "actionKeyword": keyword,
            "isReQuery": requery,
        },
        plugin,
    )

    assert query.is_requery is requery
    assert query.keyword == keyword
    assert query.text == text
    assert query.raw_text == raw_query


def test_eq(fooquery: Query, fooquery2: Query, randquery: Query) -> None:
    assert fooquery != randquery
    assert fooquery == fooquery2
    assert fooquery != 5


def test_hash(fooquery: Query) -> None:
    assert hash(fooquery) == hash(fooquery.raw_text)


@pytest.mark.asyncio
async def test_update_results(fooquery: Query) -> None:
    test_results = [Result("Title", "sub"), Result("foo", "bar")]

    class MockApi:
        async def update_results(self, raw_query: str, results: list[Result]) -> None:
            assert fooquery.raw_text == raw_query
            assert results == test_results

    fooquery.plugin.api = MockApi()  # type: ignore

    await fooquery.update_results(test_results)


class TestUpdateMethod:
    @pytest.fixture(
        params=[
            # text, keyword, requery, raw_text
            # text cases
            (None, MISSING, False, "{original.keyword}"),
            ("bar", MISSING, False, "{original.keyword} bar"),
            # keyword cases
            (MISSING, None, False, "{original.text}"),
            (MISSING, "Bar", False, "Bar {original.text}"),
            (MISSING, "*", False, "{original.text}"),
            # requery case
            (MISSING, MISSING, True, "{original.raw_text}"),
            (MISSING, MISSING, False, "{original.raw_text}"),
        ]
    )
    def update_test_case(
        self, request: pytest.FixtureRequest
    ) -> tuple[str | None, str | None, bool, str]:
        return request.param

    @pytest.mark.asyncio
    async def test(
        self,
        fooquery: Query,
        update_test_case: tuple[str | None, str | None, bool, str],
    ) -> None:
        original = copy.copy(fooquery)

        class MockApi:
            async def change_query(self, new_query: str, requery: bool = False) -> None:
                assert new_query == update_test_case[3].format(original=original)
                assert requery == update_test_case[2]

        fooquery.plugin.api = MockApi()  # type: ignore

        await fooquery.update(
            text=update_test_case[0],
            keyword=update_test_case[1],
            requery=update_test_case[2],
        )
