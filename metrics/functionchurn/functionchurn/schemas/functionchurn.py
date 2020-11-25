from marshmallow import Schema, fields, post_load

from ..models import FunctionChurn


class FunctionChurnSchema(Schema):
    insertions = fields.Integer(allow_none=True)
    deletions = fields.Integer(allow_none=True)
    modifications = fields.Integer(allow_none=True)
    aggregate = fields.Integer(allow_none=True)

    @post_load
    def make_functionchurn(self, data, **kwargs):
        return FunctionChurn(**data)
