from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TypeAlias

Jsonable: TypeAlias = dict[str, "Jsonable"] | str | int | list["Jsonable"] | None
