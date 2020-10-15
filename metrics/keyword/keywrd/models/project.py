import dataclasses


@dataclasses.dataclass(frozen=True)
class Project:
    __slots__ = [
        'id', 'name', 'description', 'domain', 'language', 'project_url',
        'repository_url'
    ]

    id: int
    name: str
    description: str
    domain: str
    language: str
    project_url: str
    repository_url: str
