import pytest

from flogin import Settings


@pytest.fixture
def settings():
    return Settings({"foo": 0})


def test_settings_get_key(settings: Settings):
    assert settings["foo"] == 0


def test_settings_get_attr(settings: Settings):
    assert settings.foo == 0


def test_settings_set_key(settings: Settings):
    settings["foo"] = 1
    assert settings["foo"] == 1


def test_settings_set_attr(settings: Settings):
    settings.foo = 1
    assert settings.foo == 1


def test_update_settings(settings: Settings):
    settings._update({"bar": 25})
    assert settings.bar == 25


def test_get_updates(settings: Settings):
    settings.setting = 10
    updates = settings._get_updates()
    assert updates == {"setting": 10}


def test_get_nonexistant_key(settings: Settings):
    val = settings.a_random_key
    assert val == None
