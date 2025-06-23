import code

from flask import Blueprint, jsonify, request
from quiz.models import db, GameSession, Player
from quiz.schemas.sessions import GameSessionSchema, PlayerSchema

bp = Blueprint('sessions', __name__, url_prefix='/sessions')

session_schema = GameSessionSchema()
player_schema = PlayerSchema()
players_schema = PlayerSchema(many=True)


@bp.route('/', methods=['POST'])
def create_session():
    """Create a new session (returns session code)"""
    session = GameSession()
    db.session.add(session)
    db.session.commit()
    return jsonify(session_schema.dump(session)), 201


@bp.route('/<string:code>/join', methods=['POST'])
def join_session(code):
    """
    Join an existing session by code.
    Required JSON with 'name' field.
    """
    session = GameSession.query.filter_by(code=code).first_or_404()
    data = request.get_json()

    errors = player_schema.validate(data)
    if errors:
        return jsonify({'error': errors}), 400

    player = Player(name=data['name'], session_id=session.id)
    db.session.add(player)
    db.session.commit()
    return jsonify(player_schema.dump(player)), 201


@bp.route('/<string:code>/players', methods=['GET'])
def get_players(code):
    """Return all players in a session"""
    session = GameSession.query.filter_by(code=code).first_or_404()
    return jsonify(players_schema.dump(session.players)), 200


@bp.route('/<string:code>/players/<int:player_id>/ready', methods=['PUT'])
def set_ready(player_id):
    """
    Set a player's readiness within a session.

    - Validates that the session with the given code exists.
    - Validates that the player belongs to that session.
    """
    session = GameSession.query.filter_by(code=code).first_or_404()
    player = Player.query.get_or_404(player_id)

    if player.session_id != session.id:
        return jsonify({'error': 'Player does not belong to the session'}), 403

    data = request.get_json()
    errors = player_schema.validate(data, partial=True)
    if errors:
        return jsonify({'error': errors}), 400

    if 'is_ready' in data:
        player.is_ready = data['is_ready']
        
    db.session.commit()
    return jsonify(player_schema.dump(player)), 200
