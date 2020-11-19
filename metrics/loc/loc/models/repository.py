import dataclasses

from typing import Dict, List


@dataclasses.dataclass(frozen=True)
class Delta:
    __slots__ = ['insertions', 'deletions']

    insertions: int
    deletions: int


@dataclasses.dataclass(frozen=True)
class Developer:
    __slots__ = ['name', 'email']

    name: str
    email: str


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


@dataclasses.dataclass(frozen=True)
class Commit:
    __slots__ = ['sha', 'timestamp', 'author']

    sha: str
    timestamp: int
    author: Developer


@dataclasses.dataclass(frozen=True)
class LastModifier:
    __slots__ = ['line', 'commit']

    line: int
    commit: Commit


@dataclasses.dataclass
class LineChanges:
    __slots__ = ['linechanges']

    linechanges: Dict[str, Dict[str, List]]


@dataclasses.dataclass(frozen=True)
class Module:
    __slots__ = ['path']

    path: str


@dataclasses.dataclass(frozen=True)
class Move:
    __slots__ = ['source', 'destination']

    source: str
    destination: str


@dataclasses.dataclass(frozen=True)
class Moves:
    __slots__ = ['commit', 'moves']

    commit: Commit
    moves: List[Move]


@dataclasses.dataclass(frozen=True)
class File:
    __slots__ = ['path', 'module', 'is_active']

    path: str
    is_active: bool
    module: Module
