from marshmallow import Schema, fields


class FunctionSchema(Schema):
    name = fields.String()
    lines = fields.Tuple((fields.Integer(), fields.Integer()))
