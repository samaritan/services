from marshmallow import Schema, fields, post_load

from ..models import Entity, Metrics


class EntitySchema(Schema):
    uid = fields.Integer()
    type = fields.String()
    name = fields.String()
    path = fields.String(allow_none=True)

    @post_load
    def make_entity(self, data, **kwwargs):
        return Entity(**data)


class MetricsSchema(Schema):
    entity = fields.Nested(EntitySchema)
    metrics = fields.Dict(fields.String(), fields.Raw(allow_none=True))

    @post_load
    def make_metrics(self, data, **kwwargs):
        return Metrics(**data)
