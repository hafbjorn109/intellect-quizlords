from flask_socketio import join_room, leave_room, emit
from quiz import socketio

@socketio.on('join')
def handle_join(data):
    room = data.get('room')
    username = data.get('username')
    if room and username:
        join_room(room)
        emit('status', {
            'msg': f'{username} has joined room {room}.'
        }, to=room)