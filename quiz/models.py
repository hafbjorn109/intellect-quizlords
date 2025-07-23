import string, random
from db import db

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    questions = db.relationship('Question', back_populates='category')

    def __repr__(self):
        return f'<Category "{self.name}">'


class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    category = db.relationship(Category, back_populates="questions")
    answers = db.relationship('Answer', back_populates='question', cascade="all, delete")

    def __repr__(self):
        return f'<Question "{self.text}">'


class Answer(db.Model):
    __tablename__ = 'answers'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, default=False, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    question = db.relationship(Question, back_populates="answers")

    def __repr__(self):
        return f'<Answer {self.text } (correct={self.is_correct})>'


class AnswerGiven(db.Model):
    __tablename__ = 'answers_given'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    round_id = db.Column(db.Integer, db.ForeignKey('rounds.id'), nullable=False)
    answer_id = db.Column(db.Integer, db.ForeignKey('answers.id'), nullable=False)

    is_correct = db.Column(db.Boolean, nullable=False)

    player = db.relationship('Player')
    round = db.relationship('Round')
    answer = db.relationship('Answer')


class GameSession(db.Model):
    __tablename__ = 'game_sessions'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, unique=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    chooser_id = db.Column(
        db.Integer,
        db.ForeignKey('players.id', use_alter=True, name='fk_chooser_id', ondelete='SET NULL'),
        nullable=True
    )
    players = db.relationship(
        'Player',
        back_populates='session',
        cascade="all, delete",
        foreign_keys='Player.session_id'
    )
    chooser = db.relationship('Player', foreign_keys=[chooser_id])
    rounds = db.relationship('Round', back_populates='session', cascade="all, delete")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.code:
            self.code = self.generate_unique_code()

    @staticmethod
    def generate_unique_code():
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not GameSession.query.filter_by(code=code).first():
                return code


class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    is_ready = db.Column(db.Boolean, default=False, nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('game_sessions.id'), nullable=False)
    session = db.relationship(
        'GameSession',
        back_populates='players',
        foreign_keys=[session_id]
    )
    score = db.Column(db.Integer, default=0)
    is_connected = db.Column(db.Boolean, default=True)


class Round(db.Model):
    __tablename__ = 'rounds'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('game_sessions.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    current = db.Column(db.Boolean, default=False, nullable=False)
    chooser_id = db.Column(
        db.Integer,
        db.ForeignKey('players.id', use_alter=True, name='fk_round_chooser_id', ondelete='SET NULL'),
        nullable=True
    )

    session = db.relationship('GameSession', back_populates='rounds')
    question = db.relationship('Question')
