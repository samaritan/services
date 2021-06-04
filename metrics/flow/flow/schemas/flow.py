from marshmallow import Schema, fields, post_load

from .change import ChangeSchema
from ..models import Flow


class FlowSchema(Schema):
    change = fields.Nested(ChangeSchema)
    ninput = fields.Integer()
    noutput = fields.Integer()
    npath = fields.Integer()

    @post_load
    def make_flow(self, data, **kwargs):
        return Flow(**data)
