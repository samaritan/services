from marshmallow import Schema, fields, post_load

from .models import Offender


class OffenderSchema(Schema):
    timestamp = fields.Integer()
    path = fields.String()
    aliases = fields.List(fields.String(), allow_none=True)
    reference = fields.String()

    @post_load
    def make_offender(self, data, **kwargs):
        return Offender(**data)
