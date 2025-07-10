from flask import Flask
from flask_jwt_extended import JWTManager
from config import Config
from.socketio_instance import socketio
from db import db, migrate
from . import models
from .routes import register_routes


def create_app(config_class=Config):
    """
    Flask application factory.

    Initializes Flask app with configuration, database, migration support,
    Socket.IO, and registers blueprints and models.

    Args:
        config_class: Configuration class for app settings.

    Returns:
        A fully configured Flask app instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)

    jwt = JWTManager(app)

    with app.app_context():
        from quiz import models
        from quiz import socket_handlers

    register_routes(app)
    return app