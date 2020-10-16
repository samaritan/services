from marshmallow import Schema, fields, post_load

from .repository import CommitSchema
from ..models import PatchTokens


class PatchTokensSchema(Schema):
    commit = fields.Nested(CommitSchema)
    tokens = fields.List(fields.String())

    @post_load
    def make_patchtokens(self, data, **kwargs):
        return PatchTokens(**data)
