from flask.views import MethodView
from os import environ
from flask import request, jsonify, Response # noqa
import jwt
import sqlite3
from settings import BASE_DIR


class XLSApi(MethodView):
    conn = sqlite3.connect(f'{BASE_DIR}/{environ.get("DATABASE")}')

    def post(self):
        authenticated, message = self.auth()
        if not authenticated:
            return jsonify({'detail': message}), 403
        return 'ok'

    def auth(self):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return False, 'Authentication credentials were not provided.'
        try:
            data = jwt.decode(auth_header.split()[1], environ.get('SEC_KEY'), algorithms=['HS256'])
            user = self.conn.execute('SELECT * FROM user WHERE email=(?)', (data.get('email', ''),))
            return (True, '') if user.fetchone() else (False, 'Invalid credentials')
        except (jwt.exceptions.DecodeError, jwt.exceptions.InvalidSignatureError):
            return False, 'Invalid credentials.'
