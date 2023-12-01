from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from domain.challenge import challenge_schema, challenge_crud
from domain.challenge.challenge_crud import get_challenge_list, get_challenge_detail, get_challenge_participants, \
    get_challenge_master_by_id, get_challenge_invite, get_challenge_user_list
from domain.challenge.challenge_schema import ChallengeParticipant, ChallengeInvite
from domain.user.user_crud import get_current_user
from models import User

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


@router.get("/invite/{challenge_mst_no}", response_model=ChallengeInvite)
def challenge_invite(challenge_mst_no: int, db: Session = Depends(get_db)):
    challenge_info = get_challenge_invite(db, challenge_mst_no)

    return challenge_info


@router.get("/user/list/{challenge_mst_no}", response_model=list[challenge_schema.ChallengeUserList])
def challenge_user_list(challenge_mst_no: int, db: Session = Depends(get_db)):
    challenge_user_list_data = get_challenge_user_list(db, challenge_mst_no)

    return challenge_user_list_data


@router.post("")
def challenge_create(_challenge_create: challenge_schema.ChallengeCreate,
                     db: Session = Depends(get_db),
                     _current_user: User = Depends(get_current_user)):
    challenge_crud.post_create_challenge(db, challenge_create=_challenge_create,
                                         current_user=_current_user)

    return {"message": "챌린지 생성 성공"}
