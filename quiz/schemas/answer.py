from marshmallow import Schema, fields, validate
from quiz.schemas.question import QuestionSchema

class AnswerSchema(Schema):
    # Marshmallow schema for serializing and validating Answer objects.
    id = fields.Int(dump_only=True)
    text = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    is_correct = fields.Bool(required=True)
    question_id = fields.Int(required=True)
    question = fields.Nested(QuestionSchema(only=('id', 'text')), dump_only=True)