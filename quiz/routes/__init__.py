from .categories import bp as categories_bp
from .questions import bp as questions_bp
from .answers import bp as answers_bp
from .sessions import bp as sessions_bp
from .rounds import bp as rounds_bp
from .views import bp as views_bp


def register_routes(app):
    """
    Register all blueprint routes for the application.

    Currently includes:
    - /categories
    - /questions
    - /answers
    - /sessions
    - /sessions/<string:code>/rounds
    """
    app.register_blueprint(categories_bp)
    app.register_blueprint(questions_bp)
    app.register_blueprint(answers_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(rounds_bp)
    app.register_blueprint(views_bp)