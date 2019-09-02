from marshmallow import Schema, fields, post_load

from .models import Offender


class OffenderSchema(Schema):
    path = fields.String()
    cve = fields.String()

    @post_load
    def make_offender(self, data, **kwargs):
        return Offender(**data)
