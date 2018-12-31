import dataclasses

from typing import List

__all__ = ['Change', 'Changes', 'Commit', 'Contribution', 'Developer']

@dataclasses.dataclass(frozen=True)
class Developer:
    __slots__ = ['name', 'email']

    name: str
    email: str


@dataclasses.dataclass(frozen=True)
class Change:
    __slots__ = ['path', 'insertions', 'deletions']

    path: str
    insertions: int
    deletions: int


@dataclasses.dataclass(frozen=True)
class Commit:
    __slots__ = ['sha', 'timestamp', 'author']

    sha: str
    timestamp: int
    author: Developer


@dataclasses.dataclass
class Contribution:
    __slots__ = ['path', 'contribution']

    path: str
    contribution: float


@dataclasses.dataclass
class Changes:
    __slots__ = ['commit', 'changes']

    commit: Commit
    changes: List[Change]
