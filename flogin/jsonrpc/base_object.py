import json
from typing import Any, ClassVar, Generic, Self, TypeVar, cast

T = TypeVar("T")

__all__ = ("Base",)


class Base(Generic[T]):
    __slots__ = ()
    __jsonrpc_option_names__: ClassVar[dict[str, str]] = {}

    def to_dict(self) -> T:
        names = self.__jsonrpc_option_names__ or {}
        foo = {}
        for name in self.__slots__:
            item: Any = getattr(self, name)
            if isinstance(item, Base):
                item = item.to_dict()
            elif item and isinstance(item, list) and isinstance(item[0], Base):
                item = [child.to_dict() for child in cast("list[Base[Any]]", item)]
            foo[names.get(name, name)] = item

        return cast("T", foo)

    @classmethod
    def from_dict(cls: type[Self], data: T) -> Self:
        raise NotImplementedError

    def __repr__(self) -> str:
        args = [f"{item}={getattr(self, item)!r}" for item in self.__slots__]
        return f"<{self.__class__.__name__} {' '.join(args)}>"


class ToMessageBase(Base[T], Generic[T]):
    def to_message(self, id: int) -> bytes:
        return (json.dumps(self.to_dict()) + "\r\n").encode()
