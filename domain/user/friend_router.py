from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from database import get_db
from domain.user import user_crud
from domain.user.friend_schema import FriendListResponse
from domain.user.user_crud import get_current_user
from models import User, Friend, InviteAcceptType

router = APIRouter(
    prefix="/friend",
    tags=["Friend"]
)


@router.post("/{uid}")
def invite_friend(uid: int, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    recipient_user = user_crud.get_user_by_uid(db, uid)

    # 이미 친구 요청이 존재하는지 확인
    existing_request = db.query(Friend).filter(
        or_(
            (Friend.SENDER_NO == current_user.USER_NO) & (Friend.RECIPIENT_NO == recipient_user.USER_NO),
            (Friend.SENDER_NO == recipient_user.USER_NO) & (Friend.RECIPIENT_NO == current_user.USER_NO)
        ),
        Friend.ACCEPT_STATUS != InviteAcceptType.DECLINED
    ).first()

    if existing_request.ACCEPT_STATUS == InviteAcceptType.ACCEPTED:
        raise HTTPException(status_code=404, detail="이미 친구인 상태입니다.")

    if existing_request.ACCEPT_STATUS == InviteAcceptType.PENDING:
        raise HTTPException(status_code=404, detail="이미 친구요청이 보내진 상태입니다.")

    # 새로운 친구 요청 생성
    db_friend = Friend(SENDER_NO=current_user.USER_NO, RECIPIENT_NO=recipient_user.USER_NO)
    db.add(db_friend)
    db.commit()

    return {"message": "친구요청 성공!"}


@router.get("/list", response_model=FriendListResponse)
def get_friend_list(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 친구 목록 조회
    friend_records = db.query(Friend).filter(
        or_(Friend.SENDER_NO == current_user.USER_NO, Friend.RECIPIENT_NO == current_user.USER_NO)
    ).all()

    # 각 상태에 따른 친구 목록 필터링 및 필요한 정보 추출
    pending_friends = []
    accepted_friends = []

    for record in friend_records:
        friend_user_no = record.SENDER_NO if record.RECIPIENT_NO == current_user.USER_NO else record.RECIPIENT_NO
        friend_user = db.query(User).filter(User.USER_NO == friend_user_no).first()

        if friend_user:
            friend_data = {"UID": friend_user.UID, "USER_NM": friend_user.USER_NM}
            if record.ACCEPT_STATUS == InviteAcceptType.PENDING:
                pending_friends.append(friend_data)
            elif record.ACCEPT_STATUS == InviteAcceptType.ACCEPTED:
                accepted_friends.append(friend_data)

    return {"pending": pending_friends, "accepted": accepted_friends}


@router.put("/{friend_no}")
def update_friend(friend_no: int, status: InviteAcceptType, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    friend = db.query(Friend).filter(Friend.FRIEND_NO == friend_no).first()

    if not friend:
        raise HTTPException(status_code=404, detail="친구 정보를 찾을 수 없습니다.")

    if not (friend.SENDER_NO == current_user.USER_NO or friend.RECIPIENT_NO == current_user.USER_NO):
        raise HTTPException(status_code=401, detail="수정 권한이 없습니다.")

    friend.ACCEPT_STATUS = status

    db.commit()

    return {"message": "친구상태 업데이트 성공"}
