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

class GameSession(db.Model):
    __tablename__ = 'game_sessions'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), nullable=False, unique=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    players = db.relationship('Player', back_populates='session', cascade="all, delete")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.code:
            self.code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    is_ready = db.Column(db.Boolean, default=False, nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('game_sessions.id'), nullable=False)
    session = db.relationship(GameSession, back_populates='players')