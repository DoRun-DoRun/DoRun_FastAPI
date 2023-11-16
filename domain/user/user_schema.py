from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    UID: int


class User(BaseModel):
    UID: int
    USER_NM: str
