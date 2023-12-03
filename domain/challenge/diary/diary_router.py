from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
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
