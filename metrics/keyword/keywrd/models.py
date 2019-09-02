import dataclasses

from typing import Dict


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
class Keyword:
    __slots__ = ['commit', 'keyword']

    commit: Commit
    keyword: Dict[str, int]


@dataclasses.dataclass(frozen=True)
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
