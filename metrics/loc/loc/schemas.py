from marshmallow import Schema, fields


class LocSchema(Schema):
    path = fields.String()
    bloc = fields.Integer()
    cloc = fields.Integer()
    sloc = fields.Integer()
