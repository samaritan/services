import dataclasses


@dataclasses.dataclass(frozen=True)
class FunctionChurn:
    __slots__ = ['insertions', 'deletions', 'modifications']

    insertions: int
    deletions: int
    modifications: int
