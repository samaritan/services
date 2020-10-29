from marshmallow import Schema, fields, post_load

from .models import Comment, Function


class CommentSchema(Schema):
    type = fields.Integer()
    lines = fields.Tuple((fields.Integer(), fields.Integer()))

    @post_load
    def make_comment(self, data, **kwargs):
        return Comment(**data)


class FunctionSchema(Schema):
    name = fields.String()
    lines = fields.Tuple((fields.Integer(), fields.Integer()))

    @post_load
    def make_function(self, data, **kwargs):
        return Function(**data)
