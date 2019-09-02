from marshmallow import Schema, fields, post_load

from ..models import Contribution


class ContributionSchema(Schema):
    path = fields.String()
    contribution = fields.Float()

    @post_load
    def make_contribution(self, data, **kwargs):
        return Contribution(**data)
