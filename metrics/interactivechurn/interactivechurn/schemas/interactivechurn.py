from marshmallow import Schema, fields, post_load

from .repository import CommitSchema
from ..models import InteractiveChurn


class InteractiveChurnSchema(Schema):
    commit = fields.Nested(CommitSchema)
    path = fields.String()
    interactivechurn = fields.Float(allow_none=True)

    @post_load
    def make_interactivechurn(self, data, **kwargs):
        return InteractiveChurn(**data)
