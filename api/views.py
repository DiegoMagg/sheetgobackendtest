from flask.views import MethodView
from re import sub
from os import environ, remove
import jwt
import sqlite3
import openpyxl
from PIL import Image
from flask import request, jsonify, Response, send_file  # noqa
from settings import BASE_DIR


class XLSApi(MethodView):

    def post(self):
        authenticated, data = auth()
        if not authenticated:
            return jsonify({'detail': data}), 403
        return jsonify(self.parse_xls())

    def parse_xls(self):
        json = {}
        ws = list(openpyxl.load_workbook(request.files['file']).active.values)
        json['columns'] = ws.pop(0)
        json['rows'] = sorted(ws, key=lambda i: i[1])
        return json


class ImageConversionApi(MethodView):
    accepted_formats = ('png', 'jpeg')
    converted_files_path = f'{BASE_DIR}/static/images/converted/'

    def post(self):
        authenticated, data = auth()
        if not authenticated:
            return jsonify({'detail': data}), 403
        return self.handle_image()

    def handle_image(self):
        param = request.form.to_dict().get('format')
        if not param or param not in self.accepted_formats:
            return jsonify({'detail': 'unsupported format or format is missing.'}), 400
        filepath = self.converted_files_path + sub(r'\.\w+', f'.{param}', request.files['file'].filename)
        Image.open(request.files['file']).convert('RGB').save(filepath)
        response = send_file(filepath, attachment_filename=filepath.split('/')[-1])
        remove(filepath)
        return response


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
