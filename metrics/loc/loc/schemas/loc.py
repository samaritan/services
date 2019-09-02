from marshmallow import Schema, fields, post_load

from .understand import EntitySchema
from ..models import Loc


class LocSchema(Schema):
    entity = fields.Nested(EntitySchema)
    bloc = fields.Integer()
    cloc = fields.Integer()
    sloc = fields.Integer()

    @post_load
    def make_loc(self, data, **kwargs):
        return Loc(**data)
