from marshmallow import Schema, fields, post_load

from .repository import CommitSchema
from ..models import MessageTokens


class MessageTokensSchema(Schema):
    commit = fields.Nested(CommitSchema)
    tokens = fields.List(fields.String())

    @post_load
    def make_messagetokens(self, data, **kwargs):
        return MessageTokens(**data)
