from __future__ import annotations

from collections.abc import Iterable
from typing import NotRequired

from typing_extensions import TypedDict


class RawRPCAction(TypedDict):
    method: str


class RawPreview(TypedDict):
    previewImagePath: str
    isMedia: NotRequired[bool | None]
    description: NotRequired[str | None]


class RawGlyph(TypedDict):
    glyph: str
    fontFamily: str


class RawProgressBar(TypedDict):
    progressBar: NotRequired[int]
    progressBarColor: NotRequired[str]


class RawResult(RawProgressBar):
    title: NotRequired[str]
    subTitle: NotRequired[str]
    icoPath: NotRequired[str]
    titleTooltip: NotRequired[str]
    subtitleTooltip: NotRequired[str]
    copyText: NotRequired[str]
    titleHighlightData: NotRequired[Iterable[int]]
    jsonRPCAction: NotRequired[RawRPCAction]
    contextData: NotRequired[Iterable[str]]
    score: NotRequired[int]
    preview: NotRequired[RawPreview]
    autoCompleteText: NotRequired[str]
    roundedIcon: NotRequired[bool]
    glyph: NotRequired[RawGlyph]
