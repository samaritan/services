from marshmallow import Schema, fields


class OffenderSchema(Schema):
    path = fields.String()
    cve = fields.String()
