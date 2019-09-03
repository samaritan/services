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
    __slots__ = ['type', 'oids']

    type: int
    oids: Oids


@dataclasses.dataclass(frozen=True)
class Commit:
    __slots__ = ['sha', 'timestamp', 'author']

    sha: str
    timestamp: int
    author: Developer


@dataclasses.dataclass
class Changes:
    __slots__ = ['commit', 'changes']

    commit: Commit
    changes: Dict[str, Change]


@dataclasses.dataclass
class Deltas:
    __slots__ = ['commit', 'deltas']

    commit: Commit
    deltas: Dict[str, Delta]


@dataclasses.dataclass
class Message:
    __slots__ = ['commit', 'message']

    commit: Commit
    message: str


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


@dataclasses.dataclass
class Patch:
    __slots__ = ['commit', 'patch']

    commit: Commit
    patch: str
