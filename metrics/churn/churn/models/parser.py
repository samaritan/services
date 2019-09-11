import dataclasses

from typing import Tuple


@dataclasses.dataclass(frozen=True)
class Function:
    __slots__ = ['name', 'lines']

    name: str
    lines: Tuple[int, int]
