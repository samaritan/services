from marshmallow import Schema, fields, post_load

from .understand import EntitySchema
from ..models import Complexity


class ComplexitySchema(Schema):
    entity = fields.Nested(EntitySchema)
    complexity = fields.Integer()

    @post_load
    def make_complexity(self, data, **kwargs):
        return Complexity(**data)
