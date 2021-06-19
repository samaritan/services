from marshmallow import Schema, fields, post_load
from marshmallow.utils import INCLUDE

from .models import Comment, Function, FunctionProperties, \
     Position, Span, AcyclicalPath

class PositionSchema(Schema):
    line = fields.Integer()
    column = fields.Integer(allow_none=True)

    @post_load
    def make_position(self, data, **kwargs):
        return Position(**data)


class SpanSchema(Schema):
    begin = fields.Nested(PositionSchema)
    end = fields.Nested(PositionSchema)

    @post_load
    def make_span(self, data, **kwargs):
        return Span(**data)


class CommentSchema(Schema):
    type = fields.Integer()
    span = fields.Nested(SpanSchema)

    @post_load
    def make_comment(self, data, **kwargs):
        return Comment(**data)

class AcyclicalPathSchema(Schema):
    type = fields.String()
    if_type = fields.String(allow_none=True)
    children = fields.List(
        fields.Nested(
            lambda: AcyclicalPathSchema()
        )
    )

    @post_load
    def make_acyclical_path(self, data, **kwargs):
        return AcyclicalPath(**data)

class GlobalVariableWrite(Schema):
    expressions = fields.List(fields.String)
    members_modified = fields.List(fields.String)
    indices_modified = fields.List(fields.String)

    @post_load
    def make_global_variable_write(self, data, **kwargs):
        return GlobalVariableWrite(**data)

class FunctionSchema(Schema):
    signature = fields.String()
    span = fields.Nested(SpanSchema)

    @post_load
    def make_function(self, data, **kwargs):
        return Function(**data)

class FunctionPropertiesSchema(FunctionSchema):
    class Meta:
        unknown = INCLUDE

    calls = fields.List(
        fields.String(),
        default = [],
        allow_none=True
    )

    callers = fields.List(
        fields.String(),
        default = [],
        allow_none=True
    )

    acyclical_paths_tree = fields.List(
        fields.Nested(AcyclicalPathSchema),
        allow_none=True
    )

    has_return = fields.Boolean(
        default = False,
        allow_none=True
    )

    parent_structure_name = fields.String(allow_none=True)
    parent_structure_type = fields.String(allow_none=True)

    global_variable_writes = fields.Dict(
        keys = fields.String(),
        values = fields.Nested(GlobalVariableWrite),
        allow_none = True
    )

    global_variable_reads = fields.List(
        fields.String(),
        allow_none=True
    )

    @post_load
    def make_function(self, data, **kwargs):
        return FunctionProperties(**data)
