import dataclasses

from .repository import Commit


@dataclasses.dataclass(frozen=True)
class Hunk:
    __slots__ = ['commit', 'hunk']

    commit: Commit
    hunk: int
