from flask import Flask

from .authentication import authenticate, public, unauthorized
from .security import set_security_headers


def register_middlewares(app: Flask) -> None:
    app.after_request(set_security_headers)


__all__ = ["authenticate", "public", "register_middlewares", "unauthorized"]
