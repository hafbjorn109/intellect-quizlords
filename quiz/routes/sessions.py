from flask import Blueprint, jsonify, request, current_app
from quiz.models import db, GameSession, Player
from quiz.schemas.sessions import GameSessionSchema, PlayerSchema, ScoreboardPlayerSchema
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from quiz import socketio

bp = Blueprint('sessions', __name__, url_prefix='/sessions')

session_schema = GameSessionSchema()
sessions_schema = GameSessionSchema(many=True)
player_schema = PlayerSchema()
players_schema = PlayerSchema(many=True)
scoreboard_schema = ScoreboardPlayerSchema(many=True)

@bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    player_id = int(get_jwt_identity())
    return jsonify({'message': f'Hello, Player {player_id}'}), 200


@bp.route('/', methods=['POST'])
def create_session():
    """Create a new session (returns session code)"""
    session = GameSession()
    db.session.add(session)
    db.session.commit()
    return jsonify(session_schema.dump(session)), 201


@bp.route('/', methods=['GET'])
def get_sessions():
    """Gets a list of all sessions."""
    sessions = GameSession.query.all()
    return jsonify(sessions_schema.dump(sessions)), 200


@bp.route('/<string:code>', methods=['GET'])
def get_session(code):
    """Gets a session based on code."""
    session = GameSession.query.filter_by(code=code).first()
    if session is None:
        return jsonify({'error': f'Session {code} not found'}), 404

    return jsonify(session_schema.dump(session)), 200


@bp.route('/<string:code>/join', methods=['POST'])
def join_session(code):
    """
    Join an existing session by code.
    Required JSON with 'name' field.
    """

    session = GameSession.query.filter_by(code=code).first_or_404()
    if not session.is_active:
        return jsonify({'error': 'Session is no longer active'}), 403

    data = request.get_json()

    errors = player_schema.validate(data)
    if errors:
        return jsonify({'error': errors}), 400

    player = Player(name=data['name'], session_id=session.id)
    db.session.add(player)
    db.session.commit()

    access_token = create_access_token(identity=str(player.id))

    try:
        socketio.emit('player_joined', {
            'id': player.id,
            'name': player.name,
        }, to=code)
    except Exception as e:
        current_app.logger.warning(f'Emit failed for session {code}: {e}')


    return jsonify({
        'player': player_schema.dump(player),
        'access_token': access_token
    }), 201


@bp.route('/<string:code>/players', methods=['GET'])
def get_players(code):
    """Return all players in a session"""
    session = GameSession.query.filter_by(code=code).first_or_404()
    return jsonify(players_schema.dump(session.players)), 200


@bp.route('/<string:code>/players/<int:player_id>/ready', methods=['PUT'])
def set_ready(code, player_id):
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


@bp.route('/<string:code>/scoreboard', methods=['GET'])
def get_scoreboard(code):
    """
    Return a scoreboard of all players in the session,
    sorted by score descending.
    """
    session = GameSession.query.filter_by(code=code).first_or_404()
    players = Player.query.filter_by(session_id=session.id).order_by(Player.score.desc()).all()

    return jsonify(scoreboard_schema.dump(players)), 200


@bp.route('/end', methods=['POST'])
def end_session(code):
    """
    End the game session (marks session as inactive).
    """
    session = GameSession.query.filter_by(code=code).first_or_404()

    session.is_active = False
    db.session.commit()

    return jsonify({'message': 'Session ended'}), 200
