from flask import Flask, Request, Response, abort
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

from app.schemas import ErrorData


def build_error(e: HTTPException) -> ErrorData:
    return ErrorData(code=e.code, type=e.name.lower().replace(" ", "_"), message=e.description)


def reject_invalid_request(
    req: Request,
    resp: Response | None,
    req_validation_error: ValidationError | None,
    instance: object,
    model_adapter: object,
) -> None:
    if req_validation_error is None:
        return
    details = "; ".join(
        f"{'.'.join(map(str, error['loc']))}: {error['msg']}"
        for error in req_validation_error.errors(include_context=False)
    )
    abort(400, description=details)


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(HTTPException)
    def handleError(e: HTTPException) -> tuple[dict, int]:
        return build_error(e).model_dump(mode="json"), e.code
