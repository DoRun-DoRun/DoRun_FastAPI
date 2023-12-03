from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from domain.challenge.daily.daily_schema import CreatePersonGoal, UpdatePersonGoal, CompleteDailyGoalAll
from models import User, ChallengeMaster, PersonDailyGoalComplete, PersonDailyGoal


def create_person_goal(db: Session,
                       create_todo: CreatePersonGoal):
    db_person_goal = PersonDailyGoal(
        PERSON_NM=create_todo.PERSON_NM,
        CHALLENGE_USER_NO=create_todo.CHALLENGE_USER_NO
    )
    db.add(db_person_goal)
    db.commit()


def get_person_goal(db: Session, person_no: int):
    person_goal = db.query(PersonDailyGoal).filter(PersonDailyGoal.PERSON_NO == person_no).first()
    return person_goal


def update_person_goal(db: Session,
                       db_person_goal: PersonDailyGoal,
                       person_goal_update: UpdatePersonGoal):
    db_person_goal.PERSON_NM = person_goal_update.PERSON_NM
    db_person_goal.IS_DONE = person_goal_update.IS_DONE
    db.add(db_person_goal)
    db.commit()


def delete_person_goal(db: Session,
                       db_person_goal: PersonDailyGoal):
    db.delete(db_person_goal)
    db.commit()


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
