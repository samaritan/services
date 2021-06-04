import dataclasses

from .change import Change


@dataclasses.dataclass(frozen=True)
class Flow:
    __slots__ = ['entity', 'ninput', 'noutput', 'npath']

    entity: Change
    ninput: int
    noutput: int
    npath: int
