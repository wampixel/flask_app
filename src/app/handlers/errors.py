from flask import jsonify
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handleError(e: HTTPException):
        return jsonify(code=e.code, type=e.name.lower().replace(" ", "_"), message=e.description), e.code
