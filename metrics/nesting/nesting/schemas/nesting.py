from marshmallow import Schema, fields, post_load

from ..models import Nesting


class NestingSchema(Schema):
    function = fields.String()
    path = fields.String()
    nesting = fields.Integer()

    @post_load
    def make_nesting(self, data, **kwargs):
        return Nesting(**data)
