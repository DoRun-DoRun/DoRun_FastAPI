from datetime import datetime, timedelta, date
import random
from math import ceil
from typing import Type

from fastapi import HTTPException
from sqlalchemy import func, Integer, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload, aliased

from domain.challenge.challenge_schema import ChallengeCreate, ChallengeParticipant, \
    AdditionalGoalPydantic, ChallengeInvite, \
    ChallengeUserList, GetChallengeUserDetail, ChallengeUserListModel, GetChallengeHistory, EmojiUser, DiaryPydantic, \
    ItemPydantic, UserStatus
from domain.desc.utils import calculate_challenge_progress
from domain.user.user_crud import get_user_by_uid, get_equipped_avatar
from models import ChallengeMaster, User, ChallengeUser, PersonDailyGoal, AdditionalGoal, ItemUser, \
    Item, InviteAcceptType, PersonDailyGoalComplete, AvatarType, ChallengeStatusType, \
    DailyCompleteUser


# 기능 함수
# Challenge Master 객체를 Challenge Mst No로 가져오기
def get_challenge_master_by_id(db: Session, challenge_mst_no: int) -> Type[ChallengeMaster]:
    challenge = db.query(ChallengeMaster).filter(ChallengeMaster.CHALLENGE_MST_NO == challenge_mst_no).first()

    if not challenge:
        raise HTTPException(status_code=404, detail="챌린지를 찾을 수 없습니다.")

    if challenge.DELETE_YN:
        raise HTTPException(status_code=404, detail="삭제된 챌린지 입니다.")

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

        # week = (day // 7) + 1

        # 일일, 주간, 추가 목표 진행도를 단일 쿼리로 계산
        progress_stats = db.query(
            func.count(PersonDailyGoalComplete.DAILY_COMPLETE_NO),
            # func.sum(func.cast(TeamWeeklyGoal.IS_DONE, Integer)),
            func.sum(func.cast(AdditionalGoal.IS_DONE, Integer)),
            func.sum(func.cast(AdditionalGoal.IS_DONE == False, Integer))
        ).select_from(ChallengeUser) \
            .outerjoin(PersonDailyGoalComplete,
                       ChallengeUser.CHALLENGE_USER_NO == PersonDailyGoalComplete.CHALLENGE_USER_NO) \
            .outerjoin(AdditionalGoal, ChallengeUser.CHALLENGE_USER_NO == AdditionalGoal.CHALLENGE_USER_NO) \
            .filter(ChallengeUser.CHALLENGE_USER_NO == challenge_user_no) \
            .group_by(ChallengeUser.CHALLENGE_USER_NO).first()

        # .outerjoin(TeamWeeklyGoal, ChallengeUser.CHALLENGE_USER_NO == TeamWeeklyGoal.CHALLENGE_USER_NO) \

        if not progress_stats:
            raise ValueError("진행도 데이터를 찾을 수 없습니다.")

        # daily_goals_completed, weekly_goals_completed, additional_goals_completed, additional_goals_failed = progress_stats
        daily_goals_completed, additional_goals_completed, additional_goals_failed = progress_stats

        # None 값 처리
        daily_goals_completed = daily_goals_completed or 0
        # weekly_goals_completed = weekly_goals_completed or 0
        additional_goals_completed = additional_goals_completed or 0
        additional_goals_failed = additional_goals_failed or 0

        # 진행도 계산
        daily_progress = (100 / day) * daily_goals_completed
        # weekly_progress = (15 / week) * weekly_goals_completed
        additional_progress = (additional_goals_completed - additional_goals_failed) * 5

        # 전체 진행도 계산
        # total_progress = daily_progress + weekly_progress + additional_progress
        total_progress = daily_progress + additional_progress

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


# 해당 날짜의 Challenge User객체들의 정보를 user_no로 가져오기
def get_challenge_users_by_user_no(db: Session, user_no):
    challenge_user = db.query(ChallengeUser).filter(
        ChallengeUser.USER_NO == user_no,
    ).all()

    if not challenge_user:
        raise HTTPException(status_code=404, detail="사용자에 대한 challenge_user를 찾을 수 없습니다.")

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
def get_person_goal_by_user(db: Session, challenge_user_no: int, current_day: datetime):
    person_goals = db.query(PersonDailyGoal).filter(
        PersonDailyGoal.CHALLENGE_USER_NO == challenge_user_no,
        PersonDailyGoal.INSERT_DT >= current_day,
        PersonDailyGoal.INSERT_DT <= current_day + timedelta(days=1)
    ).all()

    return person_goals


# 해당 날짜의 사용자 team weekly goal 객체들을 가져오기
# def get_team_weekly_goal_by_user(db: Session, challenge_mst_no: int, current_day: datetime):
#     team_goals = db.query(TeamWeeklyGoal).join(
#         ChallengeUser,
#     ).filter(
#         ChallengeUser.CHALLENGE_MST_NO == challenge_mst_no,
#         TeamWeeklyGoal.START_DT <= current_day,  # 현재 시간 이후로 시작하는 것을 포함
#         TeamWeeklyGoal.END_DT >= current_day,  # 현재 시간 이전에 종료하는 것을 배제
#     ).all()
#
#     return team_goals


# challenge_user 객체를 challenge_user_no 값으로 가져오기
def get_challenge_user_by_challenge_user_no(db: Session, challenge_user_no: int):
    challenge_user = db.query(ChallengeUser).filter(ChallengeUser.CHALLENGE_USER_NO == challenge_user_no).first()

    if not challenge_user:
        raise HTTPException(status_code=404, detail="challenge_user를 찾을 수 없습니다.")

    return challenge_user


# 지정된 날짜에 활성화된 챌린지 중, 특정 유저가 참여하고 있는 챌린지 조회
def get_active_challenges_for_user(db: Session, user_no: int, specified_date: date, page: int):
    page_size = 1
    offset = (page - 1) * page_size

    user_challenge = db.query(ChallengeMaster).join(
        ChallengeUser,
        ChallengeUser.CHALLENGE_MST_NO == ChallengeMaster.CHALLENGE_MST_NO
    ).filter(
        ChallengeUser.USER_NO == user_no,
        ChallengeMaster.START_DT <= specified_date,
        ChallengeMaster.END_DT >= specified_date,
        ChallengeMaster.DELETE_YN == False,
        ChallengeMaster.CHALLENGE_STATUS != ChallengeStatusType.PENDING
    ).offset(offset).limit(page_size).first()

    if not user_challenge:
        # raise HTTPException(status_code=404, detail="해당 날짜에 챌린지 기록이 존재하지 않습니다.")
        return None

    return user_challenge


# 라우터 함수
def get_challenge_list(db: Session, current_user: User):
    challenge_user_alias = aliased(ChallengeUser)

    challenges = db.query(
        ChallengeMaster.CHALLENGE_MST_NO,
        ChallengeMaster.CHALLENGE_MST_NM,
        ChallengeMaster.START_DT,
        ChallengeMaster.END_DT,
        ChallengeMaster.HEADER_EMOJI,
        ChallengeMaster.CHALLENGE_STATUS,
        challenge_user_alias.ACCEPT_STATUS
    ).join(
        challenge_user_alias,
        challenge_user_alias.CHALLENGE_MST_NO == ChallengeMaster.CHALLENGE_MST_NO
    ).filter(
        challenge_user_alias.USER_NO == current_user.USER_NO,
        ChallengeMaster.CHALLENGE_STATUS != ChallengeStatusType.COMPLETE,
        ChallengeMaster.DELETE_YN == False
    ).all()

    invited_challenges = [
        {
            "CHALLENGE_MST_NO": challenge.CHALLENGE_MST_NO,
            "CHALLENGE_MST_NM": challenge.CHALLENGE_MST_NM,
            "START_DT": challenge.START_DT,
            "END_DT": challenge.END_DT,
            "HEADER_EMOJI": challenge.HEADER_EMOJI,
            "CHALLENGE_STATUS": challenge.CHALLENGE_STATUS,
            "PROGRESS": calculate_challenge_progress(challenge.START_DT, challenge.END_DT)
        }
        for challenge in challenges if challenge.ACCEPT_STATUS == InviteAcceptType.PENDING
    ]

    progress_challenges = [
        {
            "CHALLENGE_MST_NO": challenge.CHALLENGE_MST_NO,
            "CHALLENGE_MST_NM": challenge.CHALLENGE_MST_NM,
            "START_DT": challenge.START_DT,
            "END_DT": challenge.END_DT,
            "HEADER_EMOJI": challenge.HEADER_EMOJI,
            "CHALLENGE_STATUS": challenge.CHALLENGE_STATUS,
            "PROGRESS": calculate_challenge_progress(challenge.START_DT, challenge.END_DT)
        }
        for challenge in challenges if challenge.ACCEPT_STATUS == InviteAcceptType.ACCEPTED
    ]

    return {
        "invited_challenges": invited_challenges,
        "progress_challenges": progress_challenges
    }


def get_challenge_detail(db: Session, user_no: int, challenge_mst_no: int):
    challenge = get_challenge_master_by_id(db, challenge_mst_no)
    challenge_user = get_challenge_user_by_user_no(db, challenge_mst_no, user_no)

    # person_goals = get_person_goal_by_user(db, challenge_user.CHALLENGE_USER_NO, current_day)

    # 현재 UTC 시간 가져오기
    current_utc_time = datetime.utcnow()

    # TeamWeeklyGoal 목록 검색 및 필터링
    # team_goals = get_team_weekly_goal_by_user(db, challenge_mst_no, current_day)

    today = datetime.utcnow().date()
    day_start = datetime(today.year, today.month, today.day - 1, 19, 0, 0)
    day_end = day_start + timedelta(days=1) - timedelta(minutes=1)

    existing_diary = db.query(PersonDailyGoalComplete).filter(
        and_(
            PersonDailyGoalComplete.CHALLENGE_USER == challenge_user,
            PersonDailyGoalComplete.INSERT_DT >= day_start,
            PersonDailyGoalComplete.INSERT_DT <= day_end
        )
    ).first()

    additional_goals = db.query(AdditionalGoal).join(
        ChallengeUser,
        ChallengeUser.CHALLENGE_USER_NO == AdditionalGoal.CHALLENGE_USER_NO
    ).join(
        User,
        User.USER_NO == ChallengeUser.USER_NO
    ).filter(
        ChallengeUser.CHALLENGE_MST_NO == challenge_mst_no,
        AdditionalGoal.START_DT <= current_utc_time,
        AdditionalGoal.END_DT >= current_utc_time
    ).all()

    additional_goals_data = []
    for goal in additional_goals:
        try:
            # ChallengeUser와 User 테이블에 대한 참조를 사용하여 사용자 이름 가져오기
            user_nn = goal.CHALLENGE_USER.USER.USER_NM

            # Pydantic 모델에 필요한 데이터를 딕셔너리로 만들기
            goal_data_dict = {
                "ADDITIONAL_NO": goal.ADDITIONAL_NO,
                "ADDITIONAL_NM": goal.ADDITIONAL_NM,
                "IS_DONE": goal.IS_DONE,
                "IMAGE_FILE_NM": goal.IMAGE_FILE_NM,
                "START_DT": goal.START_DT,
                "END_DT": goal.END_DT,
                "CHALLENGE_USER_NO": goal.CHALLENGE_USER_NO,
                "CHALLENGE_USER_NN": user_nn,  # 추가된 사용자 이름
                "IS_MINE": goal.CHALLENGE_USER_NO == challenge_user.CHALLENGE_USER_NO
            }

            # 딕셔너리를 Pydantic 모델로 변환
            goal_data = AdditionalGoalPydantic(**goal_data_dict)
            additional_goals_data.append(goal_data)
        except Exception as e:
            print(f"Error processing goal: {goal}. Error: {e}")

    # Pydantic 모델을 사용하여 결과 구조화
    return {
        "CHALLENGE_USER_NO": challenge_user.CHALLENGE_USER_NO,
        "CHALLENGE_STATUS": challenge.CHALLENGE_STATUS,
        "IS_DONE_TODAY": existing_diary is not None,
        # "personGoal": [PersonDailyGoalPydantic.model_validate(goal) for goal in person_goals],
        # "teamGoal": [TeamWeeklyGoalPydantic.model_validate(goal) for goal in team_goals],
        "additionalGoal": additional_goals_data
    }


def get_challenge_invite(db: Session, challenge_mst_no: int, _current_user: User):
    _challenge = get_challenge_master_by_id(db, challenge_mst_no)
    _challenge_user = get_challenge_user_by_user_no(db, _challenge.CHALLENGE_MST_NO, _current_user.USER_NO)

    # SQLAlchemy 모델 객체에서 필요한 필드만 추출
    challenge_data = {
        'CHALLENGE_MST_NO': _challenge.CHALLENGE_MST_NO,
        'CHALLENGE_MST_NM': _challenge.CHALLENGE_MST_NM,
        'START_DT': _challenge.START_DT,
        'END_DT': _challenge.END_DT,
        'HEADER_EMOJI': _challenge.HEADER_EMOJI,
        'CHALLENGE_STATUS': _challenge.CHALLENGE_STATUS,
        "IS_OWNER": _challenge_user.IS_OWNER
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
    )
    db.add(db_challenge)

    # USERS_UID를 기반으로 챌린지에 참여중인 유저를 가져와 challenge_user 생성
    for uid in challenge_create.USERS_UID:
        user = get_user_by_uid(db, uid.USER_UID)

        db_challenge_user = ChallengeUser(
            CHALLENGE_MST=db_challenge,
            # COMMENT=random.choice(comments),
            USER=user,
            IS_OWNER=current_user == user if True else False,
            ACCEPT_STATUS=InviteAcceptType.ACCEPTED if current_user == user else InviteAcceptType.PENDING
        )
        db.add(db_challenge_user)

    db.commit()
    return db_challenge


def start_challenge(db: Session, challenge_mst_no: int, current_user: User, start_dt: datetime):
    challenge = get_challenge_master_by_id(db, challenge_mst_no)
    owner = get_challenge_user_by_user_no(db, challenge_mst_no, user_no=current_user.USER_NO)

    if not owner.IS_OWNER:
        raise HTTPException(status_code=401, detail="시작 권한이 없습니다")

    challenge.START_DT = start_dt
    challenge.CHALLENGE_STATUS = ChallengeStatusType.PROGRESS

    comments = [
        "하루 하루가 소중해요.",
        "늘 최선을 다하세요!",
        "긍정의 힘이 당신을 이끌어요.",
        "오늘도 멋진 하루가 되길 바랍니다.",
        "작은 성공이 큰 기쁨으로 이어지길."
    ]

    # ACCEPTED 상태가 아닌 ChallengeUser 삭제
    db.query(ChallengeUser).filter(
        ChallengeUser.CHALLENGE_MST_NO == challenge_mst_no,
        ChallengeUser.ACCEPT_STATUS != InviteAcceptType.ACCEPTED
    ).delete(synchronize_session=False)

    challenge_users = db.query(ChallengeUser).filter(
        ChallengeUser.CHALLENGE_MST_NO == challenge_mst_no, ChallengeUser.ACCEPT_STATUS == InviteAcceptType.ACCEPTED
    ).all()

    items = db.query(Item).all()

    # team_leader = random.choice(challenge_users)
    # team_leader.IS_LEADER = True

    for challenge_user in challenge_users:
        # db_team = TeamWeeklyGoal(
        #     CHALLENGE_USER=challenge_user,
        #     START_DT=challenge.START_DT,
        #     END_DT=challenge.START_DT + timedelta(days=7),
        # )
        # db.add(db_team)

        challenge_user.COMMENT = random.choice(comments)

        for item in items:
            db_item_user = ItemUser(
                ITEM_NO=item.ITEM_NO,
                CHALLENGE_USER=challenge_user
            )
            db.add(db_item_user)

    db.commit()
    return {"message": "챌린지가 시작되었습니다"}


def start_challenge_server(db: Session, challenge: ChallengeMaster):
    challenge.CHALLENGE_STATUS = ChallengeStatusType.PROGRESS

    # ACCEPTED 상태가 아닌 ChallengeUser 삭제
    db.query(ChallengeUser).filter(
        ChallengeUser.CHALLENGE_MST_NO == challenge.CHALLENGE_MST_NO,
        ChallengeUser.ACCEPT_STATUS != InviteAcceptType.ACCEPTED
    ).delete(synchronize_session=False)

    challenge_users = db.query(ChallengeUser).filter(
        ChallengeUser.CHALLENGE_MST_NO == challenge.CHALLENGE_MST_NO,
        ChallengeUser.ACCEPT_STATUS == InviteAcceptType.ACCEPTED
    ).all()

    items = db.query(Item).all()

    comments = [
        "하루 하루가 소중해요.",
        "늘 최선을 다하세요!",
        "긍정의 힘이 당신을 이끌어요.",
        "오늘도 멋진 하루가 되길 바랍니다.",
        "작은 성공이 큰 기쁨으로 이어지길."
    ]

    for challenge_user in challenge_users:
        challenge_user.COMMENT = random.choice(comments)

        for item in items:
            db_item_user = ItemUser(
                ITEM_NO=item.ITEM_NO,
                CHALLENGE_USER=challenge_user
            )
            db.add(db_item_user)

    db.commit()
    return {"message": "챌린지가 시작되었습니다"}


def end_challenge_server(db: Session, challenge: ChallengeMaster):
    challenge.CHALLENGE_STATUS = ChallengeStatusType.COMPLETE

    challenge_users = db.query(ChallengeUser).filter(
        ChallengeUser.CHALLENGE_MST_NO == challenge.CHALLENGE_MST_NO,
        ChallengeUser.ACCEPT_STATUS == InviteAcceptType.ACCEPTED
    ).all()


def get_challenge_user_list(db: Session, current_user: User, page: int):
    page_size = 1
    offset = (page - 1) * page_size

    # 총 항목 수 계산
    total_items = db.query(ChallengeMaster). \
        join(ChallengeUser, ChallengeUser.CHALLENGE_MST_NO == ChallengeMaster.CHALLENGE_MST_NO). \
        filter(ChallengeUser.USER_NO == current_user.USER_NO,
               ChallengeMaster.CHALLENGE_STATUS == ChallengeStatusType.PROGRESS,
               ChallengeUser.ACCEPT_STATUS == InviteAcceptType.ACCEPTED,
               ChallengeMaster.DELETE_YN == False).count()

    # 총 페이지 수 계산
    total_pages = ceil(total_items / page_size)

    challenge = db.query(ChallengeMaster). \
        join(ChallengeUser, ChallengeUser.CHALLENGE_MST_NO == ChallengeMaster.CHALLENGE_MST_NO). \
        filter(ChallengeUser.USER_NO == current_user.USER_NO,
               ChallengeMaster.CHALLENGE_STATUS == ChallengeStatusType.PROGRESS,
               ChallengeUser.ACCEPT_STATUS == InviteAcceptType.ACCEPTED,
               ChallengeMaster.DELETE_YN == False) \
        .offset(offset) \
        .limit(page_size) \
        .first()

    if not challenge:
        return {}

    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)

    # ChallengeUserList 정보 조회
    challenge_users = get_challenge_users_by_mst_no(db, challenge.CHALLENGE_MST_NO)

    challenge_user_lists = []
    one_week_ago = datetime.utcnow() - timedelta(days=7)

    for challenge_user in challenge_users:
        # 각 사용자별로 Character 및 Pet 정보 조회
        character = get_equipped_avatar(db, challenge_user.USER_NO, AvatarType.CHARACTER)

        if not character:
            raise HTTPException(status_code=404, detail="캐릭터 정보를 찾을 수 없습니다.")

        pet = get_equipped_avatar(db, challenge_user.USER_NO, AvatarType.PET)

        if challenge_user.USER_NO != current_user.USER_NO:
            diaries = db.query(PersonDailyGoalComplete).filter(
                PersonDailyGoalComplete.CHALLENGE_USER_NO == challenge_user.CHALLENGE_USER_NO,
                PersonDailyGoalComplete.INSERT_DT >= twenty_four_hours_ago
                # PersonDailyGoalComplete.COMMENT != '' or PersonDailyGoalComplete.IMAGE_FILE_NM != '',
            ).all()
        else:
            diaries = []

        total_diaries = db.query(PersonDailyGoalComplete).filter(
            PersonDailyGoalComplete.CHALLENGE_USER_NO == challenge_user.CHALLENGE_USER_NO,
            PersonDailyGoalComplete.INSERT_DT >= one_week_ago
        ).all()

        diaries_length = len(total_diaries)
        user_status = UserStatus.SLEEPING
        if 1 <= diaries_length < 3:
            user_status = UserStatus.WALKING  # '걷고 있음'
        elif diaries_length >= 3:
            user_status = UserStatus.RUNNING  # '뛰고 있음'

        challenge_user_list = ChallengeUserList(
            CHALLENGE_USER_NO=challenge_user.CHALLENGE_USER_NO,
            PROGRESS=calculate_user_progress(db, challenge_user.CHALLENGE_USER_NO),
            CHARACTER_NO=character.AVATAR_NO,
            PET_NO=pet.AVATAR_NO if pet else None,
            DIARIES=[DiaryPydantic.model_validate(diary) for diary in diaries],
            STATUS=user_status,
        )
        challenge_user_lists.append(challenge_user_list)

    return ChallengeUserListModel(
        CHALLENGE_MST_NO=challenge.CHALLENGE_MST_NO,
        CHALLENGE_MST_NM=challenge.CHALLENGE_MST_NM,
        challenge_user=challenge_user_lists,
        total_page=total_pages)


def get_challenge_user_detail(db: Session, challenge_user_no: int, current_user: User):
    target_user = get_challenge_user_by_challenge_user_no(db, challenge_user_no)
    used_user = get_challenge_user_by_user_no(db, target_user.CHALLENGE_MST_NO, current_user.USER_NO)

    character = get_equipped_avatar(db, target_user.USER_NO, AvatarType.CHARACTER)

    items = db.query(Item).all()
    item_list = []

    one_week_ago = datetime.utcnow() - timedelta(days=7)

    diaries = db.query(PersonDailyGoalComplete).filter(
        PersonDailyGoalComplete.CHALLENGE_USER_NO == target_user.CHALLENGE_USER_NO,
        PersonDailyGoalComplete.INSERT_DT >= one_week_ago
    ).all()

    diary_count = len(diaries)
    user_status = UserStatus.SLEEPING
    if diary_count == 1:
        user_status = UserStatus.WALKING  # '걷고 있음'
    elif diary_count >= 3:
        user_status = UserStatus.RUNNING  # '뛰고 있음'

    if used_user != target_user:
        for item in items:
            item_user = db.query(ItemUser).filter(
                ItemUser.CHALLENGE_USER_NO == used_user.CHALLENGE_USER_NO,
                ItemUser.ITEM_NO == item.ITEM_NO
            ).first()

            item_list.append(ItemPydantic(
                ITEM_NO=item.ITEM_NO,
                ITEM_NM=item.ITEM_NM,
                COUNT=item_user.COUNT if item_user else 0,
                ITEM_USER_NO=item_user.ITEM_USER_NO if item_user else -1
            ))

    return GetChallengeUserDetail(
        CHALLENGE_USER_NO=target_user.CHALLENGE_USER_NO,
        END_DT=target_user.CHALLENGE_MST.END_DT,
        USER_NM=target_user.USER.USER_NM,
        CHARACTER_NO=character.AVATAR_NO,
        # PROGRESS=calculate_user_progress(db, challenge_user_no),
        COMMENT=target_user.COMMENT,
        ITEM=item_list,
        STATUS=user_status,
        IS_ME=target_user == used_user
    )


def get_challenge_history_list(db: Session, current_day: datetime, _current_user: User, page: int):
    challenge = get_active_challenges_for_user(db, _current_user.USER_NO, current_day, page)
    if not challenge:
        return GetChallengeHistory(
            CHALLENGE_MST_NO=0,
            CHALLENGE_MST_NM=None,
            IMAGE_FILE_NM=None,
            EMOJI=None,
            COMMENT=None,
            personGoal=None,
            total_size=0
        )

    total_size = db.query(ChallengeMaster).join(
        ChallengeUser,
        ChallengeUser.CHALLENGE_MST_NO == ChallengeMaster.CHALLENGE_MST_NO
    ).filter(
        ChallengeUser.USER_NO == _current_user.USER_NO,
        ChallengeMaster.START_DT <= current_day,
        ChallengeMaster.END_DT >= current_day,
        ChallengeMaster.DELETE_YN == False,
        ChallengeMaster.CHALLENGE_STATUS != ChallengeStatusType.PENDING
    ).count()

    challenge_user = get_challenge_user_by_user_no(db, challenge.CHALLENGE_MST_NO, _current_user.USER_NO)

    daily_complete = db.query(PersonDailyGoalComplete).filter(
        PersonDailyGoalComplete.CHALLENGE_USER_NO == challenge_user.CHALLENGE_USER_NO,
        PersonDailyGoalComplete.INSERT_DT >= current_day,
        PersonDailyGoalComplete.INSERT_DT <= current_day + timedelta(days=1)
    ).first()

    daily_complete_users_list = []
    image_file = ''
    comment = ''
    person_goal = []

    if daily_complete:
        image_file = daily_complete.IMAGE_FILE_NM
        comment = daily_complete.COMMENT
        daily_complete_users = db.query(DailyCompleteUser).filter(
            DailyCompleteUser.DAILY_COMPLETE_NO == daily_complete.DAILY_COMPLETE_NO,
        ).all()
        for daily_complete_user in daily_complete_users:
            daily_complete_users_list.append(
                EmojiUser(CHALLENGE_USER_NO=daily_complete_user.CHALLENGE_USER_NO, EMOJI=daily_complete_user.EMOJI))

        person_goal = get_person_goal_by_user(db, challenge_user.CHALLENGE_USER_NO, current_day)
    # team_goal = db.query(TeamWeeklyGoal).join(ChallengeUser).filter(
    #     ChallengeUser.CHALLENGE_MST_NO == challenge.CHALLENGE_MST_NO,
    #     TeamWeeklyGoal.START_DT <= current_day,  # 현재 시간 이후로 시작하는 것을 포함
    #     TeamWeeklyGoal.END_DT >= current_day,  # 현재 시간 이전에 종료하는 것을 배제
    #     challenge_user.CHALLENGE_USER_NO == TeamWeeklyGoal.CHALLENGE_USER_NO
    # ).first()

    return GetChallengeHistory(
        CHALLENGE_MST_NO=challenge.CHALLENGE_MST_NO,
        CHALLENGE_MST_NM=challenge.CHALLENGE_MST_NM,
        IMAGE_FILE_NM=image_file,
        EMOJI=daily_complete_users_list,
        COMMENT=comment,
        personGoal=person_goal,
        # teamGoal=team_goal,
        total_size=total_size
    )


# UID 정보를 가져와 CHALLENGE USER 업데이트 필요
def challenge_update(db: Session, challenge_mst_no: int, _challenge_update: ChallengeCreate, current_user: User):
    challenge = get_challenge_master_by_id(db, challenge_mst_no)
    challenge_user = get_challenge_user_by_user_no(db, challenge_mst_no, current_user.USER_NO)

    if not challenge_user.IS_OWNER:
        raise HTTPException(status_code=401, detail="수정 권한이 존재하지 않습니다.")

    existing_user_ids = {cu.USER.USER_NO for cu in challenge.USERS}
    update_user_ids = {uid.USER_UID for uid in _challenge_update.USERS_UID}

    # USERS_UID를 기반으로 챌린지에 참여중인 유저를 가져와 challenge_user 생성
    for uid in _challenge_update.USERS_UID:
        user = get_user_by_uid(db, uid.USER_UID)

        if user.USER_NO in existing_user_ids:
            continue  # 이미 챌린지에 참여중인 유저는 건너뜀

        db_challenge_user = ChallengeUser(
            CHALLENGE_MST=challenge,
            USER=user,
            IS_OWNER=(current_user.USER_NO == user.USER_NO),
            ACCEPT_STATUS=uid.INVITE_STATS
        )
        db.add(db_challenge_user)

    db.commit()

    for challenge_user in challenge.USERS:
        if challenge_user.USER.UID not in update_user_ids:
            db.delete(challenge_user)

    # 챌린지 정보 업데이트
    challenge.CHALLENGE_MST_NM = _challenge_update.CHALLENGE_MST_NM
    challenge.START_DT = _challenge_update.START_DT
    challenge.END_DT = _challenge_update.END_DT
    challenge.HEADER_EMOJI = _challenge_update.HEADER_EMOJI

    db.commit()

    return {"message": "챌린지가 성공적으로 업데이트 되었습니다."}


def challenge_add_user(db: Session, challenge_mst_no: int, new_user_uid: int, current_user: User):
    # 챌린지 정보 가져오기
    challenge = get_challenge_master_by_id(db, challenge_mst_no)

    # 현재 사용자가 챌린지의 소유자인지 확인
    challenge_user = get_challenge_user_by_user_no(db, challenge_mst_no, current_user.USER_NO)
    if not challenge_user.IS_OWNER:
        raise HTTPException(status_code=401, detail="수정 권한이 존재하지 않습니다.")

    # 새로운 사용자 정보 가져오기
    new_user = get_user_by_uid(db, new_user_uid)

    # 챌린지에 이미 있는 사용자인지 확인
    existing_user_ids = {cu.USER.USER_NO for cu in challenge.USERS}
    if new_user.USER_NO in existing_user_ids:
        raise HTTPException(status_code=400, detail="사용자가 이미 챌린지에 존재합니다.")

    # 새로운 사용자를 챌린지에 추가
    db_challenge_user = ChallengeUser(
        CHALLENGE_MST=challenge,
        USER=new_user,
        IS_OWNER=False,  # 새로 추가되는 사용자는 소유자가 아님
        ACCEPT_STATUS=InviteAcceptType.PENDING
    )
    db.add(db_challenge_user)
    db.commit()

    return {"message": "새 사용자가 챌린지에 추가되었습니다."}


def challenge_remove_user(db: Session, challenge_mst_no: int, user_uid: int, current_user: User):
    # 챌린지 정보 가져오기
    challenge = get_challenge_master_by_id(db, challenge_mst_no)

    # 현재 사용자가 챌린지의 소유자인지 확인
    challenge_user = get_challenge_user_by_user_no(db, challenge_mst_no, current_user.USER_NO)
    if not challenge_user.IS_OWNER:
        raise HTTPException(status_code=401, detail="삭제 권한이 존재하지 않습니다.")

    # 삭제할 사용자 정보 가져오기
    user_to_remove = get_user_by_uid(db, user_uid)

    # 삭제할 사용자가 챌린지에 있는지 확인
    challenge_user_to_remove = db.query(ChallengeUser).filter_by(
        CHALLENGE_MST_NO=challenge.CHALLENGE_MST_NO,
        USER_NO=user_to_remove.USER_NO
    ).first()

    if not challenge_user_to_remove:
        raise HTTPException(status_code=404, detail="챌린지에서 사용자를 찾을 수 없습니다.")

    # 사용자를 챌린지에서 삭제
    db.delete(challenge_user_to_remove)
    db.commit()

    return {"message": "사용자가 챌린지에서 삭제되었습니다."}


# 삭제 시, 기존 챌린지 조회에 대한 예외처리 필요
def challenge_delete(db: Session, challenge_mst_no: int, current_user: User):
    challenge = get_challenge_master_by_id(db, challenge_mst_no)
    challenge_user = get_challenge_user_by_user_no(db, challenge_mst_no, current_user.USER_NO)

    if challenge_user.IS_OWNER:
        challenge.DELETE_YN = True
        challenge.DELETE_DT = datetime.utcnow()
        challenge_users = get_challenge_users_by_mst_no(db, challenge_mst_no)

        for _challenge_user in challenge_users:
            db.delete(_challenge_user)

        db.commit()
        return {"message": "챌린지가 성공적으로 삭제되었습니다."}

    db.delete(challenge_user)
    db.commit()
    return {"message": "챌린지에서 성공적으로 탈퇴했습니다."}
