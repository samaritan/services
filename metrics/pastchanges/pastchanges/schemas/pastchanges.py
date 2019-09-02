from marshmallow import Schema, fields, post_load

from .repository import CommitSchema
from ..models import PastChanges


class PastChangesSchema(Schema):
    commit = fields.Nested(CommitSchema)
    path = fields.String()
    pastchanges = fields.Integer()

    @post_load
    def make_pastchanges(self, data, **kwargs):
        return PastChanges(**data)
