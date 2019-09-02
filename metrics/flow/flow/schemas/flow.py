from marshmallow import Schema, fields, post_load

from .understand import EntitySchema
from ..models import Flow


class FlowSchema(Schema):
    entity = fields.Nested(EntitySchema)
    ninput = fields.Integer()
    noutput = fields.Integer()
    npath = fields.Integer()

    @post_load
    def make_flow(self, data, **kwargs):
        return Flow(**data)
