from marshmallow import Schema, fields, post_load, EXCLUDE

from .models import Comment, Function, Position, Span


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

class FunctionSchema(Schema):
    signature = fields.String()
    span = fields.Nested(SpanSchema)

    class Meta:
        unknown = EXCLUDE

    param_count = fields.Integer(
        default = 0,
        allow_none = True
    )

    calls = fields.List(
        fields.String(),
        default = [],
        allow_none=True
    )

    functions_called_by = fields.List(
        fields.String(),
        default = [],
        allow_none=True
    )

    acyclical_paths_tree = fields.List(
        fields.Dict(),
        allow_none=True
    )

    has_return = fields.Boolean(
        default = False,
        allow_none=True
    )

    parent_structure_name = fields.String(allow_none=True)
    parent_structure_type = fields.String(allow_none=True)
    file_name = fields.String(allow_none=True)

    global_variable_writes = fields.Dict(
        keys = fields.String(),
        values = fields.Dict(
            keys = fields.String(),
            values = fields.List(
                fields.String,
                default = [],
                allow_none = True
            )
        ),
        allow_none = True
    )

    global_variable_reads = fields.List(
        fields.String(),
        allow_none=True
    )


    @post_load
    def make_function(self, data, **kwargs):
        return Function(**data)
