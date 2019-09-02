from marshmallow import Schema, fields, post_load

from .understand import EntitySchema
from ..models import Nesting


class NestingSchema(Schema):
    entity = fields.Nested(EntitySchema)
    nesting = fields.Integer()

    @post_load
    def make_nesting(self, data, **kwargs):
        return Nesting(**data)
