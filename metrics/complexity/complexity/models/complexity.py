import dataclasses

from .understand import Entity


@dataclasses.dataclass(frozen=True)
class Complexity:
    __slots__ = ['entity', 'complexity']

    entity: Entity
    complexity: int
