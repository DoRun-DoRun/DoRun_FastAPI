from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from domain.challenge import challenge_schema, challenge_crud
from domain.challenge.challenge_crud import get_challenge_list, get_challenge_detail, \
    get_challenge_invite, get_challenge_user_list, get_challenge_user_by_no
from domain.challenge.challenge_schema import ChallengeInvite, PutChallengeInvite
from domain.user.user_crud import get_current_user
from models import User, ChallengeUser

router = APIRouter(
    prefix="/challenge",
    tags=["challenge"]
)


@router.get("/list", response_model=list[challenge_schema.ChallengeList])
def challenge_list(db: Session = Depends(get_db),
                   _current_user: User = Depends(get_current_user)):
    _challenge_list = get_challenge_list(db, _current_user)

    if not _challenge_list:
        raise HTTPException(status_code=404, detail="참여중인 챌린지를 찾을 수 없습니다.")

    return _challenge_list


@router.get("/{challenge_mst_no}", response_model=challenge_schema.ChallengeDetail)
def challenge_detail(challenge_mst_no: int, current_day: datetime, db: Session = Depends(get_db),
                     _current_user: User = Depends(get_current_user)):
    _challenge = get_challenge_detail(db, user_no=_current_user.USER_NO, challenge_mst_no=challenge_mst_no,
                                      current_day=current_day)

    return _challenge


@router.post("")
def challenge_create(_challenge_create: challenge_schema.ChallengeCreate,
                     db: Session = Depends(get_db),
                     _current_user: User = Depends(get_current_user)):
    if len(_challenge_create.USERS_UID) > 6:
        raise HTTPException(status_code=404, detail="참가 가능한 최대 인원은 6명 입니다.")

    challenge = challenge_crud.post_create_challenge(db, challenge_create=_challenge_create,
                                                     current_user=_current_user)
    db.refresh(challenge)
    return {"message": "챌린지 생성 성공", "challenge": challenge}


# @router.put("")
# @router.delete("")
@router.get("/user/{challenge_user_no}", response_model=challenge_schema.GetChallengeUserDetail)
def get_challenge_user_detail(challenge_user_no: int, db: Session = Depends(get_db)):
    challenge_user = db.query(ChallengeUser).filter(ChallengeUser.CHALLENGE_USER_NO == challenge_user_no).first()
    if not challenge_user:
        return None  # 적절한 예외 처리 또는 반환값


@router.get("/user/list/{challenge_mst_no}", response_model=list[challenge_schema.ChallengeUserList])
def challenge_user_list(challenge_mst_no: int, db: Session = Depends(get_db)):
    challenge_user_list_data = get_challenge_user_list(db, challenge_mst_no)

    return challenge_user_list_data


@router.get("/invite/{challenge_mst_no}", response_model=ChallengeInvite)
def challenge_invite(challenge_mst_no: int, db: Session = Depends(get_db)):
    challenge_info = get_challenge_invite(db, challenge_mst_no)

    return challenge_info


@router.put("/invite/{challenge_mst_no}")
def challenge_invite(put_challenge_invite: PutChallengeInvite, db: Session = Depends(get_db),
                     _current_user: User = Depends(get_current_user)):
    challenge_user = get_challenge_user_by_no(db, put_challenge_invite.CHALLENGE_MST_NO, _current_user.USER_NO)
    challenge_user.ACCEPT_STATUS = put_challenge_invite.ACCEPT_STATUS
    db.commit()

    db.refresh(challenge_user)

    return {"message": "초대상태 수정완료", "challenge_user": challenge_user}

# @router.get("/mypage")
# def get_challenge_list_day(challenge_mst_no: int, current_day: datetime, db: Session = Depends(get_db),
#                            _current_user: User = Depends(get_current_user)):
