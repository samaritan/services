from marshmallow import Schema, fields, post_load

from ..models import Function


class FunctionSchema(Schema):
    name = fields.String()
    lines = fields.Tuple((fields.Integer(), fields.Integer()))

    @post_load
    def make_function(self, data, **kwargs):
        return Function(**data)
