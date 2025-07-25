import sys
import os
from quiz import create_app
from quiz.models import db, Admin
from werkzeug.security import generate_password_hash
from decouple import config

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = create_app()

with app.app_context():
    username = config('ADMIN_USERNAME')
    password = config('ADMIN_PASSWORD')
    if not Admin.query.filter_by(username=username).first():
        admin = Admin(
            username=username,
            password_hash=generate_password_hash(password),
        )

        db.session.add(admin)
        db.session.commit()
        print('Admin created successfully.')
    else:
        print('Admin already exists.')
