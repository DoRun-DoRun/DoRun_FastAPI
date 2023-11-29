from fastapi import APIRouter
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from domain.user import user_crud, user_schema
from domain.user.user_crud import encode_token, get_current_user
from domain.user.user_schema import CreateUser
from models import User, SignType

router = APIRouter(
    prefix="/user",
    tags=["user"]
)


@router.post("/docs/login")
def user_test_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    current_user = user_crud.get_user(db, uid=int(form_data.username))
    access_token = encode_token(str(current_user.UID), is_exp=True)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "UID": current_user.UID
    }


@router.post("/{sign_type}", response_model=user_schema.Token)
def user_create(sign_type: SignType, user: CreateUser, db: Session = Depends(get_db)):
    new_uid = user_crud.create_user(sign_type, user, db)

    access_token = encode_token(str(new_uid), is_exp=True)
    refresh_token = encode_token(str(new_uid), is_exp=False)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
        "UID": new_uid
    }


@router.get("")
def login_for_access_token(current_user: User = Depends(get_current_user)):
    access_token = encode_token(str(current_user.UID), is_exp=True)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "UID": current_user.UID
    }
