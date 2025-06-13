from .categories import bp as categories_bp
from .questions import bp as questions_bp
from. answers import bp as answers_bp

def register_routes(app):
    """
    Register all blueprint routes for the application.

    Currently includes:
    - /categories
    - /questions
    - /answers
    """
    app.register_blueprint(categories_bp)
    app.register_blueprint(questions_bp)
    app.register_blueprint(answers_bp)