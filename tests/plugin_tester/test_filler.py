# pyright: basic

import pytest

from flogin.testing.filler import FillerObject


def test_filler_object():
    obj = FillerObject("this is a test")

    with pytest.raises(RuntimeError, match="this is a test"):
        obj.test
