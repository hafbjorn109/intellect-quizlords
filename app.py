from quiz import create_app, socketio

app = create_app()

if __name__ == '__main__':
    # Run the Flask app using Socket.IO server with debug mode from config
    socketio.run(app, debug=app.config["DEBUG"])