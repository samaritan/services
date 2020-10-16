import dataclasses

from typing import List

from .repository import Commit


@dataclasses.dataclass(frozen=True)
class MessageTokens:
    __slots__ = ['commit', 'tokens']

    commit: Commit
    tokens: List[str]
