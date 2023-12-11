from typing import Optional

from pydantic import BaseModel, EmailStr

from models import SignType


class PostCreateUser(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    UID: int
    USER_NM: str


class CreateUser(BaseModel):
    ID_TOKEN: Optional[str] = None
    USER_EMAIL: Optional[EmailStr] = None
    SIGN_TYPE: SignType

    @property
    def is_valid(self):
        if self.SIGN_TYPE != SignType.GUEST:
            if not self.ID_TOKEN:
                return False, "ID_TOKEN을 입력해주세요."
            if not self.USER_EMAIL:
                return False, "USER_EMAIL 입력해주세요."
        return True, ""


class UpdateUser(BaseModel):
    USER_NM: Optional[str] = None
    SIGN_TYPE: Optional[SignType] = None
    USER_EMAIL: Optional[EmailStr] = None
    ID_TOKEN: Optional[str] = None


class UpdateUserResponse(BaseModel):
    UID: int
    USER_NM: str
    SIGN_TYPE: SignType
    USER_EMAIL: EmailStr
    ID_TOKEN: str


class GetUser(BaseModel):
    USER_NM: str
    USER_CHARACTER_NO: int
    COMPLETE: int
    PROGRESS: int
    PENDING: int


class GetUserSetting(BaseModel):
    NOTICE_PUSH_YN: bool
    NOTICE_PUSH_NIGHT_YN: bool
    NOTICE_PUSH_AD_YN: bool
    SIGN_TYPE: SignType
    UID: int


class UpdateUserSetting(BaseModel):
    NOTICE_PUSH_YN: bool
    NOTICE_PUSH_NIGHT_YN: bool
    NOTICE_PUSH_AD_YN: bool
