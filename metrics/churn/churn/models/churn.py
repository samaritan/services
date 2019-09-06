import dataclasses

from .repository import Commit


@dataclasses.dataclass(frozen=True)
class BaseChurn:
    __slots__ = ['insertions', 'deletions']

    insertions: int
    deletions: int


class FunctionChurn(BaseChurn):
    pass


class LineChurn(BaseChurn):
    pass


@dataclasses.dataclass(frozen=True)
class Churn:
    __slots__ = ['commit', 'path', 'line', 'function']

    commit: Commit
    path: str
    line: LineChurn
    function: FunctionChurn
