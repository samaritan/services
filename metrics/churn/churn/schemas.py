from marshmallow import Schema, fields, post_load

from .models import Commit, Change, Changes, Developer


class ChangeSchema(Schema):
    path = fields.String()
    insertions = fields.Integer(missing=None)
    deletions = fields.Integer(missing=None)

    @post_load
    def make_change(self, data, **kwargs):
        return Change(**data)


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


class ChangesSchema(Schema):
    commit = fields.Nested(CommitSchema)
    changes = fields.Nested(ChangeSchema, many=True)

    @post_load
    def make_changes(self, data, **kwargs):
        return Changes(**data)


class ChurnSchema(Schema):
    commit = fields.Nested(CommitSchema)
    path = fields.String()
    insertions = fields.Integer()
    deletions = fields.Integer()
