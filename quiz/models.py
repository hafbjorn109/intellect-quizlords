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
