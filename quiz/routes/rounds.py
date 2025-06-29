from flask import Blueprint, jsonify, request
from quiz.models import db, Round, GameSession, Question, Player, Answer, AnswerGiven
from quiz.schemas.sessions import RoundSchema
from quiz.schemas.questions import AnswerGivenSchema

bp = Blueprint('rounds', __name__, url_prefix='/sessions/<string:code>/rounds')

round_schema = RoundSchema()
answer_given_schema = AnswerGivenSchema()

@bp.route('/start', methods=['POST'])
def start_round(code):
    session = GameSession.query.filter_by(code=code).first_or_404()

    #Deactivate current round if any
    Round.query.filter_by(session_id=session.id, current=True).update({'current': False})

    question = Question.query.order_by(db.func.random()).first()
    if not question:
        return jsonify({'error': 'No questions found'}), 400

    new_round = Round(session_id=session.id, question_id=question.id, current=True)
    db.session.add(new_round)
    db.session.commit()

    return jsonify(round_schema.dump(new_round)), 201


@bp.route('/current', methods=['GET'])
def get_current_round(code):
    session = GameSession.query.filter_by(code=code).first_or_404()
    current_round = Round.query.filter_by(session_id=session.id, current=True).first()

    if not current_round:
        return jsonify({'error': 'No active round found'}), 404

    return jsonify(round_schema.dump(current_round)), 200


@bp.route('/<int:round_id>/answer', methods=['POST'])
def given_answer(code, round_id):
    session = GameSession.query.filter_by(code=code).first_or_404()
    round = Round.query.filter_by(session_id=session.id, id=round_id).first_or_404()

    data = request.get_json()
    errors = answer_given_schema.validate(data)
    if errors:
        return jsonify({'error': errors}), 400

    player = Player.query.get_or_404(data['player_id'])
    if player.session_id != session.id:
        return jsonify({'error': 'Player does not belong to this session'}), 403

    answer = Answer.query.get_or_404(data['answer_id'])
    if answer.question.id != round.question_id:
        return jsonify({'error': 'Answer does not belong to the current round question'}), 400

    is_correct = answer.is_correct

    given = AnswerGiven(
        player_id=player.id,
        round_id=round.id,
        answer_id=answer.id,
        is_correct=is_correct,
    )

    db.session.add(given)
    db.session.commit()

    return jsonify(answer_given_schema.dump(given)), 201
