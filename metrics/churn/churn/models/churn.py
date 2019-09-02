import dataclasses

from .repository import Commit


@dataclasses.dataclass(frozen=True)
class Churn:
    __slots__ = ['commit', 'path', 'insertions', 'deletions']

    commit: Commit
    path: str
    insertions: int
    deletions: int
