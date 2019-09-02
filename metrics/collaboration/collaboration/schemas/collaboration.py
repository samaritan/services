from marshmallow import Schema, fields, post_load

from ..models import Collaboration


class CollaborationSchema(Schema):
    path = fields.String()
    collaboration = fields.Float()

    @post_load
    def make_collaboration(self, data, **kwargs):
        return Collaboration(**data)
