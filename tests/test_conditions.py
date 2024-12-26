import re

import pytest

from flogin import (
    AllCondition,
    AnyCondition,
    KeywordCondition,
    PlainTextCondition,
    Query,
    RegexCondition,
)
from flogin.testing.filler import FillerObject


def _create_query(text: str, plugin, keyword: str = "*", is_requery: bool = False):
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
def plugin():
    return FillerObject(f"Fake plugin object provided")


@pytest.fixture
def yes_query(plugin):
    return _create_query(text="foo", keyword="bar", plugin=plugin)


@pytest.fixture
def no_query(plugin):
    return _create_query(text="apple", keyword="car", plugin=plugin)


@pytest.fixture(params=[0, 1])
def query(yes_query: Query, no_query: Query, request: pytest.FixtureRequest):
    return [yes_query, no_query][request.param]


conditions = {
    "PlainTextCondition": PlainTextCondition("foo"),
    "RegexCondition": RegexCondition(re.compile(r"^[foo]*$")),
    "KeywordCondition-Allowed": KeywordCondition(allowed_keywords="bar"),
    "KeywordCondition-Disallowed": KeywordCondition(disallowed_keywords="car"),
    "CustomCondition": lambda q: q.text == "foo",
}


@pytest.fixture(params=conditions.values(), ids=list(conditions.keys()))
def condition(request):
    return request.param


def test_conditions_1(condition, yes_query: Query):
    res = condition(yes_query)
    assert res == True


def test_conditions_2(condition, no_query: Query):
    res = condition(no_query)
    assert res == False


allcondition_yes_tests = [
    AllCondition(
        conditions["PlainTextCondition"],
        conditions["RegexCondition"],
    ),
    AllCondition(
        conditions["KeywordCondition-Allowed"],
        conditions["CustomCondition"],
    ),
    AllCondition(
        conditions["KeywordCondition-Allowed"],
        conditions["KeywordCondition-Disallowed"],
    ),
    AllCondition(
        conditions["KeywordCondition-Disallowed"],
        conditions["RegexCondition"],
    ),
]
allcondition_no_tests = [
    AllCondition(
        cond,
        lambda q: q.text == "bar",
    )
    for cond in conditions.values()
]


class TestAllCondition:
    @pytest.fixture(scope="class", params=allcondition_yes_tests)
    def allcondition_yes(self, request: pytest.FixtureRequest):
        return request.param

    @pytest.fixture(scope="class", params=allcondition_no_tests)
    def allcondition_no(self, request: pytest.FixtureRequest):
        return request.param

    def test_allcondition_1(self, allcondition_yes: AllCondition, yes_query: Query):
        res = allcondition_yes(yes_query)
        assert res == True

    def test_allcondition_2(self, allcondition_yes: AllCondition, no_query: Query):
        res = allcondition_yes(no_query)
        assert res == False

    def test_allcondition_3(self, allcondition_no: AllCondition, query: Query):
        res = allcondition_no(query)
        assert res == False

    def test_condition_data(self, yes_query: Query):
        def condition1(query: Query):
            query.condition_data = 25
            return True

        def condition2(query: Query):
            query.condition_data = 20
            return True

        cond = AllCondition(condition1, condition2)
        assert cond(yes_query) == True
        assert yes_query.condition_data == {
            condition2: 20,
            condition1: 25,
        }


anycondition_yes_tests = [
    AnyCondition(
        PlainTextCondition("foo"),
        PlainTextCondition("apple"),
    )
]
anycondition_no_tests = [
    AnyCondition(
        PlainTextCondition("bar"),
        PlainTextCondition("car"),
    )
]


class TestAnyCondition:
    @pytest.fixture(scope="class", params=anycondition_yes_tests)
    def anycondition_yes(self, request: pytest.FixtureRequest):
        return request.param

    @pytest.fixture(scope="class", params=anycondition_no_tests)
    def anycondition_no(self, request: pytest.FixtureRequest):
        return request.param

    def test_multicondition_any_1(self, anycondition_yes: AnyCondition, query: Query):
        res = anycondition_yes(query)
        assert res == True

    def test_multicondition_any_2(self, anycondition_no: AnyCondition, query: Query):
        res = anycondition_no(query)
        assert res == False

    def test_condition_data(self, yes_query: Query):
        def condition(query: Query):
            query.condition_data = 25
            return True

        cond = AnyCondition(
            condition,
        )
        assert cond(yes_query) == True
        assert yes_query.condition_data == (condition, 25)
