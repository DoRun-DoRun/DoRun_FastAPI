import random
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query
from sqlalchemy.orm import Session

from database import get_db
from domain.challenge import challenge_schema, challenge_crud
from domain.challenge.challenge_crud import get_challenge_list, get_challenge_detail, \
    get_challenge_invite, get_challenge_user_by_user_no, start_challenge, calculate_user_progress, \
    get_challenge_participants, get_challenge_master_by_id
from domain.challenge.challenge_schema import ChallengeInvite, PutChallengeInvite
from domain.desc.utils import get_random_avatar_not_owned_by_user, RewardType, select_randomly_with_probability
from domain.user.user_crud import get_current_user
from models import User, ChallengeUser, ChallengeMaster, ChallengeStatusType, AvatarUser, InviteAcceptType

router = APIRouter(
    prefix="/challenge",
    tags=["Challenge"]
)


@router.get("/list", response_model=challenge_schema.ChallengeList)
def challenge_list(db: Session = Depends(get_db),
                   _current_user: User = Depends(get_current_user)):
    _challenge_list = get_challenge_list(db, _current_user)

    return _challenge_list


@router.get("/detail/{challenge_mst_no}", response_model=challenge_schema.ChallengeDetail)
def challenge_detail(challenge_mst_no: int, db: Session = Depends(get_db),
                     _current_user: User = Depends(get_current_user)):
    _challenge = get_challenge_detail(db, user_no=_current_user.USER_NO, challenge_mst_no=challenge_mst_no)

    return _challenge


@router.post("")
def challenge_create(_challenge_create: challenge_schema.ChallengeCreate,
                     db: Session = Depends(get_db),
                     _current_user: User = Depends(get_current_user)):
    if len(_challenge_create.USERS_UID) > 6:
        raise HTTPException(status_code=404, detail="참가 가능한 최대 인원은 6명 입니다.")

    _challenge_list = get_challenge_list(db, _current_user)

    if len(_challenge_list["progress_challenges"]) >= 3:
        raise HTTPException(status_code=404, detail="참가 가능한 챌린지는 3개입니다.")

    challenge = challenge_crud.post_create_challenge(db, challenge_create=_challenge_create,
                                                     current_user=_current_user)
    db.refresh(challenge)
    return challenge


@router.post("/start")
def challenge_start(challenge_mst_no: int, start_dt: datetime, db: Session = Depends(get_db),
                    current_user=Depends(get_current_user)):
    message = start_challenge(db, challenge_mst_no, current_user, start_dt)
    return message


@router.put("/{challenge_mst_no}")
def challenge_update(challenge_mst_no: int, _challenge_update: challenge_schema.ChallengeCreate,
                     db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    message = challenge_crud.challenge_update(db, challenge_mst_no, _challenge_update, current_user)
    return message


@router.put("/link/{challenge_mst_no}")
def challenge_update(challenge_mst_no: int,
                     db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    challenge = get_challenge_master_by_id(db, challenge_mst_no)

    if challenge.CHALLENGE_STATUS != ChallengeStatusType.PENDING:
        return {"message": "참가할 수 없는 챌린지 입니다."}

    existing_user_ids = {cu.USER.USER_NO for cu in challenge.USERS}

    if current_user.USER_NO in existing_user_ids:
        return {"message": "이미 존재하는 유저입니다."}
    else:
        db_challenge_user = ChallengeUser(
            CHALLENGE_MST=challenge,
            USER=current_user,
            IS_OWNER=False,
            ACCEPT_STATUS=InviteAcceptType.PENDING
        )
        db.add(db_challenge_user)
        db.commit()

        count = db.query(ChallengeMaster).join(
            ChallengeUser,
            ChallengeMaster.CHALLENGE_MST_NO == ChallengeUser.CHALLENGE_MST_NO
        ).filter(
            ChallengeUser.USER_NO == current_user.USER_NO,
            ChallengeUser.ACCEPT_STATUS == InviteAcceptType.ACCEPTED,
            ChallengeMaster.CHALLENGE_STATUS != ChallengeStatusType.COMPLETE,
            ChallengeMaster.DELETE_YN == False
        ).count()

        return {"message": "참가 성공", "challenge": challenge_mst_no, "challenge_count": count}


@router.delete("/{challenge_mst_no}")
def challenge_delete(challenge_mst_no: int, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    message = challenge_crud.challenge_delete(db, challenge_mst_no, current_user)
    return message


@router.get("/user/list", response_model=challenge_schema.ChallengeUserListModel)
def get_challenge_user_list(db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
                            page: int = Query(1, description="페이지 번호")):
    if page < 1:
        raise HTTPException(status_code=404, detail="페이지 숫자는 0보다 커야합니다.")
    challenge_user_list_data = challenge_crud.get_challenge_user_list(db, current_user, page)

    return challenge_user_list_data


@router.get("/user/{challenge_user_no}", response_model=challenge_schema.GetChallengeUserDetail)
def get_challenge_user_detail(challenge_user_no: int, db: Session = Depends(get_db),
                              current_user: User = Depends(get_current_user)):
    challenge_user_detail = challenge_crud.get_challenge_user_detail(db, challenge_user_no, current_user)

    return challenge_user_detail


@router.put("/user/{challenge_user_no}")
def put_challenge_user_detail(challenge_user_no: int, comment: str, db: Session = Depends(get_db),
                              current_user: User = Depends(get_current_user)):
    challenge_user = challenge_crud.get_challenge_user_by_challenge_user_no(db, challenge_user_no)

    if challenge_user.USER_NO != current_user.USER_NO:
        raise HTTPException(status_code=401, detail="수정 권한이 없습니다.")

    challenge_user.COMMENT = comment
    db.commit()
    db.refresh(challenge_user)

    return {"message": "상태메시지 수정완료", "challenge_user": challenge_user}


@router.get("/invite/{challenge_mst_no}", response_model=ChallengeInvite)
def challenge_invite(challenge_mst_no: int, db: Session = Depends(get_db),
                     _current_user: User = Depends(get_current_user)):
    challenge_info = get_challenge_invite(db, challenge_mst_no, _current_user)

    return challenge_info


@router.put("/invite/{challenge_mst_no}")
def challenge_invite(put_challenge_invite: PutChallengeInvite, db: Session = Depends(get_db),
                     _current_user: User = Depends(get_current_user)):
    challenge_user = get_challenge_user_by_user_no(db, put_challenge_invite.CHALLENGE_MST_NO, _current_user.USER_NO)

    if put_challenge_invite.ACCEPT_STATUS == InviteAcceptType.DECLINED:
        db.delete(challenge_user)
        db.commit()
        return {"message": "초대상태 수정완료", "challenge_user": None, "status": put_challenge_invite.ACCEPT_STATUS}

    _challenge_list = get_challenge_list(db, _current_user)

    if len(_challenge_list["progress_challenges"]) >= 3:
        raise HTTPException(status_code=404, detail="참가 가능한 챌린지는 3개입니다.")

    challenge_user.ACCEPT_STATUS = put_challenge_invite.ACCEPT_STATUS
    db.commit()

    db.refresh(challenge_user)

    return {"message": "초대상태 수정완료", "challenge_user": challenge_user, "status": put_challenge_invite.ACCEPT_STATUS}


@router.get("/history", response_model=challenge_schema.GetChallengeHistory)
def get_challenge_history_list(current_day: datetime, page: int = Query(1, description="페이지 번호"),
                               db: Session = Depends(get_db),
                               _current_user: User = Depends(get_current_user)):
    challenge_history_list = challenge_crud.get_challenge_history_list(db, current_day, _current_user, page)
    return challenge_history_list


@router.get("/log")
def get_challenge_log(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    completed_challenge_users = db.query(ChallengeUser).join(
        ChallengeMaster, ChallengeUser.CHALLENGE_MST_NO == ChallengeMaster.CHALLENGE_MST_NO
    ).filter(
        ChallengeMaster.CHALLENGE_STATUS == ChallengeStatusType.COMPLETE,
        ChallengeUser.USER_NO == current_user.USER_NO,
        ChallengeUser.IS_VIEW == False,
    ).all()

    completed_challenges_data = []

    for completed_challenge_user in completed_challenge_users:
        challenge_users = get_challenge_participants(db, completed_challenge_user.CHALLENGE_MST.CHALLENGE_MST_NO)
        challenge_users_data = []
        challenge = completed_challenge_user.CHALLENGE_MST

        for challenge_user in challenge_users:
            challenge_users_data.append({"USER_NM": challenge_user.User.USER_NM,
                                         "progress": calculate_user_progress(db,
                                                                             completed_challenge_user.CHALLENGE_USER_NO)})

        completed_challenges_data.append(
            {"CHALLENGE_MST_NM": completed_challenge_user.CHALLENGE_MST.CHALLENGE_MST_NM,
             "CHALLENGE_MST_NO": challenge.CHALLENGE_MST_NO,
             "CHALLENGE_USER_NO": completed_challenge_user.CHALLENGE_USER_NO,
             "START_DT": challenge.START_DT,
             "END_DT": challenge.END_DT,
             "participants": challenge_users_data})
    db.commit()
    return completed_challenges_data


@router.put("/log/{challenge_user_no}")
def update_challenge_log(challenge_user_no: int, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    challenge_user = challenge_crud.get_challenge_user_by_challenge_user_no(db, challenge_user_no)

    if challenge_user.USER_NO != current_user.USER_NO:
        raise HTTPException(status_code=401, detail="업데이트 권한이 없습니다.")

    challenge_user.IS_VIEW = True

    duration = (challenge_user.CHALLENGE_MST.END_DT - challenge_user.CHALLENGE_MST.START_DT).days

    challenge_user_count = db.query(ChallengeUser).filter(
        ChallengeUser.CHALLENGE_MST_NO == challenge_user.CHALLENGE_MST_NO).count()

    avatar_type = select_randomly_with_probability(50 + challenge_user_count * 5, 0, 50 - challenge_user_count * 5,
                                                   duration)

    avatar = None

    if avatar_type == RewardType.AVATAR:
        avatar = get_random_avatar_not_owned_by_user(db, current_user.USER_NO)

        if avatar:
            db_avatar_user = AvatarUser(AVATAR_NO=avatar.AVATAR_NO, USER_NO=current_user.USER_NO, IS_EQUIP=False)
            db.add(db_avatar_user)
        else:
            avatar_type = RewardType.NOTHING

    db.commit()

    return {"message": "업데이트 성공", "AVATAR_NO": avatar.AVATAR_NO if avatar is not None else None,
            "AVATAR_TYPE": avatar_type}
