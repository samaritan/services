from marshmallow import Schema, fields, post_load

from .repository import CommitSchema
from ..models import Churn, LineChurn


class LineChurnSchema(Schema):
    insertions = fields.Integer()
    deletions = fields.Integer()

    @post_load
    def make_linechurn(self, data, **kwargs):
        return LineChurn(**data)


class ChurnSchema(Schema):
    commit = fields.Nested(CommitSchema)
    path = fields.String()
    line = fields.Nested(LineChurnSchema)

    @post_load
    def make_churn(self, data, **kwargs):
        return Churn(**data)
