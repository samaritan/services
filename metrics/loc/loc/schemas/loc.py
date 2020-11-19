from marshmallow import Schema, fields, post_load

from ..models import Loc


class LocSchema(Schema):
    bloc = fields.Integer()
    cloc = fields.Integer()
    sloc = fields.Integer()

    @post_load
    def make_loc(self, data, **kwargs):
        return Loc(**data)
