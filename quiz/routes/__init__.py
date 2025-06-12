from .categories import bp as categories_bp

def register_routes(app):
    app.register_blueprint(categories_bp)