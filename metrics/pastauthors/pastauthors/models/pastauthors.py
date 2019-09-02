import dataclasses

from .repository import Commit


@dataclasses.dataclass(frozen=True)
class PastAuthors:
    __slots__ = ['commit', 'path', 'pastauthors']

    commit: Commit
    path: str
    pastauthors: int
