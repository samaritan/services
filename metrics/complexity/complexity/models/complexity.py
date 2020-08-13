import dataclasses


@dataclasses.dataclass(frozen=True)
class Complexity:
    __slots__ = ['function', 'path', 'complexity']

    function: str
    path: str
    complexity: int
