from marshmallow import Schema, fields


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