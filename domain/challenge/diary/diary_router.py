from datetime import datetime, timedelta
from random import choice

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import not_, and_, func
from sqlalchemy.orm import Session

from database import get_db
from domain.challenge import challenge_crud
from domain.challenge.challenge_crud import get_challenge_user_by_challenge_user_no
from domain.challenge.diary import diary_crud
from domain.challenge.diary.diary_schema import CreateDiary
from domain.desc.utils import select_randomly_with_probability, RewardType, get_random_item, \
    get_random_avatar_not_owned_by_user
from domain.user.user_crud import get_current_user
from models import User, DailyCompleteUser, PersonDailyGoalComplete, ChallengeUser, ItemUser, AvatarUser, Avatar, \
    PersonDailyGoal

router = APIRouter(
    prefix="/diary",
    tags=["Diary"]
)


@router.post("/emoji/{daily_complete_no}")
def post_emoji(daily_complete_no: int, emoji: str, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    diary = diary_crud.get_diary(db, daily_complete_no)

    challenge_user = challenge_crud.get_challenge_user_by_user_no(db, diary.CHALLENGE_USER.CHALLENGE_MST_NO,
                                                                  current_user.USER_NO)

    if not challenge_user:
        raise HTTPException(status_code=404, detail="챌린지 유저를 찾을 수 없습니다.")

    db_emoji = DailyCompleteUser(EMOJI=emoji, DAILY_COMPLETE_NO=daily_complete_no, CHALLENGE_USER=challenge_user)
    db.add(db_emoji)

    db.commit()

    return {"message": "이모지 전송 성공"}


@router.get("/{daily_complete_no}")
def get_diary(daily_complete_no: int, db: Session = Depends(get_db)):
    diary = diary_crud.get_diary(db, daily_complete_no)

    challenge_user = get_challenge_user_by_challenge_user_no(db, challenge_user_no=diary.CHALLENGE_USER_NO)

    person_goals = db.query(PersonDailyGoal).filter(PersonDailyGoal.DAILY_COMPLETE_NO == daily_complete_no).all()

    goals_data = [{
        "PERSON_NM": goal.PERSON_NM,
        "IS_DONE": goal.IS_DONE
    } for goal in person_goals]

    return {"diary": diary, "user": challenge_user.USER.USER_NM, "goals": goals_data}


@router.post("")
def create_diary(_create_diary: CreateDiary, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    challenge_user = challenge_crud.get_challenge_user_by_challenge_user_no(db, _create_diary.CHALLENGE_USER_NO)

    if challenge_user.USER_NO != current_user.USER_NO:
        raise HTTPException(status_code=401, detail="현재 접속중인 유저와 Challenge_user가 다릅니다.")

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

    if existing_diary:
        raise HTTPException(status_code=400, detail="오늘 이미 일기가 작성되었습니다.")

    db_diary = PersonDailyGoalComplete(
        IMAGE_FILE_NM=_create_diary.IMAGE_FILE_NM,
        COMMENT=_create_diary.COMMENT,
        CHALLENGE_USER=challenge_user
    )
    db.add(db_diary)

    db.commit()

    for person_goal in _create_diary.PERSON_GOAL:
        db_person_goal = PersonDailyGoal(
            PERSON_NM=person_goal.PERSON_NM,
            IS_DONE=person_goal.IS_DONE,
            CHALLENGE_USER=challenge_user,
            DAILY_COMPLETE=db_diary
        )
        db.add(db_person_goal)

    # 아이템 50%, 꽝 50%
    select_item_type = select_randomly_with_probability(0, 70, 30, 0)
    select_item = 0

    if select_item_type == RewardType.ITEM:
        item = get_random_item(db)
        item_user = db.query(ItemUser).filter(
            ItemUser.CHALLENGE_USER_NO == challenge_user.CHALLENGE_USER_NO,
            ItemUser.ITEM_NO == item.ITEM_NO).first()
        if not item_user:
            raise HTTPException(status_code=404, detail="사용자 아이템 정보가 없습니다.")
        item_user.COUNT += 1
        select_item = item.ITEM_NO

    if select_item_type == RewardType.AVATAR:
        avatar = get_random_avatar_not_owned_by_user(db, current_user.USER_NO)
        if not avatar:
            select_item_type = RewardType.NOTHING
            db.commit()
            return {"message": "일기 생성 완료", "item_type": select_item_type, "item_no": select_item}

        select_item = avatar.AVATAR_NO
        db_avatar_user = AvatarUser(AVATAR_NO=avatar.AVATAR_NO, USER_NO=current_user.USER_NO, IS_EQUIP=False)
        db.add(db_avatar_user)

    db.commit()

    return {"message": "일기 생성 완료", "item_type": select_item_type, "item_no": select_item}
