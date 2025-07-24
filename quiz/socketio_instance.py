from flask_socketio import SocketIO

"""
This module defines a single, reusable instance of the SocketIO object.

Having a separate file for the `socketio` instance allows for clean separation of concerns.
- It prevents circular imports between application modules (especially when socket events are in separate files).
- It ensures the same `SocketIO` object is used across the entire application (e.g., for initialization, event handling, and running the app).

The instance is imported and initialized in `__init__.py` alongside the Flask app.
"""

socketio = SocketIO(cors_allowed_origins="*")