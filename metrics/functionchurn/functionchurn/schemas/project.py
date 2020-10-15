from marshmallow import Schema, fields, post_load

from ..models import Project

class ProjectSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    description = fields.String()
    domain = fields.String()
    language = fields.String()
    project_url = fields.String()
    repository_url = fields.String()

    @post_load
    def make_project(self, data, **kwargs):
        return Project(**data)
