import dataclasses

from .repository import Commit


@dataclasses.dataclass(frozen=True)
class InteractiveChurn:
    __slots__ = ['commit', 'path', 'interactivechurn']

    commit: Commit
    path: str
    interactivechurn: float
