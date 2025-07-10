from flask import Blueprint, render_template

bp = Blueprint('test', __name__, url_prefix='/test')

@bp.route('/')
def ws_test():
    return render_template('ws_test.html')
