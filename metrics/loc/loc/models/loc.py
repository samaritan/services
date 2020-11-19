import dataclasses


@dataclasses.dataclass(frozen=True)
class Loc:
    __slots__ = ['bloc', 'cloc', 'sloc']

    bloc: int
    cloc: int
    sloc: int
