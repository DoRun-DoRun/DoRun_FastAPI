from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from domain.challenge.daily.daily_schema import CompleteDailyGoal, CreatePersonGoal, GetPersonGoal, UpdatePersonGoal
from models import User, ChallengeMaster, PersonDailyGoalComplete, PersonDailyGoal


def create_person_goal(db: Session,
                     create_todo: CreatePersonGoal,
                     current_user: User,
                     current_challenge: ChallengeMaster):
    db_person_goal = PersonDailyGoal(
        PERSON_GOAL_NM=create_todo.PERSON_GOAL_NM,
        CHALLENGE=current_challenge,
        USER=current_user,
    )
    db.add(db_person_goal)
    db.commit()


def get_person_goal(db: Session, person_goal_no: int):
    person_goal = db.query(PersonDailyGoal).filter(PersonDailyGoal.PERSON_GOAL_NO == person_goal_no).first()
    return person_goal


def update_person_goal(db: Session,
                     db_person_goal: PersonDailyGoal,
                     person_goal_update: UpdatePersonGoal):
    db_person_goal.PERSON_GOAL_NM = person_goal_update.PERSON_GOAL_NM
    db_person_goal.IS_DONE = person_goal_update.IS_DONE
    db.add(db_person_goal)
    db.commit()


def delete_person_goal(db: Session,
                     db_person_goal: PersonDailyGoal):
    db.delete(db_person_goal)
    db.commit()


def complete_daily_goal(db: Session,
                        complete_daily: CompleteDailyGoal,
                        current_user: User,
                        current_challenge: ChallengeMaster):
    db_daily = PersonDailyGoalComplete(
        AUTH_IMAGE_FILE_NM=complete_daily.AUTH_IMAGE_FILE_NM,
        COMMENTS=complete_daily.COMMENTS,

    )
    db.add(db_daily)
    db.commit()
