from flask import Flask
from config import Config
from flask_socketio import SocketIO

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    socketio.init_app(app, cors_allowed_origins="*")

    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=app.config["DEBUG"])