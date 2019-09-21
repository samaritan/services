import dataclasses

from .repository import Commit


@dataclasses.dataclass(frozen=True)
class BaseChurn:
    __slots__ = ['insertions', 'deletions']

    insertions: int
    deletions: int


@dataclasses.dataclass(frozen=True)
class FunctionChurn(BaseChurn):
    __slots__ = ['modifications']

    modifications: int


@dataclasses.dataclass(frozen=True)
class LineChurn(BaseChurn):
    pass


@dataclasses.dataclass(frozen=True)
class Churn:
    __slots__ = ['commit', 'path', 'line', 'function']

    commit: Commit
    path: str
    line: LineChurn
    function: FunctionChurn
