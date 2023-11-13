import secrets
from datetime import timedelta, datetime

from starlette.config import Config

from fastapi import APIRouter, HTTPException
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.user import user_crud, user_schema
from models import User

router = APIRouter(
    prefix="/api/user",
)

config = Config('.env')
ACCESS_TOKEN_EXPIRE_MINUTES = int(config('ACCESS_TOKEN_EXPIRE_MINUTES'))
SECRET_KEY = config('SECRET_KEY')
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/test/login")


@router.post("/test/login")
def user_test_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    current_user = user_crud.get_user(db, uid=int(form_data.username))
    data = {
        "sub": str(current_user.UID),
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "UID": current_user.UID
    }


@router.post("/create/guest", response_model=user_schema.Token)
def user_create(db: Session = Depends(get_db)):
    # user = user_crud.get_existing_user(db, user_create=_user_create)
    # if user:
    #     raise HTTPException(status_code=status.HTTP_409_CONFLICT,
    #                         detail="이미 존재하는 EMAIL입니다.")
    new_uid = user_crud.generate_uid(db)
    user_crud.create_guest_user(db=db, uid=new_uid)

    # Access Token 생성
    data = {
        "sub": str(new_uid),
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    # Refresh Token 생성
    refresh_token = jwt.encode({"sub": str(new_uid)}, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
        "UID": new_uid
    }


def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid = int(payload.get("sub"))
        if uid is None:
            print("NONE")
            raise credentials_exception
    except JWTError:
        print("ERROR")
        raise credentials_exception
    else:
        user = user_crud.get_user(db, uid=uid)
        if user is None:
            print("NONE USER")
            raise credentials_exception
        return user


@router.post("/login")
def login_for_access_token(current_user: User = Depends(get_current_user)):
    data = {
        "sub": current_user.UID,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "UID": current_user.UID
    }
