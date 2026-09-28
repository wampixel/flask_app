from flask import abort, jsonify


def unauthorized() -> None:
    resp = jsonify(message="Unauthorized")
    resp.status_code = 401
    abort(resp)
