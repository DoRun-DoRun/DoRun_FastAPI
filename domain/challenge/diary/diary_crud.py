from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from domain.challenge.daily.daily_schema import CreatePersonGoal, UpdatePersonGoal, CompleteDailyGoalAll
from models import User, ChallengeMaster, PersonDailyGoalComplete, PersonDailyGoal


# 완성된 개인 목표 조회
def get_person_goal_complete(db: Session, challenge_user_no: int):
    person_goal_complete = db.query(PersonDailyGoalComplete).filter(
        PersonDailyGoalComplete.CHALLENGE_USER_NO == challenge_user_no).first()
    return person_goal_complete


def complete_daily_goal(db: Session,
                        complete_daily: CompleteDailyGoalAll):
    db_daily = PersonDailyGoalComplete(
        CHALLENGE_USER_NO=complete_daily.CHALLENGE_USER_NO,
        IMAGE_FILE_NM=complete_daily.IMAGE_FILE_NM,
        COMMENTS=complete_daily.COMMENTS
    )
    db.add(db_daily)
    db.commit()
