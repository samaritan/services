from marshmallow import Schema, fields, post_load

from .repository import CommitSchema
from ..models import Churn


class ChurnSchema(Schema):
    commit = fields.Nested(CommitSchema)
    path = fields.String()
    insertions = fields.Integer(allow_none=True)
    deletions = fields.Integer(allow_none=True)

    @post_load
    def make_churn(self, data, **kwargs):
        return Churn(**data)
