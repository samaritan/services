from marshmallow import Schema, fields, post_load

from ..models import Change, Commit, Delta, Developer, File, LastModifier,    \
                     LineChanges, Module, Move, Moves, Oids

class OidsSchema(Schema):
    before = fields.String()
    after = fields.String()

    @post_load
    def make_oids(self, data, **kwargs):
        return Oids(**data)


class ChangeSchema(Schema):
    path = fields.String()
    type = fields.Integer()
    oids = fields.Nested(OidsSchema)

    @post_load
    def make_change(self, data, **kwargs):
        return Change(**data)


class DeltaSchema(Schema):
    insertions = fields.Integer(allow_none=True)
    deletions = fields.Integer(allow_none=True)

    @post_load
    def make_delta(self, data, **kwargs):
        return Delta(**data)


class DeveloperSchema(Schema):
    name = fields.String()
    email = fields.String()

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


class LastModifierSchema(Schema):
    line = fields.Integer()
    commit = fields.Nested(CommitSchema)

    @post_load
    def make_lastmodifier(self, data, **kwargs):
        return LastModifier(**data)


class LineChangesSchema(Schema):
    linechanges = fields.Dict(
        fields.String(),
        fields.Dict(
            fields.String(),
            fields.List(fields.Tuple((fields.Integer(), fields.Integer())))
        )
    )

    @post_load
    def make_linechanges(self, data, **kwargs):
        return LineChanges(**data)


class ModuleSchema(Schema):
    path = fields.String()

    @post_load
    def make_module(self, data, **kwargs):
        return Module(**data)


class MoveSchema(Schema):
    source = fields.String()
    destination = fields.String()

    @post_load
    def make_move(self, data, **kwargs):
        return Move(**data)


class MovesSchema(Schema):
    commit = fields.Nested(CommitSchema)
    moves = fields.Nested(MoveSchema, many=True)

    @post_load
    def make_moves(self, data, **kwargs):
        return Moves(**data)


class FileSchema(Schema):
    path = fields.String()
    is_active = fields.Boolean()
    module = fields.Nested(ModuleSchema)

    @post_load
    def make_file(self, data, **kwargs):
        return File(**data)
