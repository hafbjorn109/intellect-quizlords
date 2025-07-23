from flask_socketio import join_room, emit, leave_room, disconnect
from flask import request
from quiz import socketio
from .models import GameSession, Player
import random
from quiz.models import db

connected_players = {}

@socketio.on('join')
def handle_join(data):
    room = data.get('room')
    username = data.get('username')
    player_id = data.get('player_id')

    if room and username and player_id:
        join_room(room)

        player = Player.query.get(player_id)
        if player:
            player.is_connected = True
            db.session.commit()

        connected_players[request.sid] = player_id

        emit('player_joined', {
            'room': room,
            'username': username,
        }, to=room)


@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    print(f"[disconnect] SID {sid} disconnected.")  # ✅ DEBUG

    player_id = connected_players.pop(sid, None)
    print(f"[disconnect] Resolved player_id: {player_id}")  # ✅ DEBUG

    if player_id:
        player = Player.query.get(player_id)
        if player:
            session = GameSession.query.get(player.session_id)
            if session:
                leave_room(session.code)
                emit("player_left", {
                    "player_id": player.id,
                    "name": player.name
                }, to=session.code)

            player.is_connected = False
            db.session.commit()


@socketio.on('leave')
def handle_leave(data):
    sid = request.sid
    print(f"[leave] SID: {sid} requested leave")  # ✅ DEBUG

    player_id = data.get("player_id")
    print(f"[leave] Leaving player_id: {player_id}")  # ✅ DEBUG

    if not player_id:
        return

    connected_players.pop(sid, None)
    print(f"[leave] connected_players after pop: {connected_players}")  # ✅ DEBUG

    player = Player.query.get(player_id)
    if player:
        session = GameSession.query.get(player.session_id)
        if session:
            leave_room(session.code)
            emit("player_left", {
                "player_id": player.id,
                "name": player.name
            }, to=session.code)

        player.is_connected = False
        db.session.commit()


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

        session = GameSession.query.filter_by(code=room).first()
        if session:
            players = Player.query.filter_by(session_id=session.id, is_connected=True).all()
            all_ready = all(p.is_ready for p in players)

            if all_ready:
                chooser = random.choice(players)
                session.chooser_id = chooser.id
                db.session.commit()

                emit('game_started', {
                    'chooser': {
                        'id': chooser.id,
                        'name': chooser.name,
                    },
                    'round_number': 1
                }, to=room)
