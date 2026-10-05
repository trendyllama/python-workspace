from typing import Any, Protocol


class Ordered(Protocol):
    def __lt__(self, other: Any, /) -> bool: ...
