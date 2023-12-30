from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query
from sqlalchemy.orm import Session

from database import get_db
from domain.challenge import challenge_schema, challenge_crud
from domain.challenge.challenge_crud import get_challenge_list, get_challenge_detail, \
    get_challenge_invite, get_challenge_user_by_user_no, start_challenge
from domain.challenge.challenge_schema import ChallengeInvite, PutChallengeInvite
from domain.user.user_crud import get_current_user
from models import User, ChallengeUser

router = APIRouter(
    prefix="/challenge",
    tags=["Challenge"]
)


@router.get("/list", response_model=challenge_schema.ChallengeList)
def challenge_list(db: Session = Depends(get_db),
                   _current_user: User = Depends(get_current_user)):
    _challenge_list = get_challenge_list(db, _current_user)

    return _challenge_list


@router.get("/detail/{challenge_mst_no}", response_model=challenge_schema.ChallengeDetail)
def challenge_detail(challenge_mst_no: int, db: Session = Depends(get_db),
                     _current_user: User = Depends(get_current_user)):
    _challenge = get_challenge_detail(db, user_no=_current_user.USER_NO, challenge_mst_no=challenge_mst_no)

    return _challenge


@router.post("")
def challenge_create(_challenge_create: challenge_schema.ChallengeCreate,
                     db: Session = Depends(get_db),
                     _current_user: User = Depends(get_current_user)):
    if len(_challenge_create.USERS_UID) > 6:
        raise HTTPException(status_code=404, detail="참가 가능한 최대 인원은 6명 입니다.")

    _challenge_list = get_challenge_list(db, _current_user)

    if len(_challenge_list["progress_challenges"]) >= 3:
        raise HTTPException(status_code=404, detail="참가 가능한 챌린지는 3개입니다.")

    challenge = challenge_crud.post_create_challenge(db, challenge_create=_challenge_create,
                                                     current_user=_current_user)
    db.refresh(challenge)
    return challenge


@router.post("/start")
def challenge_start(challenge_mst_no: int, start_dt: datetime, db: Session = Depends(get_db),
                    current_user=Depends(get_current_user)):
    message = start_challenge(db, challenge_mst_no, current_user, start_dt)
    return message


@router.put("/{challenge_mst_no}")
def challenge_update(challenge_mst_no: int, _challenge_update: challenge_schema.ChallengeCreate,
                     db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    message = challenge_crud.challenge_update(db, challenge_mst_no, _challenge_update, current_user)
    return message


@router.delete("/{challenge_mst_no}")
def challenge_delete(challenge_mst_no: int, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    message = challenge_crud.challenge_delete(db, challenge_mst_no, current_user)
    return message


@router.get("/user/list", response_model=challenge_schema.ChallengeUserListModel)
def get_challenge_user_list(db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
                            page: int = Query(1, description="페이지 번호")):
    if page < 1:
        raise HTTPException(status_code=404, detail="페이지 숫자는 0보다 커야합니다.")
    challenge_user_list_data = challenge_crud.get_challenge_user_list(db, current_user, page)

    return challenge_user_list_data


@router.get("/user/{challenge_user_no}", response_model=challenge_schema.GetChallengeUserDetail)
def get_challenge_user_detail(challenge_user_no: int, db: Session = Depends(get_db),
                              current_user: User = Depends(get_current_user)):
    challenge_user_detail = challenge_crud.get_challenge_user_detail(db, challenge_user_no, current_user)

    return challenge_user_detail


@router.put("/user/{challenge_user_no}")
def put_challenge_user_detail(challenge_user_no: int, comment: str, db: Session = Depends(get_db),
                              current_user: User = Depends(get_current_user)):
    challenge_user = challenge_crud.get_challenge_user_by_challenge_user_no(db, challenge_user_no)

    if challenge_user.USER_NO != current_user.USER_NO:
        raise HTTPException(status_code=401, detail="수정 권한이 없습니다.")

    challenge_user.COMMENT = comment
    db.commit()
    db.refresh(challenge_user)

    return {"message": "상태메시지 수정완료", "challenge_user": challenge_user}


@router.get("/invite/{challenge_mst_no}", response_model=ChallengeInvite)
def challenge_invite(challenge_mst_no: int, db: Session = Depends(get_db),
                     _current_user: User = Depends(get_current_user)):
    challenge_info = get_challenge_invite(db, challenge_mst_no, _current_user)

    return challenge_info


@router.put("/invite/{challenge_mst_no}")
def challenge_invite(put_challenge_invite: PutChallengeInvite, db: Session = Depends(get_db),
                     _current_user: User = Depends(get_current_user)):
    _challenge_list = get_challenge_list(db, _current_user)

    if len(_challenge_list["progress_challenges"]) >= 3:
        raise HTTPException(status_code=404, detail="참가 가능한 챌린지는 3개입니다.")

    challenge_user = get_challenge_user_by_user_no(db, put_challenge_invite.CHALLENGE_MST_NO, _current_user.USER_NO)
    challenge_user.ACCEPT_STATUS = put_challenge_invite.ACCEPT_STATUS
    db.commit()

    db.refresh(challenge_user)

    return {"message": "초대상태 수정완료", "challenge_user": challenge_user, "status": put_challenge_invite.ACCEPT_STATUS}


@router.get("/history", response_model=challenge_schema.GetChallengeHistory)
def get_challenge_history_list(current_day: datetime, page: int = Query(1, description="페이지 번호"),
                               db: Session = Depends(get_db),
                               _current_user: User = Depends(get_current_user)):
    challenge_history_list = challenge_crud.get_challenge_history_list(db, current_day, _current_user, page)
    return challenge_history_list
