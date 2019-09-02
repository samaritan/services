import dataclasses

from typing import List

from .repository import Commit


@dataclasses.dataclass(frozen=True)
class MessageTokenIndices:
    __slots__ = ['commit', 'messagetokenindices']

    commit: Commit
    messagetokenindices: List[int]


@dataclasses.dataclass(frozen=True)
class MessageTokens:
    __slots__ = ['tokens', 'messagetokenindices']

    tokens: List[str]
    messagetokenindices: List[MessageTokenIndices]
