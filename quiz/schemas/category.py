from marshmallow import Schema, fields, validate

class CategorySchema(Schema):
    # Marshmallow schema for serializing and validating Category objects.
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))