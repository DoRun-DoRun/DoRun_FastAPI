from typing import Optional

from pydantic import BaseModel, EmailStr

from models import SignType


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    UID: int


class CreateUser(BaseModel):
    ID_TOKEN: Optional[str] = None
    USER_NM: Optional[str] = None
    USER_EMAIL: Optional[EmailStr] = None
    SIGN_TYPE: SignType
