from marshmallow import Schema, fields, post_load

from ..models import RelativeChurn


class RelativeChurnSchema(Schema):
    insertions = fields.Float(allow_none=True)
    deletions = fields.Float(allow_none=True)
    aggregate = fields.Float(allow_none=True)

    @post_load
    def make_relativechurn(self, data, **kwargs):
        return RelativeChurn(**data)
