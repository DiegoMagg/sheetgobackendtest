from flask import Flask
from os import environ, path
from db import db
from accounts import user_manager
from api.views import XLSApi, ImageConversionApi, DropboxImageConversionApi
from settings import BASE_DIR

application = Flask(__name__)
application.config.from_mapping(
    SECRET_KEY=environ.get('SEC_KEY', 'dev'),
    DATABASE=path.join(BASE_DIR, environ.get('DATABASE')),
)
application.add_url_rule('/api/excel/info/', view_func=XLSApi.as_view('excel_info'))
application.add_url_rule('/api/image/convert/', view_func=ImageConversionApi.as_view('image_conversion'))
application.add_url_rule(
    '/api/image/convert/fromdropbox/', view_func=DropboxImageConversionApi.as_view('dropbox_conversion'),
)
db.init(application)
user_manager.init(application)


@application.route('/')
def index():
    return "Sheetgo Back-end Test"
