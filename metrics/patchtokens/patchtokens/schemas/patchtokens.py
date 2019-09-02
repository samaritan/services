from marshmallow import Schema, fields, post_load

from .repository import CommitSchema
from ..models import PatchTokenIndices, PatchTokens


class PatchTokenIndicesSchema(Schema):
    commit = fields.Nested(CommitSchema)
    patchtokenindices = fields.List(fields.Integer())

    @post_load
    def make_patchtokenindices(self, data, **kwargs):
        return PatchTokenIndices(**data)


class PatchTokensSchema(Schema):
    tokens = fields.List(fields.String())
    patchtokenindices = fields.Nested(PatchTokenIndicesSchema, many=True)

    @post_load
    def make_patchtokens(self, data, **kwargs):
        return PatchTokens(**data)
