from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import PersonDailyGoalComplete


def get_diary(db: Session, daily_complete_no: int):
    diary = db.query(PersonDailyGoalComplete).filter(
        daily_complete_no == PersonDailyGoalComplete.DAILY_COMPLETE_NO).first()

    if not diary:
        raise HTTPException(status_code=404, detail="Diary를 찾을 수 없습니다")

    return diary

# def get_dairy_by_challenge_user(db: Session)
