from marshmallow import Schema, fields, post_load

from .models import Developer


class DeveloperSchema(Schema):
    name = fields.String()
    email = fields.String(missing=None)

    @post_load
    def make_developer(self, data):
        return Developer(**data)
