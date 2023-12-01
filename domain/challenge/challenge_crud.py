from datetime import datetime, timedelta
import random
from typing import Dict, Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from domain.challenge.challenge_schema import ChallengeCreate, ChallengeParticipant, Challenge, PersonDailyGoalPydantic, \
    TeamWeeklyGoalPydantic, AdditionalGoalPydantic, ChallengeList, ChallengeListPydantic, ChallengeInvite, \
    ChallengeUserList
from domain.desc.utils import calculate_progress
from domain.user.user_crud import get_user_by_uid
from models import ChallengeMaster, User, TeamWeeklyGoal, ChallengeUser, PersonDailyGoal, AdditionalGoal, ItemUser, \
    Item, InviteAcceptType, Avatar, AvatarUser


def get_challenge_list(db: Session, current_user: User):
    challenges = get_challenge_masters_by_user(db, current_user)

    if not challenges:
        return []

    challenge_list = []
    for challenge in challenges:
        challenge_info = ChallengeList.model_validate(challenge)
        challenge_info.PROGRESS = calculate_progress(challenge.START_DT, challenge.END_DT)

        challenge_list.append(challenge_info)

    return challenge_list


def get_challenge_masters_by_user(db: Session, current_user: User) -> ChallengeMaster:
    challenges = db.query(ChallengeMaster). \
        join(ChallengeUser, ChallengeUser.CHALLENGE_MST_NO == ChallengeMaster.CHALLENGE_MST_NO). \
        filter(ChallengeUser.USER_NO == current_user.USER_NO).all()

    if not challenges:
        raise HTTPException(status_code=404, detail="챌린지를 찾을 수 없습니다.")

    return challenges


def get_challenge_user_by_no(db: Session, challenge_mst_no, user_no=None):
    if user_no:
        challenge_user = db.query(ChallengeUser).filter(
            ChallengeUser.USER_NO == user_no,
            ChallengeUser.CHALLENGE_MST_NO == challenge_mst_no
        ).first()

        if not challenge_user:
            raise HTTPException(status_code=404, detail="특정 사용자에 대한 challenge_user를 찾을 수 없습니다.")
    else:
        challenge_user = db.query(ChallengeUser).filter(
            ChallengeUser.CHALLENGE_MST_NO == challenge_mst_no
        ).all()

        if not challenge_user:
            raise HTTPException(status_code=404, detail="challenge_user를 찾을 수 없습니다.")

    return challenge_user


def get_challenge_detail(db: Session, user_no: int, challenge_mst_no: int, current_day: datetime) -> Dict[str, Any]:
    # ChallengeUser 정보 검색
    challenge_user = get_challenge_user_by_no(db, challenge_mst_no, user_no)

    # PersonDailyGoal 목록 검색
    person_goals = db.query(PersonDailyGoal).filter(
        PersonDailyGoal.CHALLENGE_USER_NO == challenge_user.CHALLENGE_USER_NO,
        PersonDailyGoal.INSERT_DT >= current_day,
        PersonDailyGoal.INSERT_DT <= current_day + timedelta(days=1)
    ).all()

    # 현재 UTC 시간 가져오기
    current_utc_time = datetime.utcnow()

    # TeamWeeklyGoal 목록 검색 및 필터링
    team_goals = db.query(TeamWeeklyGoal).join(
        ChallengeUser,
        ChallengeUser.CHALLENGE_USER_NO == TeamWeeklyGoal.CHALLENGE_USER_NO
    ).filter(
        ChallengeUser.CHALLENGE_MST_NO == challenge_mst_no,
        TeamWeeklyGoal.START_DT <= current_utc_time,  # 현재 시간 이후로 시작하는 것을 포함
        TeamWeeklyGoal.END_DT >= current_utc_time  # 현재 시간 이전에 종료하는 것을 배제
    ).all()

    if not team_goals:
        raise HTTPException(status_code=404, detail="팀 목표를 찾을 수 없습니다.")

    # additional_goals 목록 검색
    additional_goals = db.query(AdditionalGoal).join(
        ChallengeUser,
        ChallengeUser.CHALLENGE_USER_NO == AdditionalGoal.CHALLENGE_USER_NO
    ).filter(
        ChallengeUser.CHALLENGE_MST_NO == challenge_mst_no,
        AdditionalGoal.START_DT <= current_utc_time,  # 현재 시간 이후로 시작하는 것을 포함
        AdditionalGoal.END_DT >= current_utc_time  # 현재 시간 이전에 종료하는 것을 배제
    ).all()

    # Pydantic 모델을 사용하여 결과 구조화
    return {
        "CHALLENGE_USER_NO": challenge_user.CHALLENGE_USER_NO,
        "personGoal": [PersonDailyGoalPydantic.model_validate(goal) for goal in person_goals],
        "teamGoal": [TeamWeeklyGoalPydantic.model_validate(goal) for goal in team_goals],
        "additionalGoal": [AdditionalGoalPydantic.model_validate(goal) for goal in additional_goals]
    }


def get_challenge_participants(db: Session, challenge_id):
    participants = db.query(
        User,
        ChallengeUser.ACCEPT_STATUS
    ).join(
        ChallengeUser, User.USER_NO == ChallengeUser.USER_NO
    ).filter(
        ChallengeUser.CHALLENGE_MST_NO == challenge_id
    ).all()

    if not participants:
        raise HTTPException(status_code=404, detail="참가자를 찾을 수 없습니다.")

    return participants


def get_challenge_invite(db: Session, challenge_mst_no: int):
    _challenge = get_challenge_master_by_id(db, challenge_mst_no)

    # SQLAlchemy 모델 객체에서 필요한 필드만 추출
    challenge_data = {
        'CHALLENGE_MST_NO': _challenge.CHALLENGE_MST_NO,
        'CHALLENGE_MST_NM': _challenge.CHALLENGE_MST_NM,
        'START_DT': _challenge.START_DT,
        'END_DT': _challenge.END_DT,
        'HEADER_EMOJI': _challenge.HEADER_EMOJI,
        'CHALLENGE_STATUS': _challenge.CHALLENGE_STATUS
    }

    participants = get_challenge_participants(db, challenge_mst_no)
    participants_list = [
        ChallengeParticipant(
            UID=participant.User.UID,
            USER_NM=participant.User.USER_NM,
            ACCEPT_STATUS=participant.ACCEPT_STATUS
        ) for participant in participants
    ]

    challenge_info = ChallengeInvite(
        **challenge_data,
        PARTICIPANTS=participants_list
    )

    return challenge_info


def get_challenge_master_by_id(db: Session, challenge_mst_no: int) -> ChallengeMaster:
    challenge = db.query(ChallengeMaster).filter(ChallengeMaster.CHALLENGE_MST_NO == challenge_mst_no).first()

    if not challenge:
        raise HTTPException(status_code=404, detail="챌린지를 찾을 수 없습니다.")

    return challenge


def post_create_challenge(db: Session, challenge_create: ChallengeCreate, current_user: User):
    db_challenge = ChallengeMaster(
        CHALLENGE_MST_NM=challenge_create.CHALLENGE_MST_NM,
        START_DT=challenge_create.START_DT,
        END_DT=challenge_create.END_DT,
        HEADER_EMOJI=challenge_create.HEADER_EMOJI,
        CHALLENGE_STATUS=challenge_create.CHALLENGE_STATUS,
    )
    db.add(db_challenge)

    items = db.query(Item).all()
    item_users = []

    # USERS_UID를 기반으로 챌린지에 참여중인 유저를 가져와 challenge_user 생성
    for uid in challenge_create.USERS_UID:
        user = get_user_by_uid(db, uid)
        team_leader = get_user_by_uid(db, uid=random.choice(challenge_create.USERS_UID))

        db_challenge_user = ChallengeUser(
            CHALLENGE_MST=db_challenge,
            USER=user,
            IS_OWNER=current_user == user if True else False,
            IS_LEADER=team_leader == user if True else False,
            ACCEPT_STATUS=InviteAcceptType.ACCEPTED if current_user == user else InviteAcceptType.PENDING
        )
        db.add(db_challenge_user)

        db_team = TeamWeeklyGoal(
            CHALLENGE_USER=db_challenge_user,
            START_DT=challenge_create.START_DT,
            END_DT=challenge_create.START_DT + timedelta(days=7),
        )
        db.add(db_team)

        for item in items:
            db_item_user = ItemUser(
                ITEM_NO=item.ITEM_NO,
                CHALLENGE_USER=db_challenge_user
            )
            item_users.append(db_item_user)

    for item_user in item_users:
        db.add(item_user)

    db.commit()


def get_challenge_user_list(db: Session, challenge_mst_no: int):
    # ChallengeUserList 정보 조회
    challenge_users = get_challenge_user_by_no(db, challenge_mst_no)

    challenge_user_lists = []
    for challenge_user in challenge_users:
        # 각 사용자별로 Character 및 Pet 정보 조회
        character_info = db.query(Avatar).join(AvatarUser, Avatar.AVATAR_NO == AvatarUser.AVATAR_NO).filter(
            AvatarUser.USER_NO == challenge_user.USER_NO, Avatar.AVATAR_TYPE == 'CHARACTER').first()

        if not character_info:
            raise HTTPException(status_code=404, detail="캐릭터 정보를 찾을 수 없습니다.")

        pet_info = db.query(Avatar).join(AvatarUser, Avatar.AVATAR_NO == AvatarUser.AVATAR_NO).filter(
            AvatarUser.USER_NO == challenge_user.USER_NO, Avatar.AVATAR_TYPE == 'PET').first()

        challenge_user_list = ChallengeUserList(
            CHALLENGE_USER_NO=challenge_user.CHALLENGE_USER_NO,
            PROGRESS=0,
            CHARACTER_NO=character_info.AVATAR_NO,
            PET_NO=pet_info.AVATAR_NO if pet_info else None
        )
        challenge_user_lists.append(challenge_user_list)

    return challenge_user_lists

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
