import dataclasses


@dataclasses.dataclass(frozen=True)
class Project:
    __slots__ = ['id', 'owner', 'name', 'language', 'repository_url']

    id: int
    owner: str
    name: str
    language: str
    repository_url: str
