from marshmallow import Schema, fields, post_load

from .models import Entity, Metrics


class EntitySchema(Schema):
    uid = fields.Integer()
    type = fields.String()
    name = fields.String()
    path = fields.String(missing=None)

    @post_load
    def make_entity(self, data):
        return Entity(**data)


class MetricsSchema(Schema):
    entity = fields.Nested(EntitySchema)
    metrics = fields.Dict(values=fields.Raw(), keys=fields.String())

    @post_load
    def make_metrics(self, data):
        return Metrics(**data)


class FlowSchema(Schema):
    entity = fields.Nested(EntitySchema)
    ninput = fields.Integer()
    noutput = fields.Integer()
    npath = fields.Integer()