from .base import Base, add_prop

__all__ = ("FuzzySearchResult",)


class FuzzySearchResult(Base):
    r"""A class which represents the result given from flow launcher to a fuzzy search request

    .. NOTE::
        This is not intended to be a class that you create yourself, use :func:`~flogin.flow.api.FlowLauncherAPI.fuzzy_search` instead.

    Attributes
    --------
    score: :class:`int`
        The score of the result
    highlight_data: list[:class:`int`]
        The highlight data included with the result
    search_percision: :class:`int`
        The perision of the result
    """

    score: int = add_prop("score")
    highlight_data: list[int] = add_prop("matchData")
    search_precision: int = add_prop("searchPrecision")
