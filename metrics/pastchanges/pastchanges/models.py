__all__ = ['Change', 'Changes', 'Commit', 'Developer', 'PastChanges']

import dataclasses

from typing import List


@dataclasses.dataclass(frozen=True)
class Developer:
    __slots__ = ['name', 'email']

    name: str
    email: str


@dataclasses.dataclass(frozen=True)
class Commit:
    __slots__ = ['sha', 'timestamp', 'author']

    sha: str
    timestamp: int
    author: Developer


@dataclasses.dataclass(frozen=True)
class Change:
    __slots__ = ['path', 'insertions', 'deletions']

    path: str
    insertions: int
    deletions: int


@dataclasses.dataclass
class Changes:
    __slots__ = ['commit', 'changes']

    commit: Commit
    changes: List[Change]


@dataclasses.dataclass(frozen=True)
class PastChanges:
    __slots__ = ['commit', 'path', 'pastchanges']

    commit: Commit
    path: str
    pastchanges: int
