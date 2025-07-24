from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
from quiz.decorators import admin_required
from quiz.models import Admin

bp = Blueprint('admin', __name__, url_prefix='/admin/auth')

@bp.route('/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    admin = Admin.query.filter_by(username=data.get('username')).first()

    if not admin or not check_password_hash(admin.password_hash, data.get('password')):
        return jsonify({'error': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=f'admin:{admin.id}', additional_claims={'role': 'admin'})
    return jsonify({'access_token': access_token}), 200


@bp.route('/verify', methods=['GET'])
@admin_required
def verify_admin_token():
    return jsonify({'message': 'Token is valid'}), 200
