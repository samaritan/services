import dataclasses

from typing import List


@dataclasses.dataclass(frozen=True)
class Offender:
    __slots__ = ['timestamp', 'path', 'aliases', 'reference']

    timestamp: int
    path: str
    aliases: List[str]
    reference: str
