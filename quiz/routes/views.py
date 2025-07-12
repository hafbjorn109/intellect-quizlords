from flask import Blueprint, render_template, abort

from quiz.models import GameSession

bp = Blueprint('views', __name__)

@bp.route('/game/<string:code>')
def game_view(code):
    session = GameSession.query.filter_by(code=code).first()
    if session is None:
        abort(404)
    return render_template('game.html', code=code)