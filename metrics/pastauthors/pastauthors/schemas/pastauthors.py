from marshmallow import Schema, fields, post_load

from .repository import CommitSchema
from ..models import PastAuthors


class PastAuthorsSchema(Schema):
    commit = fields.Nested(CommitSchema)
    path = fields.String()
    pastauthors = fields.Integer()

    @post_load
    def make_pastauthors(self, data, **kwargs):
        return PastAuthors(**data)
