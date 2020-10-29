import dataclasses

from typing import Tuple


@dataclasses.dataclass(frozen=True)
class Comment:
    __slots__ = ['type', 'lines']

    type: int
    lines: Tuple[int, int]


@dataclasses.dataclass(frozen=True)
class Function:
    __slots__ = ['name', 'lines']

    name: str
    lines: Tuple[int, int]
