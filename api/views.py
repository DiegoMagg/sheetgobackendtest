from flask.views import MethodView
from os import environ
import jwt
import sqlite3
import openpyxl
from flask import request, jsonify, Response  # noqa
from settings import BASE_DIR


class XLSApi(MethodView):

    def post(self):
        authenticated, data = auth()
        if not authenticated:
            return jsonify({'detail': data}), 403
        return jsonify(self.parse_xls())

    def parse_xls(self):
        json = {}
        ws = list((openpyxl.load_workbook(request.files['file']).active).values)
        json['columns'] = ws.pop(0)
        json['lines'] = sorted(ws, key=lambda i: i[1])
        return json


def auth():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return False, 'Authentication credentials were not provided.'
    try:
        data = jwt.decode(auth_header.split()[1], environ.get('SEC_KEY'), algorithms=['HS256'])
        conn = sqlite3.connect(f'{BASE_DIR}/{environ.get("DATABASE")}')
        user = conn.execute(
            'SELECT * FROM user WHERE email=(?)', (data.get('email', ''),),
        ).fetchone()
        conn.close()
        return (True, '') if user else (False, 'Invalid credentials')
    except (jwt.exceptions.DecodeError, jwt.exceptions.InvalidSignatureError):
        return False, 'Invalid credentials.'
