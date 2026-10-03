from typing import NoReturn

from flask import abort


def unauthorized() -> NoReturn:
    abort(401)
