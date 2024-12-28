from __future__ import annotations

import logging
import random
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Coroutine,
    Generic,
    Iterable,
    NotRequired,
    Self,
    TypedDict,
    TypeVarTuple,
    Unpack,
)

from .._types import PluginT, SearchHandlerCallbackReturns
from ..utils import MISSING, cached_property, copy_doc
from .base_object import Base
from .responses import ErrorResponse, ExecuteResponse

TS = TypeVarTuple("TS")
LOG = logging.getLogger(__name__)

__all__ = ("Result", "ResultPreview", "ProgressBar", "Glyph")


class Glyph(Base):
    r"""This represents a glyph object with flow launcher, which is an alternative to :class:`~flogin.jsonrpc.results.Result` icons.

    Attributes
    ----------
    text: :class:`str`
        The text to be shown in the glyph
    font_family: :class:`str`
        The font that the text should be shown in
    """

    __slots__ = "text", "font_family"
    __jsonrpc_option_names__ = {"text": "Glyph", "font_family": "FontFamily"}

    def __init__(self, text: str, font_family: str) -> None:
        self.text = text
        self.font_family = font_family

    @classmethod
    def from_dict(cls: type[Self], data: dict[str, Any]) -> Self:
        r"""Converts a dictionary into a :class:`Glyph` object.

        Parameters
        ----------
        data: dict[:class:`str`, Any]
            The dictionary
        """

        return cls(text=data["Glyth"], font_family=data["FontFamily"])


class ProgressBar(Base):
    r"""This represents the progress bar than can be shown on a result.

    .. NOTE::
        Visually, the progress bar takes the same spot as the title

    Attributes
    ----------
    percentage: :class:`int`
        The percentage of the progress bar that should be filled. must be 0-100.
    color: :class:`str`
        The color that the progress bar should be in hex code form. Defaults to #26a0da.
    """

    __slots__ = "percentage", "color"
    __jsonrpc_option_names__ = {
        "percentage": "ProgressBar",
        "color": "ProgressBarColor",
    }

    def __init__(self, percentage: int, color: str = MISSING) -> None:
        self.percentage = percentage
        self.color = color or "#26a0da"


class ResultPreview(Base):
    r"""Represents a result's preview.

    .. NOTE::
        Previews are finicky, and may not work 100% of the time

    Attributes
    ----------
    image_path: :class:`str`
        The path to the image to be shown
    description: Optional[:class:`str`]
        The description to be shown
    is_media: Optional[:class:`bool`]
        Whther the preview should be treated as media or not
    """

    __slots__ = "image_path", "description", "is_media", "preview_deligate"
    __jsonrpc_option_names__ = {
        "image_path": "previewImagePath",
        "is_media": "isMedia",
        "description": "description",
    }

    def __init__(
        self,
        image_path: str,
        *,
        description: str | None = None,
        is_media: bool = True,
    ) -> None:
        self.image_path = image_path
        self.description = description
        self.is_media = is_media


class ResultConstructorArgs(TypedDict):
    title: NotRequired[str | None]
    sub: NotRequired[str | None]
    icon: NotRequired[str | None]
    title_highlight_data: NotRequired[Iterable[int] | None]
    title_tooltip: NotRequired[str | None]
    sub_tooltip: NotRequired[str | None]
    copy_text: NotRequired[str | None]
    score: NotRequired[int | None]
    rounded_icon: NotRequired[bool | None]
    glyph: NotRequired[Glyph | None]


class Result(Base, Generic[PluginT]):
    r"""This represents a result that would be returned as a result for a query or context menu.

    For simple useage: create instances of this class as-is.

    For advanced useage (handling clicks and custom context menus), it is recommended to subclass the result object to create your own subclass.

    This class implements a generic for the :attr:`~flogin.jsonrpc.results.Result.plugin` attribute, which will be used for typechecking purposes.

    Subclassing
    ------------
    Subclassing lets you override the following methods: :func:`~flogin.jsonrpc.results.Result.callback` and :func:`~flogin.jsonrpc.results.Result.context_menu`. It also lets you create "universal" result properties (eg: same icon). Example:

    .. code-block:: python3

        class MyResult(Result):
            def __init__(self, title: str) -> None:
                super().__init__(self, title, icon="Images/app.png")

            async def callback(self):
                # handle what happens when the result gets clicked

            async def context_menu(self):
                # add context menu options to this result's context menu

    Attributes
    ----------
    title: :class:`str`
        The title/content of the result
    sub: Optional[:class:`str`]
        The subtitle to be shown.
    icon: Optional[:class:`str`]
        A path to the icon to be shown with the result. If this and :attr:`~flogin.jsonrpc.results.Result.glyph` are passed, the user's ``Use Segoe Fluent Icons`` setting will determine which is used.
    title_highlight_data: Optional[Iterable[:class:`int`]]
        The highlight data for the title. See the :ref:`FAQ section on highlights <highlights>` for more info.
    title_tooltip: Optional[:class:`str`]
        The text to be displayed when the user hovers over the result's title
    sub_tooltip: Optional[:class:`str`]
        The text to be displayed when the user hovers over the result's subtitle
    copy_text: Optional[:class:`str`]
        This is the text that will be copied when the user does ``CTRL+C`` on the result. If the text is a file/directory path, flow will copy the actual file/folder instead of just the path text.
    plugin: :class:`~flogin.plugin.Plugin` | None
        Your plugin instance. This is filled before :func:`~flogin.jsonrpc.results.Result.callback` or :func:`~flogin.jsonrpc.results.Result.context_menu` are triggered.
    preview: Optional[:class:`~flogin.jsonrpc.results.ResultPreview`]
        Customize the preview that is shown for the result. By default, the preview shows the result's title, subtitle, and icon
    progress_bar: Optional[:class:`~flogin.jsonrpc.results.ProgressBar`]
        The progress bar that could be shown in the place of the title
    auto_complete_text: Optional[:class:`str`]
        The text that will replace the :attr:`~flogin.query.Query.raw_text` in the flow menu when the autocomplete hotkey is used on the result. Defaults to the result's title.
    rounded_icon: Optional[:class:`bool`]
        Whether to have round the icon or not.
    glyph: Optional[:class:`~flogin.jsonrpc.results.Glyph`]
        The :class:`~flogin.jsonrpc.results.Glyph` object that will serve as the result's icon. If this and :attr:`~flogin.jsonrpc.results.Result.icon` are passed, the user's ``Use Segoe Fluent Icons`` setting will determine which is used.
    """

    def __init__(
        self,
        title: str | None = None,
        sub: str | None = None,
        icon: str | None = None,
        title_highlight_data: Iterable[int] | None = None,
        title_tooltip: str | None = None,
        sub_tooltip: str | None = None,
        copy_text: str | None = None,
        score: int | None = None,
        auto_complete_text: str | None = None,
        preview: ResultPreview | None = None,
        progress_bar: ProgressBar | None = None,
        rounded_icon: bool | None = None,
        glyph: Glyph | None = None,
    ) -> None:
        self.title = title
        self.sub = sub
        self.icon = icon
        self.title_highlight_data = title_highlight_data
        self.title_tooltip = title_tooltip
        self.sub_tooltip = sub_tooltip
        self.copy_text = copy_text
        self.score = score
        self.auto_complete_text = auto_complete_text
        self.preview = preview
        self.progress_bar = progress_bar
        self.rounded_icon = rounded_icon
        self.glyph = glyph
        self.plugin: PluginT | None = None

    async def on_error(self, error: Exception) -> ErrorResponse | ExecuteResponse:
        r"""|coro|

        Override this function to add an error response behavior to this result's callback.

        Parameters
        ----------
        error: :class:`Exception`
            The error that occured
        """
        LOG.exception(
            f"Ignoring exception in reuslt callback ({self!r})", exc_info=error
        )
        return ErrorResponse.internal_error(error)

    async def callback(self) -> ExecuteResponse:
        r"""|coro|

        Override this function to add a callback behavior to your result. This method will run when the user clicks on your result.

        Returns
        -------
        :class:`~flogin.jsonrpc.responses.ExecuteResponse`
            A response to flow determining whether or not to hide flow's menu
        """

        return ExecuteResponse(False)

    def context_menu(self) -> SearchHandlerCallbackReturns:
        r"""|coro|

        Override this function to add a context menu behavior to your result. This method will run when the user gets the context menu to your result.

        This method can return/yield almost anything, and flogin will convert it into a list of :class:`~flogin.jsonrpc.results.Result` objects before sending it to flow.

        Returns
        -------
        list[:class:`~flogin.jsonrpc.results.Result`] | :class:`~flogin.jsonrpc.results.Result` | str | Any
            A list of results, an results, or something that can be converted into a list of results.

        Yields
        ------
        :class:`~flogin.jsonrpc.results.Result` | str | Any
            A result object or something that can be converted into a result object.
        """
        ...

    def on_context_menu_error(self, error: Exception) -> SearchHandlerCallbackReturns:
        r"""|coro|

        Override this function to add an error response behavior to this result's context menu callback.

        If the error was handled:
            You can return/yield almost anything, and flogin will convert it into a list of :class:`~flogin.jsonrpc.results.Result` objects before sending it to flow.

        If the error was not handled:
            Return a :class:`~flogin.jsonrpc.responses.ErrorResponse` object

        Parameters
        ----------
        error: :class:`Exception`
            The error that occured

        Returns
        -------
        :class:`~flogin.jsonrpc.responses.ErrorResponse` | list[:class:`~flogin.jsonrpc.results.Result`] | :class:`~flogin.jsonrpc.results.Result` | str | Any
            A list of results, an results, or something that can be converted into a list of results.

        Yields
        ------
        :class:`~flogin.jsonrpc.results.Result` | str | Any
            A result object or something that can be converted into a result object.
        """
        ...

    if not TYPE_CHECKING:

        @copy_doc(context_menu)
        async def context_menu(self):
            return []

        @copy_doc(on_context_menu_error)
        async def on_context_menu_error(self, error: Exception):
            LOG.exception(
                f"Ignoring exception in result's context menu callback ({self!r})",
                exc_info=error,
            )
            return ErrorResponse.internal_error(error)

    def to_dict(self) -> dict[str, Any]:
        r"""This converts the result into a json serializable dictionary

        Returns
        -------
        dict[:class:`str`, Any]
        """

        x: dict[str, Any] = {}

        if self.title is not None:
            x["title"] = self.title
        if self.sub is not None:
            x["subTitle"] = self.sub
        if self.icon is not None:
            x["icoPath"] = self.icon
        if self.title_highlight_data is not None:
            x["titleHighlightData"] = self.title_highlight_data
        if self.title_tooltip is not None:
            x["titleTooltip"] = self.title_tooltip
        if self.sub_tooltip is not None:
            x["subtitleTooltip"] = self.sub_tooltip
        if self.copy_text is not None:
            x["copyText"] = self.copy_text
        if self.callback is not None:
            x["jsonRPCAction"] = {"method": f"flogin.action.{self.slug}"}
        if self.context_menu is not None:
            x["ContextData"] = [self.slug]
        if self.score is not None:
            x["score"] = self.score
        if self.preview is not None:
            x["preview"] = self.preview.to_dict()
        if self.auto_complete_text is not None:
            x["autoCompleteText"] = self.auto_complete_text
        if self.progress_bar is not None:
            x.update(self.progress_bar.to_dict())
        if self.rounded_icon is not None:
            x["RoundedIcon"] = self.rounded_icon
        if self.glyph is not None:
            x["Glyph"] = self.glyph.to_dict()
        return x

    @classmethod
    def from_dict(cls: type[Self], data: dict[str, Any]) -> Self:
        r"""Creates a Result from a dictionary

        .. NOTE::
            This method does NOT fill the :func:`~flogin.jsonrpc.results.Result.callback` or :func:`~flogin.jsonrpc.results.Result.context_menu` attributes.

        Parameters
        ----------
        data: dict[:class:`str`, Any]
            The valid dictionary that includes the result data

        Raises
        ------
        :class:`KeyError`
            The dictionary did not include the only required field, ``title``.

        Returns
        --------
        :class:`Result`
        """

        return cls(
            title=data["title"],
            sub=data.get("subTitle"),
            icon=data.get("icoPath"),
            title_highlight_data=data.get("titleHighlightData"),
            title_tooltip=data.get("titleTooltip"),
            sub_tooltip=data.get("subtitleTooltip"),
            copy_text=data.get("copyText"),
        )

    @classmethod
    def from_anything(cls: type[Result], item: Any) -> Result:
        if isinstance(item, dict):
            return cls.from_dict(item)
        elif isinstance(item, Result):
            return item
        else:
            return cls(str(item))

    @classmethod
    def create_with_partial(
        cls: type[Result],
        partial_callback: Callable[[], Coroutine[Any, Any, Any]],
        **kwargs: Unpack[ResultConstructorArgs],
    ) -> Result:
        r"""A quick and easy way to create a result with a callback without subclassing.

        .. NOTE::
            This is meant to be used with :class:`~flogin.flow.api.FlowLauncherAPI` methods

        Example
        --------
        .. code-block:: python3

            result = Result.create_with_partial(
                functools.partial(
                    plugin.api.show_notification,
                    "notification title",
                    "notification content"
                ),
                title="Result title",
                sub="Result subtitle"
            )

        Parameters
        ----------
        partial_callback: partial :ref:`coroutine <coroutine>`
            The callback wrapped in :obj:`functools.partial`
        kwargs: See allowed kwargs here: :class:`~flogin.jsonrpc.results.Result`
            The args that will be passed to the :class:`~flogin.jsonrpc.results.Result` constructor
        """

        self = cls(**kwargs)
        self.callback = partial_callback
        return self

    @cached_property
    def slug(self) -> str:
        return "".join(
            random.choices(
                "QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890", k=15
            )
        )

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.title=} {self.sub=} {self.icon=} {self.title_highlight_data=} {self.title_tooltip=} {self.sub_tooltip=} {self.copy_text=} {self.score=} {self.auto_complete_text=} {self.preview=} {self.progress_bar=} {self.rounded_icon=} {self.glyph=}>"
