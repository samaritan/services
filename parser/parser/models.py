from __future__ import annotations
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

@dataclasses.dataclass(frozen=True)
class GlobalVariableWrite:
    __slots__ = [
        'expressions',
        'members_modified',
        'indices_modified']

    expressions: list(str)
    members_modified: list(str)
    indices_modified: list(str)

@dataclasses.dataclass(frozen=True)
class AcyclicalPath:
    __slots__ = [
        'type',
        'children',
        'if_type'
    ]

    type: str
    children: list(AcyclicalPath)
    if_type: str

    def __init__(
        self,
        type: str,
        children: list(AcyclicalPath),
        if_type: str = None):
        object.__setattr__(self, 'type', type)
        object.__setattr__(self, 'children', children)
        object.__setattr__(self, 'if_type', if_type)

@dataclasses.dataclass(frozen=True)
class FunctionProperties(Function):
    __slots__ = [
        'function_name',
        'calls',
        'callers',
        'acyclical_paths_tree',
        'has_return',
        'parent_structure_name',
        'parent_structure_type',
        'global_variable_writes',
        'global_variable_reads'
    ]

    function_name: str
    calls: list(str)
    callers: list(str)
    acyclical_paths_tree: list(AcyclicalPath)
    has_return: bool
    parent_structure_name: str
    parent_structure_type: str
    global_variable_writes: list(GlobalVariableWrite)
    global_variable_reads: list(str)
