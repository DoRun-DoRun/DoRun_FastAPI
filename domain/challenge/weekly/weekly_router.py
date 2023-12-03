from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.challenge.challenge_crud import get_challenge_master_by_id, get_challenge_user_by_challenge_user_no
from domain.challenge.weekly import weekly_crud, weekly_schema
from domain.challenge.weekly.weekly_crud import get_team_goal
from domain.user.user_crud import get_current_user
from models import User

router = APIRouter(
    prefix="/team_goal",
    tags=["Team Goal"]
)


@router.put("", status_code=status.HTTP_204_NO_CONTENT)
def update_weekly_goal(_update_weekly_goal: weekly_schema.UpdateWeeklyGoal,
                       db: Session = Depends(get_db),
                       _current_user: User = Depends(get_current_user)):
    db_team_goal = get_team_goal(db, team_no=_update_weekly_goal.TEAM_NO)
    _challenge_user = get_challenge_user_by_challenge_user_no(db, db_team_goal.CHALLENGE_USER_NO)

    if db_team_goal.IS_DONE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="이미 완료된 팀 목표는 수정할 수 없습니다.")
    elif _current_user.USER_NO != _challenge_user.USER_NO:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="수정 권한이 없습니다.")

    weekly_crud.update_weekly_goal(db, db_team_goal=db_team_goal,
                                   weekly_team_goal_update=_update_weekly_goal)
