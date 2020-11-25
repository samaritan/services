import dataclasses


@dataclasses.dataclass(frozen=True)
class RelativeChurn:
    __slots__ = ['insertions', 'deletions', 'aggregate']

    insertions: float
    deletions: float
    aggregate: float
