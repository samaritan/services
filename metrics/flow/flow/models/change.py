import dataclasses

@dataclasses.dataclass(frozen=True)
class Oids:
    __slots__ = ['before', 'after']

    before: str
    after: str


@dataclasses.dataclass(frozen=True)
class Change:
    __slots__ = ['path', 'type', 'oids']

    path: str
    type: int
    oids: Oids