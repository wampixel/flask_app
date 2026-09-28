from flask import Flask, Response


def register_middlewares(app: Flask) -> None:
    @app.after_request
    def set_security_headers(response: Response) -> None:
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"

        return response
