from marshmallow import Schema, fields, post_load

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
    name = fields.String()
    span = fields.Nested(SpanSchema)

    @post_load
    def make_function(self, data, **kwargs):
        return Function(**data)
