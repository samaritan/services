import dataclasses

from .repository import Commit


@dataclasses.dataclass(frozen=True)
class PastChanges:
    __slots__ = ['commit', 'path', 'pastchanges']

    commit: Commit
    path: str
    pastchanges: int
