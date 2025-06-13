from flask import Blueprint, jsonify, request
from quiz.models import db, Category
from quiz.schemas.category import CategorySchema

bp = Blueprint('categories', __name__, url_prefix='/categories')

category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)

@bp.route('/', methods=['POST'])
def create_category():
    data = request.get_json()

    errors = category_schema.validate(data)
    if errors:
        return jsonify({'errors': errors}), 400

    if Category.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Category with this name already exists.'}), 400

    category = Category(name=data['name'])
    db.session.add(category)
    db.session.commit()

    return jsonify(category_schema.dump(category)), 201


@bp.route('/', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify(categories_schema.dump(categories)), 200


@bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    category = Category.query.get_or_404(category_id)
    return jsonify(category_schema.dump(category)), 200


@bp.route('/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    data = request.get_json()

    errors = category_schema.validate(data)
    if errors:
        return jsonify({'errors': errors}), 400

    category.name = data['name']
    db.session.commit()
    return jsonify(category_schema.dump(category)), 200


@bp.route('/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category deleted'}), 200
