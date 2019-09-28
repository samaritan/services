import dataclasses

from .repository import Commit


@dataclasses.dataclass(frozen=True)
class FunctionChurn:
    __slots__ = ['commit', 'path', 'insertions', 'deletions', 'modifications']

    commit: Commit
    path: str
    insertions: int
    deletions: int
    modifications: int
