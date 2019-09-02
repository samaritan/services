import dataclasses

from typing import Dict

from .repository import Commit

@dataclasses.dataclass(frozen=True)
class Keyword:
    __slots__ = ['commit', 'keyword']

    commit: Commit
    keyword: Dict[str, int]
