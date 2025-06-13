from marshmallow import Schema, validate, fields
from quiz.schemas.category import CategorySchema
from quiz.schemas.answer import AnswerSchema


class QuestionSchema(Schema):
    # Marshmallow schema for serializing and validating Question objects.
    id = fields.Int(dump_only=True)
    text = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    category_id = fields.Int(required=True)
    category = fields.Nested(CategorySchema(only=('id', 'name')), dump_only=True)
    answers = fields.List(fields.Nested(AnswerSchema), dump_only=True)