import dataclasses


@dataclasses.dataclass(frozen=True)
class Position:
    __slots__ = ['line', 'column']

    line: int
    column: int


@dataclasses.dataclass(frozen=True)
class Span:
    __slots__ = ['begin', 'end']

    begin: Position
    end: Position


@dataclasses.dataclass(frozen=True)
class Comment:
    __slots__ = ['type', 'span']

    type: int
    span: Span


@dataclasses.dataclass(frozen=True)
class Function:
    __slots__ = ['signature', 'span']

    signature: str
    span: Span
