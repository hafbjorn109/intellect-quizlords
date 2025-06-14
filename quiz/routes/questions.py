from email import errors

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


@bp.route('/', methods=['GET'])
def get_questions():
    """
    Get a list of all questions.
    Returns a list of questions.
    """
    questions = Question.query.all()
    return jsonify(questions_schema.dump(questions)), 200


@bp.route('/<int:question_id>', methods=['GET'])
def get_question(question_id):
    """
    Get a single question by its ID.
    Returns the question object or 404 if not found.
    """
    question = Question.query.get_or_404(question_id)
    return jsonify(question_schema.dump(question)), 200


@bp.route('/<int:question_id>', methods=['PUT'])
def update_question(question_id):
    """
    Update data of an existing question.
    Expects JSON with a 'text' and 'category_id' field.
    Returns the updated question or an error if validation fails.
    """
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.get_json()
    errors = question_schema.validate(data, partial=True)
    if errors:
        return jsonify({'error': errors}), 400

    question = Question.query.get_or_404(question_id)

    question.text = data.get('text', question.text)
    question.category_id = data.get('category_id', question.category_id)

    db.session.commit()
    return jsonify(question_schema.dump(question)), 200


@bp.route('/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    """
    Delete a category by its ID.
    Returns a confirmation message or 404 if not found.
    """
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    return jsonify({'message': 'Question deleted'}), 200
