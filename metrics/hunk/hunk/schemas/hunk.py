from marshmallow import Schema, fields, post_load

from .repository import CommitSchema
from ..models import Hunk


class HunkSchema(Schema):
    commit = fields.Nested(CommitSchema)
    hunk = fields.Integer()

    @post_load
    def make_hunk(self, data, **kwargs):
        return Hunk(**data)
