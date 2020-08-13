from marshmallow import Schema, fields, post_load

from ..models import Complexity


class ComplexitySchema(Schema):
    function = fields.String()
    path = fields.String()
    complexity = fields.Integer()

    @post_load
    def make_complexity(self, data, **kwargs):
        return Complexity(**data)
