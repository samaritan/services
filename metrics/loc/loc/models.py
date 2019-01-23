import dataclasses

from typing import Dict


@dataclasses.dataclass(frozen=True)
class Entity:
    __slots__ = ['uid', 'type', 'name', 'path']

    uid: int
    type: str
    name: str
    path: str


@dataclasses.dataclass(frozen=True)
class Metrics:
    __slots__ = ['entity', 'metrics']

    entity: Entity
    metrics: Dict[str, object]


@dataclasses.dataclass(frozen=True)
class Loc:
    __slots__ = ['entity', 'bloc', 'cloc', 'sloc']

    entity: Entity
    bloc: int
    cloc: int
    sloc: int
