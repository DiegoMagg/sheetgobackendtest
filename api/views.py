from flask.views import MethodView


class XLSApi(MethodView):

    def get(self):
        return 'test'

    def post(self):
        breakpoint()
