from flask import Blueprint, render_template, abort
from quiz.decorators import admin_required
from quiz.models import GameSession

bp = Blueprint('views', __name__)

@bp.route('/')
def index():
    """Renders the index page. Contains create session or join existing one. """
    return render_template('index.html')

@bp.route('/game/<string:code>')
def game_view(code):
    """Renders main game view. Requires code of existing session."""
    session = GameSession.query.filter_by(code=code).first()
    if session is None:
        abort(404)
    return render_template('game.html', code=code)

@bp.route('/admin')
def admin_view():
    """
    Renders Admin Panel. Contains adding/editing categories and questions,
    allows to flush inactive sessions.
    """
    return render_template('admin.html')

@bp.route('/admin-login')
def admin_login_view():
    """Renders login page for admin panel."""
    return render_template('admin_login.html')