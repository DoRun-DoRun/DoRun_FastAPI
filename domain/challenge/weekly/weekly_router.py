from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.challenge.challenge_crud import get_challenge_master_by_id
from domain.challenge.weekly import weekly_crud
from domain.user.user_crud import get_current_user
from models import User

router = APIRouter(
    prefix="/team_goal",
    tags=["Team Goal"]
)


@router.put("/complete/weekly/{challenge_mst_no}", status_code=status.HTTP_204_NO_CONTENT)
def complete_weekly(challenge_mst_no: int, db: Session = Depends(get_db),
                    _current_user: User = Depends(get_current_user)):
    # 챌린지 정보를 가져옵니다.
    _challenge = get_challenge_master_by_id(db, challenge_no=challenge_mst_no)

    if not weekly_crud.complete_weekly_goal(db, current_challenge=_challenge, current_user=_current_user):
        raise HTTPException(status_code=404, detail="TEAM GOAL not found")
