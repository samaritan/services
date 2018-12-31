import dataclasses


@dataclasses.dataclass(frozen=True)
class Offender:
    __slots__ = ['path', 'cve']

    path: str
    cve: str
