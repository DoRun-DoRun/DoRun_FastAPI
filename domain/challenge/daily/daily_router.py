from boto3 import Session
from fastapi import APIRouter, Depends
from starlette import status

from database import get_db
from domain.challenge.challenge_crud import get_challenge
from domain.challenge.daily import daily_schema, daily_crud
from domain.user.user_crud import get_current_user
from models import User

router = APIRouter(
    prefix="/challenge",
    tags=["challenge"]
)


@router.post("/complete/daily", status_code=status.HTTP_204_NO_CONTENT)
def complete_daily(_complete_daily: daily_schema.CompleteDailyGoal,
                   db: Session = Depends(get_db),
                   _current_user: User = Depends(get_current_user)):
    _challenge = get_challenge(db, challenge_no=_complete_daily.CHALLENGE_MST_NO)
    daily_crud.complete_daily_goal(db, complete_daily=_complete_daily,
                                   current_challenge=_challenge,
                                   current_user=_current_user)
