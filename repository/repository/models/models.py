import dataclasses

from typing import List

__all__ = [
    'Change', 'Changes', 'Commit', 'Developer', 'File', 'Module', 'Project'
]

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
class Changes:
    __slots__ = ['commit', 'changes']

    commit: Commit
    changes: List[Change]


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


@dataclasses.dataclass(frozen=True)
class Project:
    __slots__ = [
        'name', 'description', 'domain', 'language', 'project_url',
        'repository_url'
    ]

    name: str
    description: str
    domain: str
    language: str
    project_url: str
    repository_url: str
