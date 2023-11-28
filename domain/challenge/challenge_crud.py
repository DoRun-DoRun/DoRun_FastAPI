from datetime import datetime, timedelta
import random
from typing import Dict, Any

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from domain.challenge import challenge_schema
from domain.challenge.challenge_schema import ChallengeCreate, ChallengeParticipant, Challenge, PersonDailyGoalPydantic, \
    TeamWeeklyGoalPydantic, AdditionalGoalPydantic
from domain.challenge.daily.daily_schema import CompleteDailyGoal
from domain.user import user_crud
from domain.user.user_crud import get_user
from models import ChallengeMaster, User, PersonDailyGoalComplete, TeamWeeklyGoal, ChallengeUser, PersonDailyGoal, \
    AdditionalGoal


def get_challenge_list(db: Session, current_user: User):
    challenges = get_user_challenges(db, current_user.USER_NO)  # 현재 사용자가 참가하고 있는 챌린지 목록
    if not challenges:
        return

    # 챌린지 객체들을 Challenge 스키마로 변환
    _challenge_list = []
    for challenge in challenges:
        progress = calculate_progress(challenge.START_DT, challenge.END_DT)

        challenge_data = {
            "CHALLENGE_MST_NO": challenge.CHALLENGE_MST_NO,
            "CHALLENGE_MST_NM": challenge.CHALLENGE_MST_NM,
            "START_DT": challenge.START_DT,
            "END_DT": challenge.END_DT,
            "HEADER_EMOJI": challenge.HEADER_EMOJI,
            "CHALLENGE_STATUS": challenge.CHALLENGE_STATUS,
            "PROGRESS": progress
        }
        _challenge_list.append(challenge_schema.ChallengeAll(**challenge_data))
    return _challenge_list


def calculate_progress(start_dt, end_dt):
    total_days = (end_dt - start_dt).days + 1
    elapsed_days = (datetime.utcnow().date() - start_dt).days
    return min(max(elapsed_days / total_days * 100, 0), 100)  # 0에서 100 사이의 값을 반환


def get_challenge_pending(db: Session, challenge_no: int):
    challenge = get_challenge_by_id(db, challenge_no)

    if not challenge:
        return None  # 챌린지가 존재하지 않으면 None 반환

    participants_data = get_challenge_participants(db, challenge.CHALLENGE_MST_NO)
    participants = [ChallengeParticipant(UID=participant.UID, ACCEPT_STATUS=participant.ACCEPT_STATUS)
                    for participant in participants_data]
    return challenge_schema.ChallengePending(
        CHALLENGE_MST_NO=challenge.CHALLENGE_MST_NO,
        CHALLENGE_MST_NM=challenge.CHALLENGE_MST_NM,
        START_DT=challenge.START_DT,
        END_DT=challenge.END_DT,
        HEADER_EMOJI=challenge.HEADER_EMOJI,
        CHALLENGE_STATUS=challenge.CHALLENGE_STATUS,
        PARTICIPANTS=participants
    )


def get_challenge_detail(db: Session, user_no: int, challenge_mst_no: int) -> Dict[str, Any]:
    # ChallengeUser 정보 검색
    challenge_user = db.query(ChallengeUser).filter(
        ChallengeUser.USER_NO == user_no,
        ChallengeUser.CHALLENGE_MST_NO == challenge_mst_no
    ).first()

    # 해당 ChallengeUser가 존재하지 않으면 None 반환
    if not challenge_user:
        return None

    # ChallengeMaster 정보 검색
    challenge_master = db.query(ChallengeMaster).filter(
        ChallengeMaster.CHALLENGE_MST_NO == challenge_user.CHALLENGE_MST_NO).first()

    # PersonDailyGoal 목록 검색
    person_goals = db.query(PersonDailyGoal).filter(
        PersonDailyGoal.CHALLENGE_USER_NO == challenge_user.CHALLENGE_USER_NO).all()

    # TeamWeeklyGoal 목록 검색
    team_goals = db.query(TeamWeeklyGoal).join(
        ChallengeUser,
        ChallengeUser.CHALLENGE_USER_NO == TeamWeeklyGoal.CHALLENGE_USER_NO
    ).filter(
        ChallengeUser.CHALLENGE_MST_NO == challenge_master.CHALLENGE_MST_NO
    ).all()

    additional_goals = db.query(AdditionalGoal).join(
        ChallengeUser,
        ChallengeUser.CHALLENGE_USER_NO == AdditionalGoal.CHALLENGE_USER_NO
    ).filter(
        ChallengeUser.CHALLENGE_MST_NO == challenge_master.CHALLENGE_MST_NO
    ).all()

    # Pydantic 모델을 사용하여 결과 구조화
    return {
        "challenge": Challenge.model_validate(challenge_master),
        "personGoal": [PersonDailyGoalPydantic.model_validate(goal) for goal in person_goals],
        "teamGoal": [TeamWeeklyGoalPydantic.model_validate(goal) for goal in team_goals],
        "additionalGoal": [AdditionalGoalPydantic.model_validate(goal) for goal in additional_goals]
    }


def get_challenge_participants(db: Session, challenge_id):
    participants = db.query(
        User.UID,
        ChallengeUser.ACCEPT_STATUS
    ).join(
        ChallengeUser, User.USER_NO == ChallengeUser.USER_NO
    ).filter(
        ChallengeUser.CHALLENGE_MST_NO == challenge_id
    ).all()

    return participants


def get_challenge_by_id(db: Session, challenge_mst_no: int) -> ChallengeMaster:
    # 주어진 챌린지 번호로 챌린지 조회
    challenge = db.query(ChallengeMaster).filter(ChallengeMaster.CHALLENGE_MST_NO == challenge_mst_no).first()
    return challenge


def get_user_challenges(db: Session, user_no: int) -> list:
    # User 모델을 통해 해당 사용자가 참여하고 있는 챌린지를 조회
    challenges = db.query(ChallengeMaster). \
        join(ChallengeUser, ChallengeUser.CHALLENGE_MST_NO == ChallengeMaster.CHALLENGE_MST_NO). \
        filter(ChallengeUser.USER_NO == user_no).all()
    return challenges


def get_challenge_users(challenge_mst_no: int, db: Session) -> list:
    # ChallengeMaster 모델을 통해 해당 챌린지에 참여하는 모든 유저를 조회
    users = db.query(User). \
        join(ChallengeUser, ChallengeUser.USER_NO == User.USER_NO). \
        filter(ChallengeUser.CHALLENGE_MST_NO == challenge_mst_no).all()
    return users


def create_challenge(db: Session, challenge_create: ChallengeCreate, current_user: User):
    db_challenge = ChallengeMaster(
        CHALLENGE_MST_NM=challenge_create.CHALLENGE_MST_NM,
        START_DT=challenge_create.START_DT,
        END_DT=challenge_create.END_DT,
        HEADER_EMOJI=challenge_create.HEADER_EMOJI,
        CHALLENGE_STATUS=challenge_create.CHALLENGE_STATUS,
    )
    db.add(db_challenge)
    db.commit()

    # USERS_UID를 기반으로 챌린지에 참여중인 유저를 가져옴
    for uid in challenge_create.USERS_UID:
        user = get_user(db, uid)
        team_leader = get_user(db, uid=random.choice(challenge_create.USERS_UID))
        if user:
            db_challenge_user = ChallengeUser(
                CHALLENGE_MST=db_challenge,
                USER=user,
                IS_OWNER=current_user == user if True else False,
                IS_LEADER=team_leader == user if True else False,
            )
            db.add(db_challenge_user)

            db_team = TeamWeeklyGoal(
                CHALLENGE_USER=db_challenge_user,
                START_DT=challenge_create.START_DT,
                END_DT=challenge_create.START_DT + timedelta(days=7),
            )
            db.add(db_team)
            db.commit()

# def calculate_challenge_progress(db: Session, challenge_id):
#     # 챌린지 기간 가져오기
#     challenge = db.query(ChallengeMaster).filter(ChallengeMaster.CHALLENGE_MST_NO == challenge_id).one()
#     total_days = (challenge.END_DT - challenge.START_DT).days + 1
#
#     # 각 날짜별 완료된 PersonDailyGoal 수집
#     daily_goals_count = db.query(
#         func.date(PersonDailyGoal.INSERT_DT),
#         func.count(PersonDailyGoal.PERSON_NO)
#     ).filter(
#         PersonDailyGoal.CHALLENGE_USER_NO == challenge_id,
#         PersonDailyGoal.IS_DONE == True
#     ).group_by(
#         func.date(PersonDailyGoal.INSERT_DT)
#     ).all()
#
#     # 진행도 계산
#     progress = sum((100 / total_days) * (1 / count) for _, count in daily_goals_count)
#
#     return progress
