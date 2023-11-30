from operator import and_

from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from sqlalchemy import or_
from starlette import status
from starlette.config import Config

from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from domain.desc.utils import random_user
from domain.user.user_schema import CreateUser, UpdateUser, UserPydantic
from models import User, SignType, UserSetting, Character, Pet

from datetime import datetime, timedelta

config = Config('.env')
ACCESS_TOKEN_EXPIRE_MINUTES = int(config('ACCESS_TOKEN_EXPIRE_MINUTES'))
SECRET_KEY = config('SECRET_KEY')
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/docs/login")


def create_user(user: CreateUser, db: Session):
    if user.SIGN_TYPE != SignType.GUEST:
        if not user.ID_TOKEN or user.USER_EMAIL:
            raise HTTPException(status_code=400, detail="ID_TOKEN과 EMAIL을 입력해주세요.")

        existing_user = db.query(User).filter(
            or_(User.ID_TOKEN == user.ID_TOKEN, User.USER_EMAIL == user.USER_EMAIL)
        ).first()

        if existing_user:
            if user.ID_TOKEN and existing_user.ID_TOKEN == user.ID_TOKEN:
                raise HTTPException(status_code=400, detail="ID_TOKEN already in use")
            if user.USER_EMAIL and existing_user.USER_EMAIL == user.USER_EMAIL:
                raise HTTPException(status_code=400, detail="USER_EMAIL already in use")

    if user.SIGN_TYPE == SignType.GUEST:
        db_user = User(USER_NM=random_user(), SIGN_TYPE=user.SIGN_TYPE)
    else:
        db_user = User(USER_NM=random_user(), SIGN_TYPE=user.SIGN_TYPE,
                       USER_EMAIL=user.USER_EMAIL, ID_TOKEN=user.ID_TOKEN)
    db.add(db_user)
    db.commit()

    db_user_setting = UserSetting(
        USER_NO=db_user.USER_NO,
    )
    db.add(db_user_setting)

    # db_character_user = CharacterUser(
    #     IS_EQUIP=True,
    #     USER_NO=db_user.USER_NO,
    #     CHARACTER_NO=1,
    # )
    # db.add(db_character_user)

    db.commit()

    return db_user.UID


def update_user(user: UpdateUser, db: Session, current_user: User):
    # 중복 체크 쿼리 조건 생성
    query_conditions = []
    if user.USER_EMAIL is not None:
        query_conditions.append(User.USER_EMAIL == user.USER_EMAIL)
    if user.ID_TOKEN is not None:
        query_conditions.append(User.ID_TOKEN == user.ID_TOKEN)

    # 중복 체크 및 에러 처리
    if query_conditions:
        existing_user = db.query(User).filter(
            or_(*query_conditions),
            User.USER_NO != current_user.USER_NO  # 현재 사용자 제외
        ).first()

        if existing_user:
            if user.USER_EMAIL and existing_user.USER_EMAIL == user.USER_EMAIL:
                raise HTTPException(status_code=400, detail="USER_EMAIL already in use")
            if user.ID_TOKEN and existing_user.ID_TOKEN == user.ID_TOKEN:
                raise HTTPException(status_code=400, detail="ID_TOKEN already in use")

    # UpdateUser 모델에서 제공된 값으로 필드 업데이트
    if user.USER_NM is not None:
        current_user.USER_NM = user.USER_NM
    if user.SIGN_TYPE is not None:
        current_user.SIGN_TYPE = user.SIGN_TYPE
    if user.USER_EMAIL is not None:
        current_user.USER_EMAIL = user.USER_EMAIL
    if user.ID_TOKEN is not None:
        current_user.ID_TOKEN = user.ID_TOKEN

    db.commit()


# def get_user(db: Session, current_user: User):
#     # Character와 CharacterUser 테이블 조인
#     characters = db.query(
#         Character.CHARACTER_NO,
#         Character.CHARACTER_NM,
#         CharacterUser.IS_EQUIP
#     ).outerjoin(
#         CharacterUser,
#         (Character.CHARACTER_NO == CharacterUser.CHARACTER_NO) &
#         (CharacterUser.USER_NO == current_user.USER_NO)
#     ).all()
#
#     # 결과 포매팅
#     character_list = []
#     for character_no, character_nm, is_equip in characters:
#         character_info = {
#             "CHARACTER_NO": character_no,
#             "CHARACTER_NM": character_nm,
#             "OWNED": is_equip is not None,
#             "EQUIPPED": bool(is_equip)
#         }
#         character_list.append(character_info)
#
#     # Pet과 PetUser 테이블 조인
#     pets = db.query(
#         Pet.PET_NO,
#         Pet.PET_NM,
#         Pet.IS_EQUIP
#     ).outerjoin(
#         PetUser,
#         (Pet.CHARACTER_NO == PetUser.CHARACTER_NO) &
#         (PetUser.USER_NO == current_user.USER_NO)
#     ).all()
#
#     # 결과 포매팅
#     pet_list = []
#     for pet_no, pet_nm, is_equip in pets:
#         pet_info = {
#             "CHARACTER_NO": pet_no,
#             "CHARACTER_NM": pet_nm,
#             "OWNED": is_equip is not None,
#             "EQUIPPED": bool(is_equip)
#         }
#         pet_list.append(pet_info)
#
#     return {"user": current_user, "character": character_list, "pet": pet_list}


def get_user_by_uid(db: Session, uid: int):
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
        user = get_user_by_uid(db, uid=uid)
        if user is None:
            print("NONE USER")
            raise credentials_exception
        if user.DISABLE_YN is True:
            raise HTTPException(status_code=404, detail="탈퇴한 유저입니다.", )
        return user
