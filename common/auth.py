import jwt
from functools import wraps
from os import environ
import sqlite3
from flask import request, jsonify
from settings import BASE_DIR


def authenticate(f):
    @wraps(f)
    def auth_func(*args, **kwargs):
        if not request.headers.get('Authorization'):
            return jsonify({'detail': 'Authentication credentials were not provided.'}), 401
        try:
            if user(request.headers.get('Authorization')):
                return f(*args, **kwargs)
            return jsonify({'detail': 'Invalid credentials.'}), 401
        except (jwt.exceptions.DecodeError, jwt.exceptions.InvalidSignatureError):
            return jsonify({'detail': 'Invalid credentials.'}), 401
    return auth_func


def user(token):
    data = jwt.decode(token.split()[1], environ.get('SEC_KEY'), algorithms=['HS256'])
    conn = sqlite3.connect(f'{BASE_DIR}/{environ.get("DATABASE")}')
    user = conn.execute('SELECT * FROM user WHERE email=(?)', (data.get('email', ''),)).fetchone()
    conn.close()
    return user
