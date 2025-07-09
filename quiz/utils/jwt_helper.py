import jwt
from flask import current_app
from datetime import datetime, UTC

def generate_token(payload):
    expiration = datetime.now(UTC) + current_app.config['JWT_EXPIRATION_DELTA']
    payload.update({'exp': expiration})
    token = jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    return token

def decode_token(token):
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None