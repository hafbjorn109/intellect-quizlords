from flask import Flask
from config import Config
from flask_socketio import SocketIO
from db import db, migrate
from . import models
from .routes import register_routes

socketio = SocketIO(cors_allowed_origins="*")

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)

    with app.app_context():
        from quiz import models

    register_routes(app)
    return app