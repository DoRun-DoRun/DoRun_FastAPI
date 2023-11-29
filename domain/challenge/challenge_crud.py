from datetime import timedelta
import random
from typing import Dict, Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from domain.challenge.challenge_schema import ChallengeCreate, ChallengeParticipant, Challenge, PersonDailyGoalPydantic, \
    TeamWeeklyGoalPydantic, AdditionalGoalPydantic
from domain.desc.utils import calculate_progress
from domain.user.user_crud import get_user
from models import ChallengeMaster, User, TeamWeeklyGoal, ChallengeUser, PersonDailyGoal, AdditionalGoal


def get_challenge_list(db: Session, current_user: User):
    challenges = db.query(ChallengeMaster). \
        join(ChallengeUser, ChallengeUser.CHALLENGE_MST_NO == ChallengeMaster.CHALLENGE_MST_NO). \
        filter(ChallengeUser.USER_NO == current_user.USER_NO).all()

    if not challenges:
        return []

    challenge_list = []
    for challenge in challenges:
        participants = get_challenge_participants(db, challenge.CHALLENGE_MST_NO)

        challenge_info = Challenge.model_validate(challenge)
        challenge_info.PROGRESS = calculate_progress(challenge.START_DT, challenge.END_DT)
        challenge_info.PARTICIPANTS = [
            ChallengeParticipant(UID=participant.UID, ACCEPT_STATUS=participant.ACCEPT_STATUS)
            for participant in participants
        ]
        challenge_list.append(challenge_info)

    return challenge_list


def get_challenge_detail(db: Session, user_no: int, challenge_mst_no: int) -> Dict[str, Any]:
    # ChallengeUser 정보 검색
    challenge_user = db.query(ChallengeUser).filter(
        ChallengeUser.USER_NO == user_no,
        ChallengeUser.CHALLENGE_MST_NO == challenge_mst_no
    ).first()

    if not challenge_user:
        raise HTTPException(status_code=404, detail="challenge_user not found")

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

    # additional_goals 목록 검색
    additional_goals = db.query(AdditionalGoal).join(
        ChallengeUser,
        ChallengeUser.CHALLENGE_USER_NO == AdditionalGoal.CHALLENGE_USER_NO
    ).filter(
        ChallengeUser.CHALLENGE_MST_NO == challenge_master.CHALLENGE_MST_NO
    ).all()

    # Pydantic 모델을 사용하여 결과 구조화
    return {
        "CHALLENGE_USER_NO": challenge_user.CHALLENGE_USER_NO,
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


def get_challenge_master_by_id(db: Session, challenge_mst_no: int) -> ChallengeMaster:
    challenge = db.query(ChallengeMaster).filter(ChallengeMaster.CHALLENGE_MST_NO == challenge_mst_no).first()

    if not challenge:
        raise HTTPException(status_code=404, detail="ChallengeMaster not found")

    return challenge


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
