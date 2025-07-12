from flask import Blueprint, jsonify, request, current_app
from quiz.models import db, Round, GameSession, Question, Player, Answer, AnswerGiven
from quiz.schemas.sessions import RoundSchema, ChooserSchema
from quiz.schemas.questions import AnswerGivenSchema, CategoryPickSchema, QuestionSchema
import random
from quiz import socketio

bp = Blueprint('rounds', __name__, url_prefix='/sessions/<string:code>/rounds')

round_schema = RoundSchema()
answer_given_schema = AnswerGivenSchema()
category_pick_schema = CategoryPickSchema()
chooser_schema = ChooserSchema()
question_schema = QuestionSchema()

MAX_ROUNDS = 10

@bp.route('/setup', methods=['POST'])
def setup_round(code):
    """
    Gets category picked by a player. Creates a new round with random question from that category.
    """
    session = GameSession.query.filter_by(code=code).first_or_404()
    if not session.is_active:
        return jsonify({'error': 'Session is no longer active'}), 403

    existing_rounds = Round.query.filter_by(session_id=session.id).count()
    if existing_rounds >= MAX_ROUNDS:
        session.is_active = False
        db.session.commit()

        return jsonify({'message': 'Game over', 'game_over': True}), 200

    data = request.get_json()
    errors = category_pick_schema.validate(data)
    if errors:
        return jsonify({'error': errors}), 400

    category_id = data['category_id']

    # Deactivate current round
    Round.query.filter_by(session_id=session.id, current=True).update({'current': False})

    # Get all previously used question IDs in this session
    used_question_ids = db.session.query(Round.question_id).filter_by(session_id=session.id).all()

    # Converts tuple into list of pure ids
    used_ids = [q[0] for q in used_question_ids]

    # Try to get a question from the given category that hasn't been used
    question = (
        Question.query
        .filter(Question.category_id == category_id, ~Question.id.in_(used_ids))
        .order_by(db.func.random())
        .first()
    )

    if not question:
        return jsonify({'error': 'No questions found for this category'}), 400

    round = Round(
        session_id=session.id,
        question_id=question.id,
        chooser_id=session.chooser_id,
        current=True
    )
    db.session.add(round)
    db.session.commit()

    try:
        socketio.emit('round_started', {
            'question': question_schema.dump(question),
            'round_number': existing_rounds + 1
        }, to=code)
    except Exception as e:
        current_app.logger.warning(f'[Setup Round] Emit failed for session {code}: {e}')

    return jsonify(round_schema.dump(round)), 201


@bp.route('/next-chooser', methods=['POST'])
def next_chooser(code):
    """
    Select the next player in turn to become the chooser for the next round.
    """
    session = GameSession.query.filter_by(code=code).first_or_404()
    if not session.is_active:
        return jsonify({'error': 'Session is no longer active'}), 403

    players = Player.query.filter_by(session_id=session.id).order_by(Player.id).all()

    try:
        current_index = next(i for i, p in enumerate(players) if p.id == session.chooser_id)
    except StopIteration:
        return jsonify({'error': 'Current chooser not found in session players'}), 400

    next_index = (current_index + 1) % len(players)
    next_player = players[next_index]

    session.chooser_id = next_player.id
    db.session.commit()

    return jsonify({'chooser': chooser_schema.dump(next_player)}), 200


@bp.route('/current', methods=['GET'])
def get_current_round(code):
    """
    Get the currently active round in a session.

    - Returns the round marked as 'current' for the given session.
    """
    session = GameSession.query.filter_by(code=code).first_or_404()
    current_round = Round.query.filter_by(session_id=session.id, current=True).first_or_404()

    if not current_round:
        return jsonify({'error': 'No active round found'}), 404

    return jsonify(round_schema.dump(current_round)), 200


@bp.route('/answer', methods=['POST'])
def given_answer(code):
    """
    Submit an answer for a round by a player.

    - Validates session and round.
    - Checks that the player hasn't answered already.
    - Verifies that the answer matches the question for this round.
    - Updates the player's score if the answer is correct.
    - Saves the answer.
    """
    session = GameSession.query.filter_by(code=code).first_or_404()
    if not session.is_active:
        return jsonify({'error': 'Session is no longer active'}), 403

    data = request.get_json()
    errors = answer_given_schema.validate(data)
    if errors:
        return jsonify({'error': errors}), 400

    round_id = data['round_id']
    round = Round.query.filter_by(session_id=session.id, id=round_id).first_or_404()

    player = Player.query.get_or_404(data['player_id'])
    if player.session_id != session.id:
        return jsonify({'error': 'Player does not belong to this session'}), 403

    existing = AnswerGiven.query.filter_by(player_id=player.id, round_id=round.id).first()
    if existing:
        return jsonify({'error': 'Player has already answered this round'}), 400

    answer = Answer.query.get_or_404(data['answer_id'])
    if answer.question.id != round.question_id:
        return jsonify({'error': 'Answer does not belong to the current round question'}), 400

    is_correct = answer.is_correct

    if is_correct:
        player.score += 1

    given = AnswerGiven(
        player_id=player.id,
        round_id=round.id,
        answer_id=answer.id,
        is_correct=is_correct,
    )

    db.session.add(given)
    db.session.commit()

    return jsonify(answer_given_schema.dump(given)), 201

