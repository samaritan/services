import dataclasses


@dataclasses.dataclass(frozen=True)
class RelativeChurn:
    __slots__ = ['insertions', 'deletions']

    insertions: float
    deletions: float
