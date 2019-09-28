from marshmallow import Schema, fields, post_load

from .repository import CommitSchema
from ..models import FunctionChurn


class FunctionChurnSchema(Schema):
    commit = fields.Nested(CommitSchema)
    path = fields.String()
    insertions = fields.Integer(allow_none=True)
    deletions = fields.Integer(allow_none=True)
    modifications = fields.Integer(allow_none=True)

    @post_load
    def make_functionchurn(self, data, **kwargs):
        return FunctionChurn(**data)
