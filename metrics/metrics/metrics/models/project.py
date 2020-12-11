import dataclasses


@dataclasses.dataclass(frozen=True)
class Project:
    __slots__ = ['id', 'owner', 'repository', 'language', 'repository_url']

    id: int
    owner: str
    repository: str
    language: str
    repository_url: str
