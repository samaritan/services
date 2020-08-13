import dataclasses


@dataclasses.dataclass(frozen=True)
class Nesting:
    __slots__ = ['function', 'path', 'nesting']

    function: str
    path: str
    nesting: int
