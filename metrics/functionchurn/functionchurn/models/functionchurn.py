import dataclasses


@dataclasses.dataclass(frozen=True)
class FunctionChurn:
    __slots__ = ['insertions', 'deletions', 'modifications', 'aggregate']

    insertions: int
    deletions: int
    modifications: int
    aggregate: int
