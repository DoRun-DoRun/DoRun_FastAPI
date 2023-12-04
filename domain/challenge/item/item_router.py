from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from domain.challenge import challenge_crud
from domain.user.user_crud import get_current_user
from models import User, ItemUser, ItemLog

router = APIRouter(
    prefix="/item",
    tags=["Item"]
)


@router.post("/{recipient_no}")
def use_item(item_no: int, challenge_user_no: int, recipient_no: int, db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user)):
    challenge_user = challenge_crud.get_challenge_user_by_challenge_user_no(db, challenge_user_no)
    if challenge_user.USER_NO != current_user.USER_NO:
        raise HTTPException(status_code=401, detail="사용 권한이 없습니다.")

    item_user = db.query(ItemUser).filter(challenge_user_no == ItemUser.CHALLENGE_USER_NO,
                                          item_no == ItemUser.ITEM_NO).first()

    if not item_user:
        raise HTTPException(status_code=404, detail="Item_User가 존재하지 않습니다")

    if item_user.COUNT == 0:
        raise HTTPException(status_code=404, detail="사용할 아이템이 존재하지 않습니다")

    item_user.COUNT -= 1
    db_item_log = ItemLog(SENDER_NO=challenge_user.CHALLENGE_USER_NO, RECIPIENT_NO=recipient_no, ITEM_NO=item_no)
    db.add(db_item_log)
    db.commit()

    return {"message": "아이템 사용 성공"}
