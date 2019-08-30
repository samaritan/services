from marshmallow import Schema, fields, post_load

from .models import Entity, Metrics


class EntitySchema(Schema):
    uid = fields.Integer()
    type = fields.String()
    name = fields.String()
    path = fields.String(missing=None)

    @post_load
    def make_entity(self, data, **kwargs):
        return Entity(**data)


class MetricsSchema(Schema):
    entity = fields.Nested(EntitySchema)
    metrics = fields.Dict(values=fields.Raw(), keys=fields.String())

    @post_load
    def make_metrics(self, data, **kwargs):
        return Metrics(**data)


class NestingSchema(Schema):
    entity = fields.Nested(EntitySchema)
    nesting = fields.Integer()
