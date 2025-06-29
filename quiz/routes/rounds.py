from flask import Blueprint, jsonify
from quiz.models import db, Round, GameSession, Question
from quiz.schemas.sessions import RoundSchema
import random

bp = Blueprint('rounds', __name__, url_prefix='/sessions/<string:code>/rounds')

round_schema = RoundSchema()

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