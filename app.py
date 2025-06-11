from flask import Flask
from config import Config
from flask_socketio import SocketIO
from db import db, migrate
from quiz import models

socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)

    with app.app_context():
        from quiz import models

    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=app.config["DEBUG"])