import dataclasses

from .repository import Developer


@dataclasses.dataclass(frozen=True)
class Ownership:
    __slots__ = ['developer', 'ownership']

    developer: Developer
    ownership: float
