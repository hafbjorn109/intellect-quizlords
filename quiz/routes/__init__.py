from .categories import bp as categories_bp

def register_routes(app):
    """
    Register all blueprint routes for the application.

    Currently includes:
    - /categories
    """
    app.register_blueprint(categories_bp)