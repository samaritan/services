from marshmallow import Schema, fields, post_load

from .repository import CommitSchema
from ..models import RelativeChurn


class RelativeChurnSchema(Schema):
    commit = fields.Nested(CommitSchema)
    path = fields.String()
    insertions = fields.Float(allow_none=True)
    deletions = fields.Float(allow_none=True)

    @post_load
    def make_relativechurn(self, data, **kwargs):
        return RelativeChurn(**data)
