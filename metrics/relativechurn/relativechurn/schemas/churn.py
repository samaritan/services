from marshmallow import Schema, fields, post_load

from ..models import Churn


class ChurnSchema(Schema):
    insertions = fields.Integer(allow_none=True)
    deletions = fields.Integer(allow_none=True)

    @post_load
    def make_churn(self, data, **kwargs):
        return Churn(**data)
