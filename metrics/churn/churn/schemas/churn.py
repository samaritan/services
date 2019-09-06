from marshmallow import Schema, fields, post_load

from .repository import CommitSchema
from ..models import Churn, FunctionChurn, LineChurn


class BaseChurnSchema(Schema):
    insertions = fields.Integer()
    deletions = fields.Integer()


class FunctionChurnSchema(BaseChurnSchema):
    @post_load
    def make_functionchurn(self, data, **kwargs):
        return FunctionChurn(**data)


class LineChurnSchema(BaseChurnSchema):
    @post_load
    def make_linechurn(self, data, **kwargs):
        return LineChurn(**data)


class ChurnSchema(Schema):
    commit = fields.Nested(CommitSchema)
    path = fields.String()
    line = fields.Nested(LineChurnSchema)
    function = fields.Nested(FunctionChurnSchema, allow_none=True)

    @post_load
    def make_churn(self, data, **kwargs):
        return Churn(**data)
