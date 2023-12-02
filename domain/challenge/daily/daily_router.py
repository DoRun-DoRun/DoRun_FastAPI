from boto3 import Session
from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from database import get_db
from domain.challenge.challenge_crud import get_challenge_master_by_id, get_challenge_detail, \
    get_challenge_masters_by_user, get_challenge_users_by_mst_no, get_challenge_user_by_user_no
from domain.challenge.daily import daily_schema, daily_crud
from domain.challenge.daily.daily_crud import get_challenge_user_by_challenge_user
from domain.user.user_router import get_current_user
from models import User

router = APIRouter(
    prefix="/person_goal",
    tags=["person_goal"]
)


@router.post("", status_code=status.HTTP_204_NO_CONTENT)
def create_person_goal(_create_todo: daily_schema.CreatePersonGoal,
                       db: Session = Depends(get_db)):
    daily_crud.create_person_goal(db, create_todo=_create_todo)


@router.put("", status_code=status.HTTP_204_NO_CONTENT)
def update_person_goal(_update_todo: daily_schema.UpdatePersonGoal,
                       db: Session = Depends(get_db),
                       _current_user: User = Depends(get_current_user)):
    db_person_goal = daily_crud.get_person_goal(db, person_no=_update_todo.PERSON_NO)
    _challenge_user = get_challenge_user_by_challenge_user(db, db_person_goal.CHALLENGE_USER_NO)
    if _current_user.USER_NO != _challenge_user.USER_NO:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="수정 권한이 없습니다.")
    daily_crud.update_person_goal(db=db, db_person_goal=db_person_goal,
                                  person_goal_update=_update_todo)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_person_goal(person_no: int,
                       db: Session = Depends(get_db),
                       _current_user: User = Depends(get_current_user)):
    db_person_goal = daily_crud.get_person_goal(db, person_no=person_no)
    _challenge_user = get_challenge_user_by_challenge_user(db, db_person_goal.CHALLENGE_USER_NO)
    if _current_user.USER_NO != _challenge_user.USER_NO:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="삭제 권한이 없습니다.")
    daily_crud.delete_person_goal(db=db, db_person_goal=db_person_goal)


@router.post("/complete/all", status_code=status.HTTP_204_NO_CONTENT)
def complete_daily(_complete_daily: daily_schema.CompleteDailyGoal,
                   db: Session = Depends(get_db),
                   _current_user: User = Depends(get_current_user)):
    _challenge = get_challenge_master_by_id(db, _complete_daily.CHALLENGE_MST_NO)
    daily_crud.complete_daily_goal(db, complete_daily=_complete_daily,
                                   current_challenge=_challenge,
                                   current_user=_current_user)
