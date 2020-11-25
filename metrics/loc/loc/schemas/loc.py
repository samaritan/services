from marshmallow import Schema, fields, post_load

from ..models import Loc


class LocSchema(Schema):
    blank = fields.Integer()
    comment = fields.Integer()
    source = fields.Integer()

    @post_load
    def make_loc(self, data, **kwargs):
        return Loc(**data)
