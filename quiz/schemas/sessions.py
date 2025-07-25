from marshmallow import Schema, fields, validates, ValidationError
from .questions import QuestionSchema


class PlayerSchema(Schema):
    # Marshmallow schema for serializing and validating Player objects.
    # Checks if name is not empty.
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    is_ready = fields.Bool(load_default=False)
    session_id = fields.Int(dump_only=True)
    score = fields.Int(dump_only=True)
    is_connected = fields.Bool(load_default=True)

    @validates('name')
    def validate_name(self, value, **kwargs):
        if not value.strip():
            raise ValidationError('Name cannot be empty')


class ScoreboardPlayerSchema(Schema):
    # Marshmallow schema for serializing and validating Scoreboard.
    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)
    score = fields.Int(dump_only=True)


class GameSessionSchema(Schema):
    # Marshmallow schema for serializing and validating Game Session objects.
    id = fields.Int(dump_only=True)
    code = fields.Str(dump_only=True)
    is_active = fields.Bool(required=True)
    players = fields.Nested(PlayerSchema, many=True, dump_only=True)
    chooser_id = fields.Int(dump_only=True)
    chooser = fields.Nested(PlayerSchema(only=('id', 'name')), dump_only=True)


class RoundSchema(Schema):
    # Marshmallow schema for serializing and validating Round objects.
    id = fields.Int(dump_only=True)
    session_id = fields.Int(required=True)
    question_id = fields.Int(dump_only=True)
    current = fields.Bool(dump_only=True)
    question = fields.Nested(QuestionSchema, dump_only=True)


class ChooserSchema(Schema):
    # Marshmallow schema for serializing and validating Chooser.
    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)
