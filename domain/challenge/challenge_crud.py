from datetime import datetime, timedelta, date
import random

from fastapi import HTTPException
from sqlalchemy import func, Integer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from domain.challenge.challenge_schema import ChallengeCreate, ChallengeParticipant, \
    PersonDailyGoalPydantic, \
    TeamWeeklyGoalPydantic, AdditionalGoalPydantic, ChallengeList, ChallengeInvite, \
    ChallengeUserList, GetChallengeUserDetail, ChallengeUserListModel, GetChallengeHistory, EmojiUser, DiaryPydantic, \
    ItemPydantic
from domain.desc.utils import calculate_challenge_progress
from domain.user.user_crud import get_user_by_uid, get_equipped_avatar
from models import ChallengeMaster, User, TeamWeeklyGoal, ChallengeUser, PersonDailyGoal, AdditionalGoal, ItemUser, \
    Item, InviteAcceptType, PersonDailyGoalComplete, AvatarType, ChallengeStatusType, \
    DailyCompleteUser


# 기능 함수
# 진행중인 Challenge Master을 Current User으로 가져오기
def get_challenge_masters_by_user(db: Session, current_user: User) -> ChallengeMaster:
    challenges = db.query(ChallengeMaster). \
        join(ChallengeUser, ChallengeUser.CHALLENGE_MST_NO == ChallengeMaster.CHALLENGE_MST_NO). \
        filter(ChallengeUser.USER_NO == current_user.USER_NO,
               ChallengeMaster.CHALLENGE_STATUS != ChallengeStatusType.COMPLETE).all()

    if not challenges:
        raise HTTPException(status_code=404, detail="진행 중인 챌린지를 찾을 수 없습니다.")

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
def get_person_goal_by_user(db: Session, challenge_user_no: int, current_day: date):
    person_goals = db.query(PersonDailyGoal).filter(
        PersonDailyGoal.CHALLENGE_USER_NO == challenge_user_no,
        PersonDailyGoal.INSERT_DT >= current_day,
        PersonDailyGoal.INSERT_DT <= current_day + timedelta(days=1)
    ).all()

    return person_goals


# 해당 날짜의 사용자 team weekly goal 객체들을 가져오기
def get_team_weekly_goal_by_user(db: Session, challenge_mst_no: int, current_day: date):
    team_goals = db.query(TeamWeeklyGoal).join(
        ChallengeUser,
    ).filter(
        ChallengeUser.CHALLENGE_MST_NO == challenge_mst_no,
        TeamWeeklyGoal.START_DT <= current_day,  # 현재 시간 이후로 시작하는 것을 포함
        TeamWeeklyGoal.END_DT >= current_day  # 현재 시간 이전에 종료하는 것을 배제
    ).all()

    return team_goals


# challenge_user 객체를 challenge_user_no 값으로 가져오기
def get_challenge_user_by_challenge_user_no(db: Session, challenge_user_no: int):
    challenge_user = db.query(ChallengeUser).filter(ChallengeUser.CHALLENGE_USER_NO == challenge_user_no).first()

    if not challenge_user:
        raise HTTPException(status_code=404, detail="challenge_user를 찾을 수 없습니다.")

    return challenge_user


# 지정된 날짜에 활성화된 챌린지 중, 특정 유저가 참여하고 있는 챌린지 조회
def get_active_challenges_for_user(db: Session, user_no: int, specified_date: date):
    user_challenges = db.query(ChallengeMaster).join(
        ChallengeUser,
        ChallengeUser.CHALLENGE_MST_NO == ChallengeMaster.CHALLENGE_MST_NO
    ).filter(
        ChallengeUser.USER_NO == user_no,
        ChallengeMaster.START_DT <= specified_date,
        ChallengeMaster.END_DT >= specified_date
    ).all()

    if not user_challenges:
        raise HTTPException(status_code=404, detail="해당 날짜에 챌린지 기록이 존재하지 않습니다.")

    return user_challenges


# 라우터 함수
def get_challenge_list(db: Session, current_user: User):
    challenges = get_challenge_masters_by_user(db, current_user)

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
    team_goals = get_team_weekly_goal_by_user(db, challenge_mst_no, current_day)

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


def get_challenge_user_list(db: Session, current_user: User):
    challenges = get_challenge_masters_by_user(db, current_user)

    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)

    challenge_lists = []
    # ChallengeUserList 정보 조회
    for challenge in challenges:
        challenge_users = get_challenge_users_by_mst_no(db, challenge.CHALLENGE_MST_NO)

        challenge_user_lists = []
        for challenge_user in challenge_users:
            # 각 사용자별로 Character 및 Pet 정보 조회
            character = get_equipped_avatar(db, challenge_user.USER_NO, AvatarType.CHARACTER)

            if not character:
                raise HTTPException(status_code=404, detail="캐릭터 정보를 찾을 수 없습니다.")

            pet = get_equipped_avatar(db, challenge_user.USER_NO, AvatarType.PET)

            diaries = db.query(PersonDailyGoalComplete).filter(
                PersonDailyGoalComplete.CHALLENGE_USER_NO == challenge_user.CHALLENGE_USER_NO,
                PersonDailyGoalComplete.INSERT_DT >= twenty_four_hours_ago
            ).all()

            challenge_user_list = ChallengeUserList(
                CHALLENGE_USER_NO=challenge_user.CHALLENGE_USER_NO,
                PROGRESS=calculate_user_progress(db, challenge_user.CHALLENGE_USER_NO),
                CHARACTER_NO=character.AVATAR_NO,
                PET_NO=pet.AVATAR_NO if pet else None,
                DIARIES=[DiaryPydantic.model_validate(diary) for diary in diaries],
            )
            challenge_user_lists.append(challenge_user_list)

        challenge_lists.append(ChallengeUserListModel(
            CHALLENGE_MST_NO=challenge.CHALLENGE_MST_NO,
            CHALLENGE_MST_NM=challenge.CHALLENGE_MST_NM,
            challenge_user=challenge_user_lists)
        )

    return challenge_lists


def get_challenge_user_detail(db: Session, challenge_user_no: int):
    challenge_user = get_challenge_user_by_challenge_user_no(db, challenge_user_no)
    user = db.query(User).filter(User.USER_NO == challenge_user.USER_NO).first()
    character = get_equipped_avatar(db, challenge_user.USER_NO, AvatarType.CHARACTER)
    items = db.query(Item).all()
    item_list = []
    for item in items:
        item_user = db.query(ItemUser).filter(
            ItemUser.CHALLENGE_USER_NO == challenge_user_no,
            ItemUser.ITEM_NO == item.ITEM_NO).first()
        item_list.append(ItemPydantic(ITEM_NO=item.ITEM_NO, ITEM_NM=item.ITEM_NM, COUNT=item_user.COUNT,
                                      ITEM_USER_NO=item_user.ITEM_USER_NO))

    return GetChallengeUserDetail(
        CHALLENGE_USER_NO=challenge_user.CHALLENGE_USER_NO,
        USER_NM=user.USER_NM,
        CHARACTER_NO=character.AVATAR_NO,
        PROGRESS=calculate_user_progress(db, challenge_user_no),
        COMMENT=challenge_user.COMMENT,
        ITEM=item_list
    )


def get_challenge_history_list(db: Session, current_day: date, _current_user: User):
    challenges = get_active_challenges_for_user(db, _current_user.USER_NO, current_day)

    challenge_history_list = []
    for challenge in challenges:
        challenge_user = get_challenge_user_by_user_no(db, challenge.CHALLENGE_MST_NO, _current_user.USER_NO)
        daily_complete = db.query(PersonDailyGoalComplete).filter(
            PersonDailyGoalComplete.CHALLENGE_USER_NO == challenge_user.CHALLENGE_USER_NO,
            func.date(PersonDailyGoalComplete.INSERT_DT) == current_day
        ).first()
        daily_complete_users_list = []
        image_file = ''
        comment = ''

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
        team_goals = get_team_weekly_goal_by_user(db, challenge_user.CHALLENGE_MST_NO, current_day)

        challenge_history_list.append(GetChallengeHistory(
            CHALLENGE_MST_NO=challenge_user.CHALLENGE_MST_NO,
            CHALLENGE_MST_NM=get_challenge_master_by_id(db, challenge_user.CHALLENGE_MST_NO).CHALLENGE_MST_NM,
            IMAGE_FILE_NM=image_file,
            EMOJI=daily_complete_users_list,
            COMMENT=comment,
            personGoal=person_goal,
            teamGoal=[TeamWeeklyGoalPydantic.model_validate(team_goal) for team_goal in team_goals])
        )

    return challenge_history_list


# UID 정보를 가져와 CHALLENGE USER 업데이트 필요
def challenge_update(db: Session, challenge_mst_no: int, _challenge_update: ChallengeCreate, current_user: User):
    challenge = get_challenge_master_by_id(db, challenge_mst_no)
    challenge_user = get_challenge_user_by_user_no(db, challenge_mst_no, current_user.USER_NO)

    if not challenge_user.IS_OWNER:
        raise HTTPException(status_code=401, detail="수정 권한이 존재하지 않습니다.")

    # 챌린지 정보 업데이트
    challenge.CHALLENGE_MST_NM = _challenge_update.CHALLENGE_MST_NM
    challenge.START_DT = _challenge_update.START_DT
    challenge.END_DT = _challenge_update.END_DT
    challenge.HEADER_EMOJI = _challenge_update.HEADER_EMOJI
    challenge.INSERT_DT = _challenge_update.INSERT_DT

    db.commit()

    return {"message": "챌린지가 성공적으로 업데이트 되었습니다."}


# 삭제 시, 기존 챌린지 조회에 대한 예외처리 필요
def challenge_delete(db: Session, challenge_mst_no: int, current_user: User):
    challenge = get_challenge_master_by_id(db, challenge_mst_no)
    challenge_user = get_challenge_user_by_user_no(db, challenge_mst_no, current_user.USER_NO)

    if not challenge_user.IS_OWNER:
        raise HTTPException(status_code=401, detail="삭제 권한이 존재하지 않습니다.")

    challenge.DELETE_YN = True
    challenge.DELETE_DT = datetime.utcnow()

    return {"message": "챌린지가 성공적으로 삭제 되었습니다."}
