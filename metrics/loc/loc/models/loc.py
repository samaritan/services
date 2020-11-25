import dataclasses


@dataclasses.dataclass(frozen=True)
class Loc:
    __slots__ = ['blank', 'comment', 'source']

    blank: int
    comment: int
    source: int
