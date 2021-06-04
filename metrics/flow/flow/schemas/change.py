from marshmallow import Schema, fields, post_load
from ..models import Oids, Change

class OidsSchema(Schema):
    before = fields.String()
    after = fields.String()

    @post_load
    def make_oids(self, data, **kwargs):
        return Oids(**data)


class ChangeSchema(Schema):
    path = fields.String()
    type = fields.Integer()
    oids = fields.Nested(OidsSchema)

    @post_load
    def make_change(self, data, **kwargs):
        return Change(**data)