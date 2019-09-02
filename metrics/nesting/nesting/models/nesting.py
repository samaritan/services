import dataclasses

from .understand import Entity


@dataclasses.dataclass(frozen=True)
class Nesting:
    __slots__ = ['entity', 'nesting']

    entity: Entity
    nesting: int
