from boto3 import Session
from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from database import get_db
from domain.challenge.challenge_crud import get_challenge
from domain.challenge.daily import daily_schema, daily_crud
from domain.user.user_router import get_current_user
from models import User

router = APIRouter(
    prefix="/challenge",
    tags=["challenge"]
)


@router.post("/create/todo_item", status_code=status.HTTP_204_NO_CONTENT)
def create_todo_item(_create_todo: daily_schema.CreateTodoItem,
                     db: Session = Depends(get_db),
                     _current_user: User = Depends(get_current_user)):
    _current_challenge = get_challenge(db, challenge_no=_create_todo.CHALLENGE_MST_NO)
    daily_crud.create_todo_item(db, create_todo=_create_todo,
                                current_user=_current_user,
                                current_challenge=_current_challenge)


@router.get("/todo_item/{person_goal_no}", response_model=daily_schema.GetTodoItem)
def get_todo_item(person_goal_no: int, db: Session = Depends(get_db)):
    person_goal = daily_crud.get_todo_item(db=db, person_goal_no=person_goal_no)
    if not person_goal:
        raise HTTPException(status_code=404, detail="해당 개인 목표를 찾을 수 없습니다.")
    return person_goal


@router.put("/update/todo_item/{person_goal_no}", status_code=status.HTTP_204_NO_CONTENT)
def update_todo_item(_update_todo: daily_schema.UpdateTodoItem,
                     db: Session = Depends(get_db),
                     _current_user: User = Depends(get_current_user)):
    db_person_goal = daily_crud.get_todo_item(db, person_goal_no=_update_todo.PERSON_GOAL_NO)
    if _current_user.USER_NO != db_person_goal.USER_ID:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="수정 권한이 없습니다.")
    daily_crud.update_todo_item(db=db, db_person_goal=db_person_goal,
                                  person_goal_update=_update_todo)


@router.delete("/delete/todo_item", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo_item(_delete_todo: daily_schema.DeleteTodoItem,
                     db: Session = Depends(get_db),
                     _current_user: User = Depends(get_current_user)):
    db_person_goal = daily_crud.get_todo_item(db, person_goal_no=_delete_todo.PERSON_GOAL_NO)
    if _current_user.USER_NO != db_person_goal.USER_ID:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="삭제 권한이 없습니다.")
    daily_crud.delete_todo_item(db=db, db_person_goal=db_person_goal)


@router.post("/complete/daily", status_code=status.HTTP_204_NO_CONTENT)
def complete_daily(_complete_daily: daily_schema.CompleteDailyGoal,
                   db: Session = Depends(get_db),
                   _current_user: User = Depends(get_current_user)):
    _challenge = get_challenge(db, challenge_no=_complete_daily.CHALLENGE_MST_NO)
    daily_crud.complete_daily_goal(db, complete_daily=_complete_daily,
                                   current_challenge=_challenge,
                                   current_user=_current_user)
