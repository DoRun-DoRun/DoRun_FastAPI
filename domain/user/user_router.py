from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from domain.user import user_crud, user_schema
from domain.user.user_crud import encode_token, get_current_user, refresh_token, get_equipped_avatar
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


@router.post("", response_model=user_schema.PostCreateUser)
def create_user(user: CreateUser, db: Session = Depends(get_db)):
    is_valid, message = user.is_valid

    if not is_valid:
        raise HTTPException(status_code=400, detail=message)

    user = user_crud.create_user(user, db)

    access_token = encode_token(str(user.UID), is_exp=True)
    _refresh_token = encode_token(str(user.UID), is_exp=False)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": _refresh_token,
        "UID": user.UID,
        "USER_NM": user.USER_NM
    }


@router.get("", response_model=GetUser)
def get_user(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return user_crud.get_user(db, current_user)


@router.get("/login")
def login_for_access_token(access_token=Depends(refresh_token)):
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# @router.get("/callback")
# def refresh_user(token=Depends(get_new_token)):
#     return {"access_token": token}


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
        "UID": current_user.UID,
        "message": "삭제 성공"
    }


@router.get("/search/{uid}")
def search_user(uid: int, db: Session = Depends(get_db)):
    # user = user_crud.get_user_by_uid(db, uid)

    user = db.query(User).filter(User.UID == uid, User.DISABLE_YN == False).first()
    if not user:
        return {"USER_NM": None, "UID": None}

    return {"USER_NM": user.USER_NM, "UID": user.UID}


@router.get("/avatar")
def get_avatars(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # AvatarUser와 Avatar 조인하여 쿼리
    query = db.query(Avatar, AvatarUser). \
        outerjoin(AvatarUser, (AvatarUser.AVATAR_NO == Avatar.AVATAR_NO) & (AvatarUser.USER_NO == current_user.USER_NO))

    avatars = []
    for avatar, avatar_user in query.all():
        avatars.append({
            "IS_EQUIP": avatar_user.IS_EQUIP if avatar_user else False,
            "AVATAR_NO": avatar.AVATAR_NO,
            "AVATAR_NM": avatar.AVATAR_NM,
            "AVATAR_TYPE": avatar.AVATAR_TYPE,
            "IS_OWNED": avatar_user is not None  # 사용자가 보유하고 있으면 True
        })
    return {
        "USER_NM": "노련한 서리태",  # 이 부분은 현재 사용자의 이름을 추가하는 예시입니다.
        "avatars": avatars
    }


@router.put("/avatar")
def set_equipped_avatar(avatar_no: int, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    # 선택한 아바타 조회
    avatar_user = db.query(AvatarUser).filter(
        AvatarUser.USER_NO == current_user.USER_NO,
        AvatarUser.AVATAR_NO == avatar_no
    ).first()

    if not avatar_user:
        raise HTTPException(status_code=404, detail="아바타를 찾을 수 없습니다.")

    # 선택한 아바타의 타입 조회
    avatar = db.query(Avatar).filter(Avatar.AVATAR_NO == avatar_user.AVATAR_NO).first()

    # 현재 착용 중인 동일 타입의 아바타 조회
    equipped_avatar = get_equipped_avatar(db, current_user.USER_NO, avatar.AVATAR_TYPE)

    # 아바타 상태 변경
    if equipped_avatar:
        equipped_avatar.IS_EQUIP = False
    avatar_user.IS_EQUIP = True

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
