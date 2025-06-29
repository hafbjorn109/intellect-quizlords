from marshmallow import Schema, fields
from .questions import QuestionSchema


class PlayerSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    is_ready = fields.Bool()
    session_id = fields.Int()


class GameSessionSchema(Schema):
    id = fields.Int(dump_only=True)
    code = fields.Str(dump_only=True)
    is_active = fields.Bool(required=True)
    players = fields.Nested(PlayerSchema, many=True, dump_only=True)


class RoundSchema(Schema):
    id = fields.Int(dump_only=True)
    session_id = fields.Int(required=True)
    question_id = fields.Int(required=True)
    current = fields.Bool()
    question = fields.Nested(QuestionSchema, dump_only=True)