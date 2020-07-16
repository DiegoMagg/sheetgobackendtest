from flask.views import MethodView
from flask import request # noqa


class XLSApi(MethodView):

    def post(self):
        return 'ok'
