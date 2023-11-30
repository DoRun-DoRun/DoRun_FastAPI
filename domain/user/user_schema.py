from typing import Optional, List

from pydantic import BaseModel, EmailStr

from models import SignType


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    UID: int


class CreateUser(BaseModel):
    ID_TOKEN: Optional[str] = None
    USER_EMAIL: Optional[EmailStr] = None
    SIGN_TYPE: SignType


class UpdateUser(BaseModel):
    USER_NM: Optional[str] = None
    SIGN_TYPE: Optional[SignType] = None
    USER_EMAIL: Optional[EmailStr] = None
    ID_TOKEN: Optional[str] = None


class UserPydantic(BaseModel):
    UID: int
    USER_NM: str
    SIGN_TYPE: SignType
    USER_EMAIL: EmailStr


class PetPydantic(BaseModel):
    UID: int
    USER_NM: str
    SIGN_TYPE: SignType
    USER_EMAIL: EmailStr


class CharacterPydantic(BaseModel):
    UID: int
    USER_NM: str
    SIGN_TYPE: SignType
    USER_EMAIL: EmailStr


class UserMyPagePydantic(BaseModel):
    user: UserPydantic
    pet: List[PetPydantic]
    character: List[CharacterPydantic]
