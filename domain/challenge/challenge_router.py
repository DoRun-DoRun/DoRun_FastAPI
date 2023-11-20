from datetime import datetime

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from database import get_db, upload_file
from domain.challenge import challenge_schema, challenge_crud
from domain.challenge.challenge_crud import get_challenge_list, get_challenge_detail
from domain.user.user_router import get_current_user
from models import User

router = APIRouter(
    prefix="/challenge",
    tags=["challenge"]
)


@router.get("/all", response_model=list[challenge_schema.Challenge])
def challenge_list(_current_user: User = Depends(get_current_user)):
    _challenge_list = get_challenge_list(current_user=_current_user)

    if not _challenge_list:
        raise HTTPException(status_code=404, detail="Challenges not found")

    return _challenge_list


@router.get("/{challenge_mst_no}", response_model=challenge_schema.Challenge)
def challenge_detail(challenge_mst_no: int, db: Session = Depends(get_db),
                     _current_user: User = Depends(get_current_user)):
    _challenge = get_challenge_detail(db, challenge_no=challenge_mst_no)

    if not _challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    return _challenge


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
def challenge_create(_challenge_create: challenge_schema.ChallengeCreate,
                     db: Session = Depends(get_db),
                     _current_user: User = Depends(get_current_user)):
    challenge_crud.create_challenge(db, challenge_create=_challenge_create,
                                    current_user=_current_user)

# @router.post("/complete/daily", status_code=status.HTTP_204_NO_CONTENT)
# def complete_daily(_complete_daily: challenge_schema.CompleteDailyGoal,
#                    db: Session = Depends(get_db),
#                    _current_user: User = Depends(get_current_user)):
#     _challenge = get_challenge(db, challenge_id=_complete_daily.CHALLENGE_MST_NO)
#     challenge_crud.complete_daily_goal(db, complete_daily=_complete_daily,
#                                        current_challenge=_challenge,
#                                        current_user=_current_user)
#
#
# @router.put("/complete/weekly/{challenge_mst_no}", status_code=status.HTTP_204_NO_CONTENT)
# def complete_weekly(challenge_mst_no: int, db: Session = Depends(get_db),
#                     _current_user: User = Depends(get_current_user)):
#     # 챌린지 정보를 가져옵니다.
#     _challenge = get_challenge(db, challenge_id=challenge_mst_no)
#
#     # 챌린지가 존재하는지 확인합니다.
#     if not _challenge:
#         raise HTTPException(status_code=404, detail="Challenge not found")
#
#     # 챌린지에 team_goal 속성이 있는지 확인합니다.
#     if not hasattr(_challenge, 'team_goal') or not _challenge.team_goal:
#         raise HTTPException(status_code=404, detail="Team goal not found for the challenge")
#
#     for team_goal in _challenge.team_goal:
#         challenge_crud.complete_weekly_goal(db, db_team=team_goal, current_user=_current_user)
