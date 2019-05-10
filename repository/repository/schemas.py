from marshmallow import Schema, fields, post_load

from .models import Commit, Project


class ChangeSchema(Schema):
    path = fields.String()
    insertions = fields.Integer()
    deletions = fields.Integer()


class DeveloperSchema(Schema):
    name = fields.String()
    email = fields.String()


class CommitSchema(Schema):
    sha = fields.String()
    timestamp = fields.Integer()
    author = fields.Nested(DeveloperSchema)

    @post_load
    def make_commit(self, data):
        return Commit(**data)


class ChangesSchema(Schema):
    commit = fields.Nested(CommitSchema)
    changes = fields.Nested(ChangeSchema, many=True)


class ModuleSchema(Schema):
    path = fields.String()


class MoveSchema(Schema):
    source = fields.String()
    destination = fields.String()


class MovesSchema(Schema):
    commit = fields.Nested(CommitSchema)
    moves = fields.Nested(MoveSchema, many=True)


class FileSchema(Schema):
    path = fields.String()
    is_active = fields.Boolean()
    module = fields.Nested(ModuleSchema)


class PatchSchema(Schema):
    commit = fields.Nested(CommitSchema)
    patch = fields.String()


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
