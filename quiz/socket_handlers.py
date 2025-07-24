from flask_socketio import join_room, emit, leave_room, disconnect
from flask import request
from quiz import socketio
from .models import GameSession, Player
import random
from quiz.models import db

connected_players = {}

@socketio.on('join')
def handle_join(data):
    """
    Handle a player joining a game session.

    - Joins the player to the specified room.
    - Marks the player as connected in the database.
    - Adds the player's socket ID to the connected_players dictionary.
    - Broadcasts a 'player_joined' event to other players in the room.
    """
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
    """
    Handle unexpected disconnection of a player (e.g., closing tab or losing connection).

    - Removes the socket ID from the connected_players dictionary.
    - Marks the player as disconnected in the database.
    - If no players remain connected to the session, marks the session as inactive.
    - Broadcasts a 'player_left' event to remaining players in the room.
    """
    sid = request.sid
    player_id = connected_players.pop(sid, None)

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
            print(f'is connected? {player.is_connected}')
            db.session.commit()

            remaining_connected = Player.query.filter_by(
                session_id=player.session_id,
                is_connected=True
            ).count()

            if remaining_connected == 0:
                session.is_active = False
                db.session.commit()


@socketio.on('leave')
def handle_leave(data):
    """
    Handle a player intentionally leaving a game session.

    - Removes the socket ID from the connected_players dictionary.
    - Marks the player as disconnected in the database.
    - If no players remain connected to the session, marks the session as inactive.
    - Broadcasts a 'player_left' event to remaining players in the room.
    """
    sid = request.sid
    player_id = data.get("player_id")

    if not player_id:
        return

    connected_players.pop(sid, None)
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

        remaining_connected = Player.query.filter_by(
            session_id=player.session_id,
            is_connected=True
        ).count()

        if remaining_connected == 0:
            session.is_active = False
            db.session.commit()


@socketio.on('player_ready_changed')
def handle_ready_changed(data):
    """
    Handle changes to a player's readiness state.

    - Broadcasts the updated readiness status to the room.
    - If all connected players are ready, picks a random chooser and starts the game.
    - Emits a 'game_started' event with the chooser info and initial round number.
    """
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
