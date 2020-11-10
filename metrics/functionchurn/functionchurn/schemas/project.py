from marshmallow import Schema, fields, post_load

from ..models import Project


class ProjectSchema(Schema):
    id = fields.Integer()
    owner = fields.String()
    name = fields.String()
    language = fields.String()
    repository_url = fields.String()

    @post_load
    def make_project(self, data, **kwargs):
        return Project(**data)
