import dataclasses

from typing import List

from .repository import Commit


@dataclasses.dataclass(frozen=True)
class PatchTokens:
    __slots__ = ['commit', 'tokens']

    commit: Commit
    tokens: List[str]
