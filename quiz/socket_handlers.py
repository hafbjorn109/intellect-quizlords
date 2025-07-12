from flask_socketio import join_room, emit
from quiz import socketio

@socketio.on('join')
def handle_join(data):
    room = data.get('room')
    username = data.get('username')

    if room and username:
        join_room(room)

        emit('player_joined', {
            'room': room,
            'username': username,
        }, to=room)

@socketio.on('player_ready_changed')
def handle_ready_changed(data):
    room = data.get('room')
    player_id = data.get('player_id')
    is_ready = data.get('is_ready')

    if room and player_id is not None:
        emit('player_ready_updated', {
            'player_id': player_id,
            'is_ready': is_ready,
        }, to=room)