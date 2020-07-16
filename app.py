from flask import Flask
from os import environ, path
from db import db
from api.views import XLSApi
from settings import BASE_DIR

application = Flask(__name__)
application.config.from_mapping(
    SECRET_KEY=environ.get('SEC_KEY', 'dev'),
    DATABASE=path.join(BASE_DIR, 'xlsproject.sqlite'),
)
application.add_url_rule('/api/excel/info/', view_func=XLSApi.as_view('excel_info'))
application.teardown_appcontext
db.init(application)


@application.route('/')
def index():
    return "Sheetgo Back-end Test"
