from marshmallow import Schema, fields, post_load

from .repository import CommitSchema
from ..models import MessageTokenIndices, MessageTokens


class MessageTokenIndicesSchema(Schema):
    commit = fields.Nested(CommitSchema)
    messagetokenindices = fields.List(fields.Integer())

    @post_load
    def make_messagetokenindices(self, data, **kwargs):
        return MessageTokenIndices(**data)


class MessageTokensSchema(Schema):
    tokens = fields.List(fields.String())
    messagetokenindices = fields.Nested(MessageTokenIndicesSchema, many=True)

    @post_load
    def make_messagetokens(self, data, **kwargs):
        return MessageTokens(**data)
