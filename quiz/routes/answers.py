from flask import Blueprint, jsonify, request
from quiz.models import db, Answer
from quiz.schemas.questions import AnswerSchema

bp = Blueprint('answers', __name__, url_prefix='/answers')

answer_schema = AnswerSchema()
answers_schema = AnswerSchema(many=True)

@bp.route('/', methods=['POST'])
def create_answer():
    """
    Create a new answer.
    Expects JSON with a 'text', 'question_id' and ' is_correct fields.
    Returns the created answer or an error if validation fails.
    """
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.get_json()

    errors = answer_schema.validate(data)
    if errors:
        return jsonify({'error': errors}), 400

    answer = Answer(text=data['text'], question_id=data['question_id'], is_correct=data['is_correct'])
    db.session.add(answer)
    db.session.commit()

    return jsonify(answer_schema.dump(answer))


@bp.route('/<int:answer_id>', methods=['GET'])
def get_answer(answer_id):
    """
    Get a single answer by its ID.
    Returns the answer object or 404 if not found.
    """
    answer = Answer.query.get_or_404(answer_id)
    return jsonify(answer_schema.dump(answer)), 200