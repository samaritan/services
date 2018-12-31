import dataclasses

from typing import List

__all__ = ['Change', 'Changes', 'Commit', 'Developer']

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
class Churn:
    __slots__ = ['commit', 'path', 'insertions', 'deletions']

    commit: Commit
    path: str
    insertions: int
    deletions: int
