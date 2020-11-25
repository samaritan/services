import dataclasses


@dataclasses.dataclass(frozen=True)
class Churn:
    __slots__ = ['insertions', 'deletions', 'aggregate']

    insertions: int
    deletions: int
    aggregate: int
