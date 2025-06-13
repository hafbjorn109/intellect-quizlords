from flask import Blueprint, jsonify, request
from quiz.models import db, Question
from quiz.schemas.questions import QuestionSchema

bp = Blueprint('questions', __name__, url_prefix='/questions')

question_schema = QuestionSchema()
questions_schema = QuestionSchema(many=True)

@bp.route('/', methods=['POST'])
def create_question():
    """
    Create a new question.
    Expects JSON with a 'text' field.
    Returns the created question or an error if validation fails.
    """
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.get_json()

    errors = question_schema.validate(data)
    if errors:
        return jsonify({'error': errors}), 400

    question = Question(text=data['text'], category_id=data['category_id'])
    db.session.add(question)
    db.session.commit()

    return jsonify(question_schema.dump(question)), 201


@bp.route('/<int:question_id>', methods=['GET'])
def get_question(question_id):
    """
    Get a single question by its ID.
    Returns the question object or 404 if not found.
    """
    question = Question.query.get_or_404(question_id)
    return jsonify(question_schema.dump(question)), 200