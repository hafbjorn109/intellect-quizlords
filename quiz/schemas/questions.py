from marshmallow import Schema, fields, validate


class CategorySchema(Schema):
    # Marshmallow schema for serializing and validating Category objects.
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))


class QuestionSchema(Schema):
    # Marshmallow schema for serializing and validating Question objects.
    id = fields.Int(dump_only=True)
    text = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    category_id = fields.Int(required=True)
    category = fields.Nested(CategorySchema(only=('id', 'name')), dump_only=True)
    answers = fields.List(fields.Nested(lambda: AnswerSchema()), dump_only=True)


class AnswerSchema(Schema):
    # Marshmallow schema for serializing and validating Answer objects.
    id = fields.Int(dump_only=True)
    text = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    is_correct = fields.Bool(required=True)
    question_id = fields.Int(required=True)
    question = fields.Nested(lambda: QuestionSchema(only=('id', 'text')), dump_only=True)


class AnswerGivenSchema(Schema):
    # Marshmallow schema for serializing and validating AnswerGiven objects.
    id = fields.Int(dump_only=True)
    player_id = fields.Int(required=True)
    round_id = fields.Int(required=True)
    answer_id = fields.Int(required=True)
    is_correct = fields.Bool(dump_only=True)
