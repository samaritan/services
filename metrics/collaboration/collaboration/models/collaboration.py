import dataclasses


@dataclasses.dataclass
class Collaboration:
    __slots__ = ['path', 'collaboration']

    path: str
    collaboration: float
