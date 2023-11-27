from datetime import datetime, timedelta
import random

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from domain.challenge import challenge_schema
from domain.challenge.challenge_schema import ChallengeCreate
from domain.challenge.daily.daily_schema import CompleteDailyGoal
from domain.user import user_crud
from domain.user.user_crud import get_user
from models import ChallengeMaster, User, PersonDailyGoalComplete, TeamWeeklyGoal, Challenge_User, PersonDailyGoal


def get_challenge_list(current_user: User):
    challenges = current_user.Challenge_User  # 현재 사용자가 참가하고 있는 챌린지 목록

    if not challenges:
        return

    # 챌린지 객체들을 Challenge 스키마로 변환
    _challenge_list = []
    for challenge in challenges:
        challenge_data = {
            "CHALLENGE_MST_NO": challenge.CHALLENGE_MST_NO,
            "CHALLENGE_MST_NM": challenge.CHALLENGE_MST_NM,
            "USERS_UID": [user.UID for user in challenge.MEMBER],
            "START_DT": challenge.START_DT,
            "END_DT": challenge.END_DT,
            "HEADER_EMOJI": challenge.HEADER_EMOJI,
            "CHALLENGE_STATUS": challenge.CHALLENGE_STATUS,
            "USER_UID": challenge.USER.UID
        }
        _challenge_list.append(challenge_schema.Challenge(**challenge_data))
    return _challenge_list


def get_challenge_detail(db: Session, challenge_no: int):
    challenge = get_challenge(db, challenge_no)

    return challenge_schema.Challenge(
        CHALLENGE_MST_NO=challenge.CHALLENGE_MST_NO,
        CHALLENGE_MST_NM=challenge.CHALLENGE_MST_NM,
        USERS_UID=[user.UID for user in challenge.MEMBER],
        START_DT=challenge.START_DT,
        END_DT=challenge.END_DT,
        HEADER_EMOJI=challenge.HEADER_EMOJI,
        INSERT_DT=challenge.INSERT_DT,
        CHALLENGE_STATUS=challenge.CHALLENGE_STATUS,
        USER_UID=challenge.USER.UID
    )


def get_challenge(db: Session, challenge_no: int):
    _challenge = db.query(ChallengeMaster).filter(ChallengeMaster.CHALLENGE_MST_NO == challenge_no).first()
    if not (_challenge):
        raise HTTPException(status_code=404, detail="Challenge not found")
    return _challenge

def create_challenge(db: Session, challenge_create: ChallengeCreate, current_user: User):
    db_challenge = ChallengeMaster(
        CHALLENGE_MST_NM=challenge_create.CHALLENGE_MST_NM,
        START_DT=challenge_create.START_DT,
        END_DT=challenge_create.END_DT,
        HEADER_EMOJI=challenge_create.HEADER_EMOJI,
        CHALLENGE_STATUS=challenge_create.CHALLENGE_STATUS,
        USER=current_user
    )
    db.add(db_challenge)
    db.commit()

    # USERS_UID를 기반으로 챌린지에 참여중인 유저를 가져옴
    for uid in challenge_create.USERS_UID:
        user = get_user(db, uid)
        team_leader = get_user(db, uid=random.choice(challenge_create.USERS_UID))
        if user:
            user.Challenge_User.append(db_challenge)
            db_team = TeamWeeklyGoal(
                USER=user,
                LEADER=team_leader,
                CHALLENGE=db_challenge,
                START_DT=challenge_create.START_DT,
                END_DT=challenge_create.START_DT + timedelta(days=7),
            )
            db.add(db_team)
            db.commit()

