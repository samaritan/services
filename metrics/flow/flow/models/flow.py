import dataclasses

from .understand import Entity


@dataclasses.dataclass(frozen=True)
class Flow:
    __slots__ = ['entity', 'ninput', 'noutput', 'npath']

    entity: Entity
    ninput: int
    noutput: int
    npath: int
