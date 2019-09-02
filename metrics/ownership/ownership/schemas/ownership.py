from marshmallow import Schema, fields, post_load

from .repository import DeveloperSchema
from ..models import Ownership


class OwnershipSchema(Schema):
    developer = fields.Nested(DeveloperSchema)
    ownership = fields.Float()

    @post_load
    def make_ownership(self, data, **kwargs):
        return Ownership(**data)
