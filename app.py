from flask import Flask
from os import environ
from api.views import XLSApi


application = Flask(__name__)
application.config.from_mapping(SECRET_KEY=environ.get('SEC_KEY', 'dev'))
application.add_url_rule('/api', view_func=XLSApi.as_view('api'))


@application.route('/')
def index():
    return "Sheetgo Back-end Test"
