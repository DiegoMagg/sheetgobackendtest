from re import sub
import requests
from json import dumps, loads
import openpyxl
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from flask import request, send_file, abort  # noqa
from flask.views import MethodView
from common.auth import authenticate
from settings import CONVERTED_FILES_PATH, ACCEPTED_FORMATS, DROPBOX_CONVERTED_FILES_PATH


class XLSApi(MethodView):

    @authenticate
    def post(self):
        json = {}
        ws = list(openpyxl.load_workbook(request.files['file']).active.values)
        json['columns'] = ws.pop(0)
        json['rows'] = sorted(ws, key=lambda i: i[1])
        return json


class ImageConversionApi(MethodView):

    @authenticate
    def post(self):
        param = request.form.to_dict().get('format')
        if not param or param.lower() not in ACCEPTED_FORMATS:
            return {'detail': 'Unsupported format or format is missing.'}, 400
        filepath = CONVERTED_FILES_PATH + sub(r'\.\w+$', f'.{param}', request.files['file'].filename)
        Image.open(request.files['file']).convert('RGB').save(filepath)
        response = send_file(filepath, attachment_filename=filepath.split('/')[-1])
        return response


class DropboxImageConversionApi(MethodView):
    url = "https://content.dropboxapi.com/2/files/download"

    @authenticate
    def post(self):
        request_is_valid, json = self.validate_request()
        if not request_is_valid:
            return json, 400
        response = requests.post(self.url, headers=self.set_header(json))
        if response.ok:
            return self.image_converter(json, response)
        return {'error': 'Check dropbox token or file path.'}, 400

    def validate_request(self):
        if not request.json.get('format') or request.json.get('format').lower() not in ACCEPTED_FORMATS:
            return False, {'detail': 'Unsupported format or format is missing.'}
        if not request.json.get('dropbox_token'):
            return False, {'detail': 'dropbox token is missing.'}
        if not request.json.get('path'):
            return False, {'detail': 'dropbox file path is missing.'}
        return True, request.json

    def set_header(self, data):
        return {
            'Authorization': f'Bearer {data["dropbox_token"]}',
            'Dropbox-API-Arg': dumps({'path': data['path']}),
        }

    def image_converter(self, json, response):
        filepath = DROPBOX_CONVERTED_FILES_PATH + sub(
            r'\.\w+$', f'.{json["format"]}', loads(response.headers['Dropbox-Api-Result'])['name'],
        )
        try:
            Image.open(BytesIO(response.content)).convert('RGB').save(filepath)
            return send_file(filepath, attachment_filename=filepath.split('/')[-1])
        except UnidentifiedImageError:
            return {'detail': 'Invalid file.'}, 400
