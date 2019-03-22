from marshmallow import Schema, fields, post_load

from .models import Commit, Developer, Patch, Project


class DeveloperSchema(Schema):
    name = fields.String()
    email = fields.String(missing=None)

    @post_load
    def make_developer(self, data):
        return Developer(**data)


class CommitSchema(Schema):
    sha = fields.String()
    timestamp = fields.Integer()
    author = fields.Nested(DeveloperSchema)

    @post_load
    def make_commit(self, data):
        return Commit(**data)


class KeywordSchema(Schema):
    commit = fields.Nested(CommitSchema)
    keyword = fields.Dict(keys=fields.Str(), values=fields.Integer())


class PatchSchema(Schema):
    commit = fields.Nested(CommitSchema)
    patch = fields.String()

    @post_load
    def make_patch(self, data):
        return Patch(**data)


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