# pyright: basic

from typing import Any

import pytest

from flogin.jsonrpc.base_object import Base, ToMessageBase


class SecondChild(Base):
    __slots__ = ("foo",)

    def __init__(self, foo: int = 10) -> None:
        self.foo = foo


class TestBase:
    @pytest.fixture(
        params=[
            ({"test": 5, "best": 10}, {}, {"test": 5, "best": 10}),
            ({"test": 5, "best": 10}, {"test": "car"}, {"car": 5, "best": 10}),
            (
                {"child": SecondChild(), "bar": 10},
                {},
                {"child": {"foo": 10}, "bar": 10},
            ),
            (
                {
                    "children": [SecondChild(5), SecondChild(6), SecondChild(7)],
                    "bar": 10,
                },
                {},
                {"children": [{"foo": 5}, {"foo": 6}, {"foo": 7}], "bar": 10},
            ),
        ]
    )
    def base_test_case(
        self, request: pytest.FixtureRequest
    ) -> tuple[dict[str, Any], dict[str, str], dict[str, Any]]:
        return request.param

    def test_to_dict(
        self, base_test_case: tuple[dict[str, Any], dict[str, str], dict[str, Any]]
    ) -> None:
        class Foo(Base):
            __slots__ = tuple(base_test_case[0].keys())
            __jsonrpc_option_names__ = base_test_case[1]

            def __init__(self) -> None:
                for key, value in base_test_case[0].items():
                    setattr(self, key, value)

        data = Foo().to_dict()
        assert data == base_test_case[2]


def test_message_base():
    class Foo(SecondChild, ToMessageBase): ...

    assert Foo().to_message(5) == b'{"foo": 10}\r\n'
