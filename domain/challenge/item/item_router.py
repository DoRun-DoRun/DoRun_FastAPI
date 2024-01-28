from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from domain.challenge import challenge_crud
from domain.challenge.item.item_crud import used_item, get_item
from domain.user.user_crud import get_current_user, get_equipped_avatar
from models import User, ChallengeMaster, ChallengeStatusType, ChallengeUser, ItemUser, ItemLog, AvatarType

router = APIRouter(
    prefix="/item",
    tags=["Item"]
)


@router.post("")
def use_item(challenge_user_no: int, db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user)):
    message = get_item(db, current_user, challenge_user_no)

    return message


@router.post("/{recipient_no}")
def use_item(item_no: int, recipient_no: int, db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user)):
    message = used_item(db, item_no, recipient_no, current_user)

    return message


@router.get("/log/{challenge_mst_no}")
def get_item_log(challenge_mst_no: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    challenge_user = challenge_crud.get_challenge_user_by_user_no(db, challenge_mst_no, current_user.USER_NO)

    twenty_four_hours_ago = datetime.now() - timedelta(hours=24)

    item_logs = db.query(ItemLog).filter(
        ItemLog.RECIPIENT_NO == challenge_user.CHALLENGE_USER_NO,
        ItemLog.IS_VIEW == False,
        ItemLog.INSERT_DT >= twenty_four_hours_ago,  # INSERT_DT가 최근 24시간 이내
    ).all()

    item_log_data = []

    for item_log in item_logs:
        send_user = item_log.sender.USER
        character = get_equipped_avatar(db, send_user.USER_NO, AvatarType.CHARACTER)
        item_log_data.append(
            {"ITEM_NO": item_log.ITEM_NO, "ITEM_LOG_NO": item_log.ITEM_LOG_NO, "INSERT_DT": item_log.INSERT_DT,
             "send_USER_NM": send_user.USER_NM, "send_CHARACTER_NO": character.AVATAR_NO})

    return item_log_data


@router.put("/log/{item_log_no}")
def update_item_log(item_log_no: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item_log = db.query(ItemLog).filter(ItemLog.ITEM_LOG_NO == item_log_no).first()

    if item_log.recipient.USER_NO != current_user.USER_NO:
        raise HTTPException(status_code=401, detail="업데이트 권한이 없습니다.")

    item_log.IS_VIEW = True
    db.commit()

    return {"message": "update 성공"}
