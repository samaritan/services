from marshmallow import Schema, fields, post_load

from .repository import CommitSchema
from ..models import Keyword


class KeywordSchema(Schema):
    commit = fields.Nested(CommitSchema)
    keyword = fields.Dict(keys=fields.Str(), values=fields.Integer())

    @post_load
    def make_keyword(self, data, **kwargs):
        return Keyword(**data)
