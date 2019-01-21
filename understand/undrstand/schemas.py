from marshmallow import Schema, fields, post_load

from .models import Project


class EntitySchema(Schema):
    uid = fields.Integer()
    type = fields.String()
    name = fields.String()
    path = fields.String()


class MetricsSchema(Schema):
    entity = fields.Nested(EntitySchema)
    metrics = fields.Dict(values=fields.Raw(), keys=fields.String())


class ProjectSchema(Schema):
    name = fields.String()
    description = fields.String()
    domain = fields.String()
    language = fields.String()
    project_url = fields.String()
    repository_url = fields.String()

    @post_load
    def make_project(self, data):
        return Project(**data)
