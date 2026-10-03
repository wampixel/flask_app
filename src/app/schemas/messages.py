from datetime import datetime

from pydantic import BaseModel


class MessageData(BaseModel):
    message: str


class ErrorData(BaseModel):
    code: int
    type: str
    message: str


class TokenData(BaseModel):
    access_token: str
    token_type: str
    expires_at: datetime
