import dataclasses

from typing import List

__all__ = ['Developer']

@dataclasses.dataclass(frozen=True)
class Developer:
    __slots__ = ['name', 'email']

    name: str
    email: str
