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
