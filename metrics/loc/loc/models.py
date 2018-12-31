import dataclasses


@dataclasses.dataclass(frozen=True)
class Loc:
    __slots__ = ['path', 'bloc', 'cloc', 'sloc']

    path: str
    bloc: int
    cloc: int
    sloc: int
