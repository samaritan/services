from marshmallow import Schema, fields, post_load

from .models import Commit, Developer, Message, Project


class DeveloperSchema(Schema):
    name = fields.String()
    email = fields.String(missing=None)

    @post_load
    def make_developer(self, data, **kwargs):
        return Developer(**data)


class CommitSchema(Schema):
    sha = fields.String()
    timestamp = fields.Integer()
    author = fields.Nested(DeveloperSchema)

    @post_load
    def make_commit(self, data, **kwargs):
        return Commit(**data)


class MessageSchema(Schema):
    commit = fields.Nested(CommitSchema)
    message = fields.String()

    @post_load
    def make_message(self, data, **kwargs):
        return Message(**data)


class MessageTokenIndicesSchema(Schema):
    commit = fields.Nested(CommitSchema)
    messagetokenindices = fields.List(fields.Integer())


class MessageTokensSchema(Schema):
    tokens = fields.List(fields.String())
    messagetokenindices = fields.Nested(MessageTokenIndicesSchema, many=True)


class ProjectSchema(Schema):
    name = fields.String()
    description = fields.String()
    domain = fields.String()
    language = fields.String()
    project_url = fields.String()
    repository_url = fields.String()

    @post_load
    def make_project(self, data, **kwargs):
        return Project(**data)
