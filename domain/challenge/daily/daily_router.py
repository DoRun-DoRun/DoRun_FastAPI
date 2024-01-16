from boto3 import Session
from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from database import get_db
from domain.challenge.challenge_crud import get_challenge_master_by_id, get_challenge_user_by_challenge_user_no
from domain.challenge.daily import daily_schema, daily_crud
from domain.user.user_router import get_current_user
from models import User

router = APIRouter(
    prefix="/person_goal",
    tags=["person_goal"]
)


@router.post("", status_code=status.HTTP_204_NO_CONTENT)
def create_person_goal(_create_todo: daily_schema.CreatePersonGoal,
                       db: Session = Depends(get_db),
                       _current_user: User = Depends(get_current_user)):
    _challenge_user = get_challenge_user_by_challenge_user_no(db, _create_todo.CHALLENGE_USER_NO)

    if _current_user.USER_NO != _challenge_user.USER_NO:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="생성 권한이 없습니다.")

    daily_crud.create_person_goal(db, create_todo=_create_todo)


@router.put("", status_code=status.HTTP_204_NO_CONTENT)
def update_person_goal(_update_todo: daily_schema.UpdatePersonGoal,
                       db: Session = Depends(get_db),
                       _current_user: User = Depends(get_current_user)):
    db_person_goal = daily_crud.get_person_goal(db, person_no=_update_todo.PERSON_NO)
    _challenge_user = get_challenge_user_by_challenge_user_no(db, db_person_goal.CHALLENGE_USER_NO)

    if _current_user.USER_NO != _challenge_user.USER_NO:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="수정 권한이 없습니다.").update_person_goal(db=db, db_person_goal=db_person_goal,
                                  person_goal_update=_update_todo)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_person_goal(person_no: int,
                       db: Session = Depends(get_db),
                       _current_user: User = Depends(get_current_user)):
    db_person_goal = daily_crud.get_person_goal(db, person_no=person_no)
    _challenge_user = get_challenge_user_by_challenge_user_no(db, db_person_goal.CHALLENGE_USER_NO)

    if _current_user.USER_NO != _challenge_user.USER_NO:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="삭제 권한이 없습니다.")

    daily_crud.delete_person_goal(db=db, db_person_goal=db_person_goal)


@router.post("/complete/all", status_code=status.HTTP_204_NO_CONTENT)
def complete_daily(_complete_daily: daily_schema.CompleteDailyGoalAll,
                   db: Session = Depends(get_db),
                   _current_user: User = Depends(get_current_user)):
    db_person_goal_complete = daily_crud.get_person_goal_complete(db, _complete_daily.CHALLENGE_USER_NO)
    _challenge_user = get_challenge_user_by_challenge_user_no(db, _complete_daily.CHALLENGE_USER_NO)

    if db_person_goal_complete:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="이미 완료된 개인 목표입니다.")
    elif _current_user.USER_NO != _challenge_user.USER_NO:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="완료 권한이 없습니다.")

    daily_crud.complete_daily_goal(db, complete_daily=_complete_daily)
