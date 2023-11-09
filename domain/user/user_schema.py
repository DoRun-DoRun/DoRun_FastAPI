from pydantic import BaseModel, field_validator, EmailStr

from models import login_type


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    SIGN_TYPE: login_type

    @field_validator('username', 'SIGN_TYPE', 'email')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('빈 값은 허용되지 않습니다.')
        return v

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str