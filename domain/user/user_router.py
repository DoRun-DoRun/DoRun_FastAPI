from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from domain.user import user_crud, user_schema
from domain.user.user_crud import encode_token, get_current_user
from domain.user.user_schema import CreateUser, UpdateUser, GetUser, UpdateUserResponse, GetUserSetting, \
    UpdateUserSetting
from models import User, AvatarUser, Avatar, UserSetting, SignType

router = APIRouter(
    prefix="/user",
    tags=["User"]
)


@router.post("/docs/login")
def user_test_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    current_user = user_crud.get_user_by_uid(db, uid=int(form_data.username))
    access_token = encode_token(str(current_user.UID), is_exp=True)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "UID": current_user.UID
    }


@router.post("", response_model=user_schema.Token)
def create_user(user: CreateUser, db: Session = Depends(get_db)):
    is_valid, message = user.is_valid

    if not is_valid:
        raise HTTPException(status_code=400, detail=message)

    new_uid = user_crud.create_user(user, db)

    access_token = encode_token(str(new_uid), is_exp=True)
    refresh_token = encode_token(str(new_uid), is_exp=False)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
        "UID": new_uid
    }


@router.get("", response_model=GetUser)
def get_user(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return user_crud.get_user(db, current_user)


@router.get("/login")
def login_for_access_token(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    access_token = encode_token(str(current_user.UID), is_exp=True)

    if not access_token:
        raise HTTPException(status_code=404, detail="AccessToken 발급 실패")

    current_user.RECENT_LOGIN_DT = datetime.utcnow()
    db.add(current_user)
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "UID": current_user.UID
    }


@router.put("", response_model=UpdateUserResponse)
def update_user(user: UpdateUser, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    user_crud.update_user(user, db, current_user)

    return UpdateUserResponse(
        UID=current_user.UID,
        USER_NM=current_user.USER_NM,
        SIGN_TYPE=current_user.SIGN_TYPE,
        USER_EMAIL=current_user.USER_EMAIL,
        ID_TOKEN=current_user.ID_TOKEN
    )


@router.delete("")
def delete_user(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    current_user.DISABLE_YN = True
    current_user.DISABLE_DT = datetime.utcnow()

    if current_user.USER_EMAIL:
        current_user.USER_EMAIL = current_user.USER_EMAIL + "#disabled"

    if current_user.ID_TOKEN:
        current_user.ID_TOKEN = None

    db.commit()

    return {
        "USER_UID": current_user.UID,
        "message": "삭제 성공"
    }


@router.get("/search/{uid}")
def search_user(uid: int, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_uid(db, uid)

    return user


@router.get("/avatar")
def get_avatars(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    avatars = db.query(AvatarUser).filter(
        AvatarUser.USER_NO == current_user.USER_NO,
    ).all()

    return avatars


@router.put("/avatar")
def set_equipped_avatar(avatar_user_no: int, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    avatar_user = db.query(AvatarUser).filter(
        AvatarUser.AVATAR_USER_NO == avatar_user_no).first()
    avatar = db.query(Avatar).filter(Avatar.AVATAR_NO == avatar_user.AVATAR_NO).first()
    equipped_avatar = user_crud.get_equipped_avatar(db, current_user.USER_NO, avatar.AVATAR_TYPE)

    avatar_user.IS_EQUIP = True
    equipped_avatar.IS_EQUIP = False
    db.commit()

    return {"message": "착용된 아바타 변경 성공"}


@router.get("/setting", response_model=GetUserSetting)
def get_user_setting(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_setting = db.query(UserSetting).filter(UserSetting.USER_NO == current_user.USER_NO).first()

    return GetUserSetting(
        NOTICE_PUSH_YN=user_setting.NOTICE_PUSH_YN,
        NOTICE_PUSH_NIGHT_YN=user_setting.NOTICE_PUSH_NIGHT_YN,
        NOTICE_PUSH_AD_YN=user_setting.NOTICE_PUSH_AD_YN,
        SIGN_TYPE=current_user.SIGN_TYPE,
        UID=current_user.UID,
    )


@router.put("/setting")
def get_user_setting(user_setting_data: UpdateUserSetting, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    user_setting = db.query(UserSetting).filter(UserSetting.USER_NO == current_user.USER_NO).first()

    user_setting.NOTICE_PUSH_YN = user_setting_data.NOTICE_PUSH_YN
    user_setting.NOTICE_PUSH_AD_YN = user_setting_data.NOTICE_PUSH_AD_YN
    user_setting.NOTICE_PUSH_NIGHT_YN = user_setting_data.NOTICE_PUSH_NIGHT_YN

    db.commit()

    return {"message": "유저 설정 변경 성공"}
