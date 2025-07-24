# Quiz Multiplayer App

Real-time multiplayer quiz game built with Flask, Socket.IO, and PostgreSQL. Players join a session via unique code, answer questions in rounds, and compete to win.

## Features

- 🧠 Answer multiple-choice questions in real time
- 🔁 Rotating chooser mechanic per round
- 🔒 JWT-based auth per player
- 📡 WebSocket real-time updates
- 📊 Scoreboard and automatic game-over logic
- 🧪 REST API for categories, questions, answers, sessions
- ⚙️ Admin panel for managing questions and categories

## Tech Stack

- Flask + Flask-SocketIO
- PostgreSQL + SQLAlchemy + Marshmallow
- JWT authentication (`flask-jwt-extended`)
- Frontend in Vanilla JS + HTML templates
- `eventlet` server for async I/O

## Setup & Installation

Clone the repo:

```bash
git clone <repo_url>
cd intellect-quizzlords
```

Set up virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env` file with database and secret config:

```
DEBUG=True
DB_USER=your_user
DB_PASS=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=quiz
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret
```

Run database migrations:

```bash
flask db init
flask db migrate
flask db upgrade
```

Run the app:

```bash
python app.py
```

## Usage

- Open `/` to join or create a session.
- Players enter a name and connect via WebSocket.
- The game proceeds in up to 10 rounds.
- One player (the "chooser") picks a category each round.
- Questions are served randomly from the selected category.
- Players earn 1 point per correct answer.
- After all rounds, scoreboard is displayed.

## WebSocket Events

### `join`

Client emits:

```json
{
  "room": "SESSIONCODE",
  "username": "Alice",
  "player_id": 1
}
```

Server broadcasts:

```json
{
  "room": "SESSIONCODE",
  "username": "Alice"
}
```

---

### `player_ready_changed`

Broadcasts updated readiness:

```json
{
  "player_id": 1,
  "is_ready": true
}
```

---

### `game_started`

Sent when all players are ready:

```json
{
  "chooser": { "id": 1, "name": "Alice" },
  "round_number": 1
}
```

---

### `round_started`

Question and answers payload:

```json
{
  "round_id": 3,
  "question": {
    "text": "...",
    "answers": [...]
  },
  "round_number": 2
}
```

---

### `chooser_turn`

Choosers rotate every round:

```json
{
  "chooser": { "id": 2, "name": "Bob" },
  "scoreboard": [...],
  "round_number": 3
}
```

---

### `game_over`

After 10 rounds:

```json
{
  "scoreboard": [
    { "name": "Alice", "score": 8 },
    { "name": "Bob", "score": 6 }
  ]
}
```

---

## REST API Reference

### Categories

- `GET /categories/`
- `POST /categories/`
- `PUT /categories/<id>`
- `DELETE /categories/<id>`

### Questions

- `GET /questions/`
- `POST /questions/`
- `PUT /questions/<id>`
- `DELETE /questions/<id>`

### Answers

- `GET /answers/`
- `POST /answers/`
- `PUT /answers/<id>`
- `DELETE /answers/<id>`

### Sessions

- `POST /sessions` → Create session
- `POST /sessions/<code>/join` → Join as player
- `GET /sessions/<code>/players` → List players
- `PUT /sessions/<code>/players/<id>/ready` → Toggle readiness
- `POST /sessions/<code>/rounds/setup` → Chooser starts round
- `POST /sessions/<code>/rounds/answer` → Submit answer
- `GET /sessions/<code>/scoreboard` → Scoreboard

## Admin Panel

Visit `/admin` to:

- Add/edit/delete categories
- Add/edit/delete questions + answers
- Delete inactive sessions

## Dev Notes

- WebSockets managed via `flask_socketio`
- Sessions expire after 10 rounds or manual POST `/end`
- Chooser rotates with each round via `next_chooser` logic
- Questions per category are selected randomly, ensuring no repeat
- Full test coverage of schemas, validation and relationships

## License

MIT © 2025 Kamil Giszka
