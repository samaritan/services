import dataclasses

from typing import List

from .repository import Commit


@dataclasses.dataclass(frozen=True)
class PatchTokenIndices:
    __slots__ = ['commit', 'patchtokenindices']

    commit: Commit
    patchtokenindices: List[int]


@dataclasses.dataclass(frozen=True)
class PatchTokens:
    __slots__ = ['tokens', 'patchtokenindices']

    tokens: List[str]
    patchtokenindices: List[PatchTokenIndices]
