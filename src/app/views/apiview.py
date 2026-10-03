from flask.views import MethodView


class ApiView(MethodView):
    provide_automatic_options = False
