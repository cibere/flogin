# pyright: basic

import pytest

from flogin.flow.base import Base, add_prop


class Foo(Base):
    bar = add_prop("bar")


def test_prop_no_default_success():
    foo = Foo({"bar": 5})
    assert foo.bar == 5


def test_prop_no_default_fail():
    foo2 = Foo({})
    with pytest.raises(KeyError):
        assert foo2.bar == 5


class Bar(Base):
    foo = add_prop("foo", default=10)


def test_prop_default_success():
    bar = Bar({"foo": 5})
    assert bar.foo == 5


def test_prop_default_fail():
    bar = Bar({})
    assert bar.foo == 10
