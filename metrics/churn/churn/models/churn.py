import dataclasses


@dataclasses.dataclass(frozen=True)
class Churn:
    __slots__ = ['insertions', 'deletions']

    insertions: int
    deletions: int
