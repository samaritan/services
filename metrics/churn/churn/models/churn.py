import dataclasses

from .repository import Commit


@dataclasses.dataclass(frozen=True)
class LineChurn:
    __slots__ = ['insertions', 'deletions']

    insertions: int
    deletions: int


@dataclasses.dataclass(frozen=True)
class Churn:
    __slots__ = ['commit', 'path', 'line']

    commit: Commit
    path: str
    line: LineChurn
