from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import re
    from collections.abc import Iterable

    from ._types.search_handlers import SearchHandlerCondition
    from .query import Query

__all__ = (
    "AllCondition",
    "AnyCondition",
    "KeywordCondition",
    "PlainTextCondition",
    "RegexCondition",
)


class PlainTextCondition:
    r"""A builtin search condition to check plain text.

    This condition will only run if the query's text is the same as the text given to this condition.
    See the :ref:`search handler section <search_handlers>` for more information about using search handlers and conditions.

    Attributes
    ----------
    text: :class:`str`
        The text to compare the query to
    """

    __slots__ = ("text",)

    def __init__(self, text: str) -> None:
        self.text = text

    def __call__(self, query: Query) -> bool:
        return query.text == self.text


class RegexCondition:
    r"""A builtin search condition to check a regex pattern.

    This condition will only run if the query's text is a match to the regex pattern given to this condition.
    See the :ref:`search handler section <search_handlers>` for more information about using search handlers and conditions.

    This condition will set the query's :attr:`~flogin.query.Query.condition_data` attribute to the :class:`re.Match` object.

    Attributes
    ----------
    pattern: :class:`re.Pattern`
        The pattern to check the queries against.
    """

    __slots__ = ("pattern",)

    def __init__(self, pattern: re.Pattern[str]) -> None:
        self.pattern = pattern

    def __call__(self, query: Query[re.Match[str]]) -> bool:
        match = self.pattern.match(query.text)
        if match:
            query.condition_data = match
            return True
        return False


class _MultiCondition:
    __slots__ = ("conditions",)

    def __init__(self, *conditions: SearchHandlerCondition) -> None:
        self.conditions = conditions

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.conditions=}"


class AllCondition(_MultiCondition):
    r"""This builtin search condition acts similiarly to the builtin ``all`` function. It only returns ``True`` if all of the given conditions also return ``True``.

    This condition will set :attr:`flogin.query.Query.condition_data` to a dictionary containing the conditions, where the keys are the conditions, and the values are the condition data that they gave.

    Attributes
    ----------
    conditions: list[:ref:`condition <condition_example>`]
        A list that contains all the conditions that should be used with this condition.
    """

    def __call__(self, query: Query) -> bool:
        condition_data = {}
        for condition in self.conditions:
            if condition(query) is False:
                return False
            condition_data[condition] = query.condition_data
            query.condition_data = None

        query.condition_data = condition_data
        return True


class AnyCondition(_MultiCondition):
    r"""This builtin search condition acts similiarly to the builtin ``any`` function. It only returns ``True`` if any one of the given conditions return ``True``.

    This condition will set :attr:`flogin.query.Query.condition_data` to a tuple containing two values. The first value will be the condition that returned true, and the second will be the condition data that the condition gave. ::

        (condition, query.condition_data)

    Attributes
    -----------
    conditions: list[:ref:`condition <condition_example>`]
        A list that contains all the conditions that should be used with this condition.
    """

    def __call__(self, query: Query) -> bool:
        for condition in self.conditions:
            if condition(query) is True:
                query.condition_data = (condition, query.condition_data)
                return True
        return False


class KeywordCondition:
    r"""A builtin search condition to check what keyword was used with the query.

    If the :attr:`~flogin.conditions.KeywordCondition.allowed_keywords` attribute is given, the handler will only run if the query's keyword is in the list of allowed keywords.
    If the :attr:`~flogin.conditions.KeywordCondition.disallowed_keywords` attribute is given, the handler will only run if the query's keyword is not in the list of allowed keywords.

    See the :ref:`search handler section <search_handlers>` for more information about using search handlers and conditions.

    Attributes
    ----------
    allowed_keywords: Optional[Iterable[:class:`str`]]
        The allowed keywords
    disallowed_keywords: Optional[Iterable[:class:`str`]]
        The disallowed keywords
    """

    __slots__ = "allowed_keywords", "disallowed_keywords"

    def __init__(
        self,
        *,
        allowed_keywords: Iterable[str] | None = None,
        disallowed_keywords: Iterable[str] | None = None,
    ) -> None:
        if allowed_keywords is None and disallowed_keywords is None:
            raise TypeError(
                "Either the 'allowed_keywords' arg or the 'disallowed_keywords' arg must be given"
            )
        if allowed_keywords is not None and disallowed_keywords is not None:
            raise TypeError(
                "'allowed_keywords' and 'disallowed_keywords' can not be passed together. Use `MultiCondition` if you would like to achieve it."
            )

        self.allowed_keywords: Iterable[str] | None = allowed_keywords or None
        self.disallowed_keywords: Iterable[str] | None = disallowed_keywords or None

    def __call__(self, query: Query) -> bool:
        if self.allowed_keywords is None and self.disallowed_keywords is not None:
            return query.keyword not in self.disallowed_keywords
        if self.allowed_keywords is not None and self.disallowed_keywords is None:
            return query.keyword in self.allowed_keywords

        raise RuntimeError(
            "'allowed_keywords' and 'disallowed_keywords' have been modified to be invalid"
        )
