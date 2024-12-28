from __future__ import annotations

from typing import Any


class FillerObject:
    def __init__(self, text: str):
        self.__error_text__ = text

    def __getattribute__(self, name: str) -> Any:
        if name == "__error_text__":
            return super().__getattribute__(name)

        raise RuntimeError(self.__error_text__)
