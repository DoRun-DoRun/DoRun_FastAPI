from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.challenge.challenge_crud import get_challenge_user_by_challenge_user_no
from domain.challenge.diary import diary_schema, diary_crud
from domain.user.user_crud import get_current_user
from models import User, DailyCompleteUser, PersonDailyGoalComplete, ChallengeUser

router = APIRouter(
    prefix="/diary",
    tags=["Diary"]
)


@router.post("/{daily_complete_no}")
def post_emoji(daily_complete_no: int, emoji: str, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    diary = db.query(PersonDailyGoalComplete).filter_by(DAILY_COMPLETE_NO=daily_complete_no).first()

    if not diary:
        raise HTTPException(status_code=404, detail="Diary를 찾을 수 없습니다")

    challenge_user = db.query(ChallengeUser).filter_by(
        CHALLENGE_USER_NO=diary.CHALLENGE_USER_NO,
        USER_NO=current_user.USER_NO
    ).first()

    db_emoji = DailyCompleteUser(EMOJI=emoji, DAILY_COMPLETE_NO=daily_complete_no, CHALLENGE_USER=challenge_user)
    db.add(db_emoji)

    db.commit()

    return {"message": "이모지 전송 성공"}


@router.get("/{daily_complete_no}")
def get_diary(daily_complete_no: int, db: Session = Depends(get_db)):
    diary = db.query(PersonDailyGoalComplete).filter(
        daily_complete_no == PersonDailyGoalComplete.DAILY_COMPLETE_NO).first()

    if not diary:
        raise HTTPException(status_code=404, detail="Diary를 찾을 수 없습니다")

    return diary


@router.post("/complete/all", status_code=status.HTTP_204_NO_CONTENT)
def complete_daily(_complete_daily: diary_schema.CompleteDailyGoalAll,
                   db: Session = Depends(get_db),
                   _current_user: User = Depends(get_current_user)):
    db_person_goal_complete = diary_crud.get_person_goal_complete(db, _complete_daily.CHALLENGE_USER_NO)
    _challenge_user = get_challenge_user_by_challenge_user_no(db, _complete_daily.CHALLENGE_USER_NO)

    if db_person_goal_complete:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="이미 완료된 개인 목표입니다.")
    elif _current_user.USER_NO != _challenge_user.USER_NO:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="완료 권한이 없습니다.")

    diary_crud.complete_daily_goal(db, complete_daily=_complete_daily)
