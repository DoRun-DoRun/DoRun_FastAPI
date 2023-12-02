from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.challenge.challenge_crud import get_challenge_master_by_id, get_challenge_user_by_challenge_user_no
from domain.challenge.weekly import weekly_crud
from domain.challenge.weekly.weekly_crud import get_team_goal
from domain.user.user_crud import get_current_user
from models import User

router = APIRouter(
    prefix="/team_goal",
    tags=["Team Goal"]
)


@router.put("/complete", status_code=status.HTTP_204_NO_CONTENT)
def complete_weekly(challenge_user_no: int,
                    db: Session = Depends(get_db),
                    _current_user: User = Depends(get_current_user)):
    db_team_goal = get_team_goal(db, challenge_user_no)
    _challenge_user = get_challenge_user_by_challenge_user_no(db, challenge_user_no)

    if db_team_goal.IS_DONE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="이미 완료된 팀 목표입니다.")
    elif _current_user.USER_NO != _challenge_user.USER_NO:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="챌린지 완료 권한이 없습니다.")

    weekly_crud.complete_weekly_goal(db, db_team_goal=db_team_goal)
