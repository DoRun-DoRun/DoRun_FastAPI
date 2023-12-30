from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from domain.challenge import challenge_crud
from domain.challenge.challenge_crud import get_challenge_user_by_user_no
from domain.user.user_crud import get_current_user
from models import User, ItemUser, ItemLog, AdditionalGoal, PersonDailyGoal, AvatarType

router = APIRouter(
    prefix="/item",
    tags=["Item"]
)


@router.post("/{recipient_no}")
def use_item(item_no: int, recipient_no: int, db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user)):
    target_user = challenge_crud.get_challenge_user_by_challenge_user_no(db, recipient_no)

    # 현재 UTC 시간
    current_utc_time = datetime.utcnow()

    # ChallengeMaster의 종료 시간
    end_time = target_user.CHALLENGE_MST.END_DT

    # 남은 시간 계산 (초 단위)
    time_remaining = (end_time - current_utc_time).total_seconds()

    # 남은 시간이 24시간 미만인 경우 오류 처리
    if time_remaining < 86400:
        raise HTTPException(status_code=402, detail="남은 시간이 24시간 미만입니다.")

    used_user = get_challenge_user_by_user_no(db, target_user.CHALLENGE_MST_NO, current_user.USER_NO)

    if target_user == used_user:
        raise HTTPException(status_code=404, detail="본인에게는 사용할 수 없습니다.")

    item_user = db.query(ItemUser).filter(used_user.CHALLENGE_USER_NO == ItemUser.CHALLENGE_USER_NO,
                                          item_no == ItemUser.ITEM_NO).first()

    if not item_user:
        raise HTTPException(status_code=404, detail="Item_User가 존재하지 않습니다")

    if item_user.COUNT == 0:
        raise HTTPException(status_code=404, detail="사용할 아이템이 존재하지 않습니다")

    item_user.COUNT -= 1
    db_item_log = ItemLog(SENDER_NO=used_user.CHALLENGE_USER_NO, RECIPIENT_NO=recipient_no, ITEM_NO=item_no)
    db.add(db_item_log)

    if item_no == 1:
        person_goal = db.query(PersonDailyGoal).filter(
            PersonDailyGoal.CHALLENGE_USER_NO == used_user.CHALLENGE_USER_NO,
        ).order_by(func.random()).first()

        db_additional_goal = AdditionalGoal(ADDITIONAL_NM=person_goal.PERSON_NM, CHALLENGE_USER_NO=recipient_no)
        db.add(db_additional_goal)

    db.commit()

    my_avatar = challenge_crud.get_equipped_avatar(db, current_user.USER_NO, AvatarType.CHARACTER).AVATAR_NO

    return {"message": "아이템 사용 성공", "item_no": item_no, "character_no": my_avatar}
