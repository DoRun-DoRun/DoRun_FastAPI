from pydantic import BaseModel, EmailStr
from pydantic.v1 import validator
from typing import Optional
from models import LoginType

import enum


# class UserCreate(BaseModel):
#     USER_NM: str
#     USER_EMAIL: EmailStr
#     SIGN_TYPE: login_type
#
#     @validator('USER_NM', 'USER_EMAIL')
#     def not_empty_string(cls, v):
#         if not v or not v.strip():
#             raise ValueError('빈 값은 허용되지 않습니다.')
#         return v
#
#     @validator('SIGN_TYPE')
#     def validate_enum(cls, v):
#         if not v:
#             raise ValueError('Enum 값은 비어 있을 수 없습니다.')
#         return v


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    UID: int


class User(BaseModel):
    UID: int
    USER_NM: str
