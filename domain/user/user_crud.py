from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from starlette import status
from starlette.config import Config

from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from models import User

from datetime import datetime, timedelta

config = Config('.env')
ACCESS_TOKEN_EXPIRE_MINUTES = int(config('ACCESS_TOKEN_EXPIRE_MINUTES'))
SECRET_KEY = config('SECRET_KEY')
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/docs/login")


# 추후 사용자 이름을 랜덤 문자열 조합으로 만들면 좋겠음
# 형용사 + 명사 (ex 부드러운 + 치즈케잌)
def create_guest_user(db: Session):
    db_user = User(USER_NM="Guest", SIGN_TYPE="GUEST")
    db.add(db_user)
    db.commit()
    return db_user.UID


def get_user(db: Session, uid: int):
    return db.query(User).filter(User.UID == uid).first()


def encode_token(sub: str, is_exp: bool):
    data = {
        "sub": sub,
    }
    if is_exp:
        data["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


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
        user = get_user(db, uid=uid)
        if user is None:
            print("NONE USER")
            raise credentials_exception
        return user
