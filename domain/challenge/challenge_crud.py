from datetime import datetime, timedelta, date
import random

from fastapi import HTTPException
from sqlalchemy import func, Integer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from domain.challenge.challenge_schema import ChallengeCreate, ChallengeParticipant, \
    PersonDailyGoalPydantic, \
    TeamWeeklyGoalPydantic, AdditionalGoalPydantic, ChallengeList, ChallengeInvite, \
    ChallengeUserList, GetChallengeUserDetail
from domain.desc.utils import calculate_challenge_progress
from domain.user.user_crud import get_user_by_uid
from models import ChallengeMaster, User, TeamWeeklyGoal, ChallengeUser, PersonDailyGoal, AdditionalGoal, ItemUser, \
    Item, InviteAcceptType, Avatar, AvatarUser, PersonDailyGoalComplete, AvatarType


# 기능 함수
# Challenge Master을 Current User으로 가져오기
def get_challenge_masters_by_user(db: Session, current_user: User) -> ChallengeMaster:
    challenges = db.query(ChallengeMaster). \
        join(ChallengeUser, ChallengeUser.CHALLENGE_MST_NO == ChallengeMaster.CHALLENGE_MST_NO). \
        filter(ChallengeUser.USER_NO == current_user.USER_NO).all()

    if not challenges:
        raise HTTPException(status_code=404, detail="챌린지를 찾을 수 없습니다.")

    return challenges


# Challenge Master 객체를 Challenge Mst No로 가져오기
def get_challenge_master_by_id(db: Session, challenge_mst_no: int) -> ChallengeMaster:
    challenge = db.query(ChallengeMaster).filter(ChallengeMaster.CHALLENGE_MST_NO == challenge_mst_no).first()

    if not challenge:
        raise HTTPException(status_code=404, detail="챌린지를 찾을 수 없습니다.")

    return challenge


# 개인의 챌린지 진행도 계산
def calculate_user_progress(db: Session, challenge_user_no: int):
    try:
        # 챌린지 마스터의 시작 및 종료 날짜만 선택
        challenge_master = db.query(ChallengeMaster.START_DT, ChallengeMaster.END_DT).filter(
            ChallengeMaster.USERS.any(CHALLENGE_USER_NO=challenge_user_no)).first()

        if not challenge_master:
            raise ValueError("챌린지 마스터 정보를 찾을 수 없습니다.")

        start_dt = challenge_master.START_DT
        end_dt = challenge_master.END_DT

        # 챌린지 기간 계산
        day = (end_dt - start_dt).days + 1

        if day <= 0:
            raise ValueError("챌린지 기간이 잘못되었습니다.")

        week = (day // 7) + 1

        # 일일, 주간, 추가 목표 진행도를 단일 쿼리로 계산
        progress_stats = db.query(
            func.count(PersonDailyGoalComplete.DAILY_COMPLETE_NO),
            func.sum(func.cast(TeamWeeklyGoal.IS_DONE, Integer)),
            func.sum(func.cast(AdditionalGoal.IS_DONE, Integer)),
            func.sum(func.cast(AdditionalGoal.IS_DONE == False, Integer))
        ).select_from(ChallengeUser) \
            .outerjoin(PersonDailyGoalComplete,
                       ChallengeUser.CHALLENGE_USER_NO == PersonDailyGoalComplete.CHALLENGE_USER_NO) \
            .outerjoin(TeamWeeklyGoal, ChallengeUser.CHALLENGE_USER_NO == TeamWeeklyGoal.CHALLENGE_USER_NO) \
            .outerjoin(AdditionalGoal, ChallengeUser.CHALLENGE_USER_NO == AdditionalGoal.CHALLENGE_USER_NO) \
            .filter(ChallengeUser.CHALLENGE_USER_NO == challenge_user_no) \
            .group_by(ChallengeUser.CHALLENGE_USER_NO).first()

        if not progress_stats:
            raise ValueError("진행도 데이터를 찾을 수 없습니다.")

        daily_goals_completed, weekly_goals_completed, additional_goals_completed, additional_goals_failed = progress_stats

        # None 값 처리
        daily_goals_completed = daily_goals_completed or 0
        weekly_goals_completed = weekly_goals_completed or 0
        additional_goals_completed = additional_goals_completed or 0
        additional_goals_failed = additional_goals_failed or 0

        # 진행도 계산
        daily_progress = (85 / day) * daily_goals_completed
        weekly_progress = (15 / week) * weekly_goals_completed
        additional_progress = (additional_goals_completed - additional_goals_failed) * 5

        # 전체 진행도 계산
        total_progress = daily_progress + weekly_progress + additional_progress

        return total_progress

    except SQLAlchemyError as e:
        # 데이터베이스 쿼리 중 발생하는 예외 처리
        raise ValueError("데이터베이스 처리 중 오류 발생: " + str(e))
    except ValueError as e:
        # 기타 계산 또는 데이터 검증 중 발생하는 예외 처리
        raise ValueError("계산 중 오류 발생: " + str(e))


# 챌린지에 참가하고 있는 참가자 리스트 반환
def get_challenge_participants(db: Session, challenge_mst_no):
    participants = db.query(
        User,
        ChallengeUser.ACCEPT_STATUS
    ).join(
        ChallengeUser, User.USER_NO == ChallengeUser.USER_NO
    ).filter(
        ChallengeUser.CHALLENGE_MST_NO == challenge_mst_no
    ).all()

    if not participants:
        raise HTTPException(status_code=404, detail="참가자를 찾을 수 없습니다.")

    return participants


# 특정 Challenge User객체의 정보를 challenge mst no와 user_no로 가져오기
def get_challenge_user_by_user_no(db: Session, challenge_mst_no, user_no):
    challenge_user = db.query(ChallengeUser).filter(
        ChallengeUser.USER_NO == user_no,
        ChallengeUser.CHALLENGE_MST_NO == challenge_mst_no
    ).first()

    if not challenge_user:
        raise HTTPException(status_code=404, detail="특정 사용자에 대한 challenge_user를 찾을 수 없습니다.")

    return challenge_user


# Challenge User 객체들의 정보를 challenge mst no로 가져오기
def get_challenge_users_by_mst_no(db: Session, challenge_mst_no):
    challenge_users = db.query(ChallengeUser).filter(
        ChallengeUser.CHALLENGE_MST_NO == challenge_mst_no
    ).all()

    if not challenge_users:
        raise HTTPException(status_code=404, detail="challenge_user를 찾을 수 없습니다.")

    return challenge_users


# 해당 날짜의 사용자 person goal 객체들을 가져오기
def get_person_goal_by_user(db: Session, challenge_user_no: int, current_day: date):
    person_goals = db.query(PersonDailyGoal).filter(
        PersonDailyGoal.CHALLENGE_USER_NO == challenge_user_no,
        PersonDailyGoal.INSERT_DT >= current_day,
        PersonDailyGoal.INSERT_DT <= current_day + timedelta(days=1)
    ).all()

    return person_goals


# 착용중인 아바타 가져오기
def get_equipped_avatar(db: Session, user_no: int, avatar_type: AvatarType):
    avatar = db.query(AvatarUser).join(Avatar, Avatar.AVATAR_NO == AvatarUser.AVATAR_NO).filter(
        AvatarUser.USER_NO == user_no,
        AvatarUser.IS_EQUIP == True,
        Avatar.AVATAR_TYPE == avatar_type
    ).first()

    if avatar_type == AvatarType.CHARACTER and not avatar:
        raise HTTPException(status_code=404, detail="CHARACTER 정보를 찾을 수 없습니다.")

    return avatar


# challenge_user 객체를 challenge_user_no 값으로 가져오기
def get_challenge_user_by_challenge_user_no(db: Session, challenge_user_no: int):
    challenge_user = db.query(ChallengeUser).filter(ChallengeUser.CHALLENGE_USER_NO == challenge_user_no).first()

    if not challenge_user:
        raise HTTPException(status_code=404, detail="challenge_user를 찾을 수 없습니다.")

    return challenge_user


# 라우터 함수
def get_challenge_list(db: Session, current_user: User):
    challenges = get_challenge_masters_by_user(db, current_user)

    if not challenges:
        return []

    challenge_list = []
    for challenge in challenges:
        challenge_info = ChallengeList.model_validate(challenge)
        challenge_info.PROGRESS = calculate_challenge_progress(challenge.START_DT, challenge.END_DT)

        challenge_list.append(challenge_info)

    return challenge_list


def get_challenge_detail(db: Session, user_no: int, challenge_mst_no: int, current_day: date):
    challenge_user = get_challenge_user_by_user_no(db, challenge_mst_no, user_no)

    person_goals = get_person_goal_by_user(db, challenge_user.CHALLENGE_USER_NO, current_day)

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
    return db_challenge


def get_challenge_user_list(db: Session, challenge_mst_no: int):
    # ChallengeUserList 정보 조회
    challenge_users = get_challenge_users_by_mst_no(db, challenge_mst_no)

    challenge_user_lists = []
    for challenge_user in challenge_users:
        # 각 사용자별로 Character 및 Pet 정보 조회
        character = get_equipped_avatar(db, challenge_user.USER_NO, AvatarType.CHARACTER)

        if not character:
            raise HTTPException(status_code=404, detail="캐릭터 정보를 찾을 수 없습니다.")

        pet = get_equipped_avatar(db, challenge_user.USER_NO, AvatarType.PET)

        challenge_user_list = ChallengeUserList(
            CHALLENGE_USER_NO=challenge_user.CHALLENGE_USER_NO,
            PROGRESS=calculate_user_progress(db, challenge_user.CHALLENGE_USER_NO),
            CHARACTER_NO=character.AVATAR_NO,
            PET_NO=pet.AVATAR_NO if pet else None
        )
        challenge_user_lists.append(challenge_user_list)

    return challenge_user_lists


def get_challenge_user_detail(db: Session, challenge_user_no: int, current_day: date):
    challenge_user = get_challenge_user_by_challenge_user_no(db, challenge_user_no)
    user = db.query(User).filter(User.USER_NO == challenge_user.USER_NO).first()
    character = get_equipped_avatar(db, challenge_user.USER_NO, AvatarType.CHARACTER)
    person_goal = get_person_goal_by_user(db, challenge_user_no, current_day)

    return GetChallengeUserDetail(
        CHALLENGE_USER_NO=challenge_user.CHALLENGE_USER_NO,
        USER_NM=user.USER_NM,
        CHARACTER_NO=character.AVATAR_NO,
        PROGRESS=calculate_user_progress(db, challenge_user_no),
        COMMENT=challenge_user.COMMENT,
        personGoal=person_goal
    )

# def get_challenge_history_list(db: Session, current_day: date, _current_user: User):
#     return GetChallengeUserDetail()
