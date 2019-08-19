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


@dataclasses.dataclass
class Message:
    __slots__ = ['commit', 'message']

    commit: Commit
    message: str


@dataclasses.dataclass(frozen=True)
class MessageTokenIndices:
    __slots__ = ['commit', 'messagetokenindices']

    commit: Commit
    messagetokenindices: List[int]


@dataclasses.dataclass(frozen=True)
class MessageTokens:
    __slots__ = ['tokens', 'messagetokenindices']

    tokens: List[str]
    messagetokenindices: List[MessageTokenIndices]


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
