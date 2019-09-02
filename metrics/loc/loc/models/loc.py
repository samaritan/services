import dataclasses

from .understand import Entity


@dataclasses.dataclass(frozen=True)
class Loc:
    __slots__ = ['entity', 'bloc', 'cloc', 'sloc']

    entity: Entity
    bloc: int
    cloc: int
    sloc: int
