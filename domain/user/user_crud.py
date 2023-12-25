from collections import Counter

from fastapi import Depends, HTTPException
from jose import jwt, JWTError, ExpiredSignatureError
from sqlalchemy import or_
from starlette.config import Config

from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from domain.challenge import challenge_crud
from domain.desc.utils import random_user
from domain.user.user_schema import CreateUser, UpdateUser, GetUser
from models import User, SignType, UserSetting, AvatarUser, ChallengeStatusType, AvatarType, Avatar, ChallengeMaster, \
    ChallengeUser, InviteAcceptType

from datetime import datetime, timedelta

config = Config('.env')
ACCESS_TOKEN_EXPIRE_MINUTES = int(config('ACCESS_TOKEN_EXPIRE_MINUTES'))
SECRET_KEY = config('SECRET_KEY')
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/docs/login")


# 기능 함수
# EMAIL과 ID_TOKEN의 중복 확인
def check_user_email_id_token_duplicate(db: Session, user_email: str, id_token: str, current_user_id: int = None):
    query_conditions = []
    if user_email:
        query_conditions.append(User.USER_EMAIL == user_email)
    if id_token:
        query_conditions.append(User.ID_TOKEN == id_token)

    if current_user_id:
        query_conditions.append(User.USER_NO != current_user_id)

    existing_user = db.query(User).filter(or_(*query_conditions)).first()
    if existing_user:
        if user_email and existing_user.USER_EMAIL == user_email:
            raise HTTPException(status_code=400, detail="입력된 USER_EMAIL가 이미 존재합니다.")
        if id_token and existing_user.ID_TOKEN == id_token:
            raise HTTPException(status_code=400, detail="입력된 ID_TOKEN가 이미 존재합니다.")


# UID를 통해서 유저 반환
def get_user_by_uid(db: Session, uid: int):
    user = db.query(User).filter(User.UID == uid, User.DISABLE_YN == False).first()
    if not user:
        raise HTTPException(status_code=401, detail="UID로 부터 사용자를 찾을 수 없습니다.")

    return user


# JWT 토큰 발급
def encode_token(sub: str, is_exp: bool):
    data = {
        "sub": sub,
    }
    if is_exp:
        data["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


# 현재 AccessToken의 유저 반환
def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        # 토큰이 만료된 경우 새 토큰 발급
        raise HTTPException(status_code=401, detail="토큰이 만료되었습니다.")
    except JWTError:
        # 다른 JWT 에러 처리
        raise HTTPException(status_code=404, detail="JWT 에러")

    uid = int(payload.get("sub"))
    if uid is None:
        raise HTTPException(status_code=401, detail="토큰값으로부터 UID 정보를 찾을 수 없습니다.")

    user = get_user_by_uid(db, uid=uid)
    return user


def refresh_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        uid = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=400, detail="유효하지 않은 토큰입니다.")

    user = get_user_by_uid(db, uid)
    user.RECENT_LOGIN_DT = datetime.utcnow()
    db.add(user)
    db.commit()

    # 새로운 토큰 생성
    new_token = encode_token(sub=uid, is_exp=True)
    return new_token


# 라우터 함수
def create_user(user: CreateUser, db: Session):
    if user.SIGN_TYPE != SignType.GUEST:
        check_user_email_id_token_duplicate(db, user.USER_EMAIL, user.ID_TOKEN)

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
    db_avatar_user = AvatarUser(
        IS_EQUIP=True,
        USER_NO=db_user.USER_NO,
        AVATAR_NO=1,
    )
    db.add(db_avatar_user)
    db.commit()

    return db_user


def update_user(user: UpdateUser, db: Session, current_user: User):
    check_user_email_id_token_duplicate(db, user.USER_EMAIL, user.ID_TOKEN, current_user.USER_NO)

    if user.USER_NM is not None:
        current_user.USER_NM = user.USER_NM
    if user.SIGN_TYPE is not None:
        current_user.SIGN_TYPE = user.SIGN_TYPE
    if user.USER_EMAIL is not None:
        current_user.USER_EMAIL = user.USER_EMAIL
    if user.ID_TOKEN is not None:
        current_user.ID_TOKEN = user.ID_TOKEN

    db.commit()


def get_user(db: Session, current_user: User):
    equipped_avatar_user = db.query(AvatarUser) \
        .filter(AvatarUser.USER_NO == current_user.USER_NO) \
        .filter(AvatarUser.IS_EQUIP == True) \
        .first()
    if not equipped_avatar_user:
        raise HTTPException(status_code=400, detail="착용된 아바타를 찾을 수 없습니다.")

    challenges = db.query(ChallengeMaster). \
        join(ChallengeUser, ChallengeUser.CHALLENGE_MST_NO == ChallengeMaster.CHALLENGE_MST_NO). \
        filter(ChallengeUser.USER_NO == current_user.USER_NO,
               ChallengeUser.ACCEPT_STATUS == InviteAcceptType.ACCEPTED,
               ChallengeMaster.DELETE_YN == False).all()

    status_counts = Counter(challenge.CHALLENGE_STATUS for challenge in challenges)

    return GetUser(USER_NM=current_user.USER_NM, USER_CHARACTER_NO=equipped_avatar_user.AVATAR_NO,
                   COMPLETE=status_counts[ChallengeStatusType.COMPLETE],
                   PROGRESS=status_counts[ChallengeStatusType.PROGRESS],
                   PENDING=status_counts[ChallengeStatusType.PENDING])


# 착용중인 아바타 가져오기
def get_equipped_avatar(db: Session, user_no: int, avatar_type: AvatarType):
    avatar = db.query(AvatarUser).join(Avatar, Avatar.AVATAR_NO == AvatarUser.AVATAR_NO).filter(
        AvatarUser.USER_NO == user_no,
        AvatarUser.IS_EQUIP == True,
        Avatar.AVATAR_TYPE == avatar_type
    ).first()

    if avatar_type == AvatarType.CHARACTER and not avatar:
        raise HTTPException(status_code=404, detail="CHARACTER 정보를 찾을 수 없습니다.")

    return avatar
