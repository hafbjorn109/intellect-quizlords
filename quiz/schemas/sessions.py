from marshmallow import Schema, fields
from .questions import QuestionSchema


class PlayerSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    is_ready = fields.Bool(required=True)
    session_id = fields.Int(dump_only=True)
    score = fields.Int(dump_only=True)


class ScoreboardPlayerSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)
    score = fields.Int(dump_only=True)


class GameSessionSchema(Schema):
    id = fields.Int(dump_only=True)
    code = fields.Str(dump_only=True)
    is_active = fields.Bool(required=True)
    players = fields.Nested(PlayerSchema, many=True, dump_only=True)
    chooser_id = fields.Int(dump_only=True)
    chooser = fields.Nested(PlayerSchema(only=('id', 'name')), dump_only=True)


class RoundSchema(Schema):
    id = fields.Int(dump_only=True)
    session_id = fields.Int(required=True)
    question_id = fields.Int(dump_only=True)
    current = fields.Bool(dump_only=True)
    question = fields.Nested(QuestionSchema, dump_only=True)


class ChooserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)