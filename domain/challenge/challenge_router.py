from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.challenge import challenge_schema, challenge_crud
from domain.challenge.challenge_crud import get_challenge_list, get_challenge_pending, get_challenge_detail
from domain.user.user_crud import get_current_user
from models import User

router = APIRouter(
    prefix="/challenge",
    tags=["challenge"]
)


@router.get("/all", response_model=list[challenge_schema.ChallengeAll])
def challenge_list(db: Session = Depends(get_db),
                   _current_user: User = Depends(get_current_user)):
    _challenge_list = get_challenge_list(db, _current_user)

    if not _challenge_list:
        raise HTTPException(status_code=404, detail="Challenges not found")

    return _challenge_list


@router.get("/pending/{challenge_mst_no}", response_model=challenge_schema.ChallengePending)
def challenge_pending(challenge_mst_no: int, db: Session = Depends(get_db)):
    _challenge = get_challenge_pending(db, challenge_no=challenge_mst_no)

    if not _challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    return _challenge


@router.get("/detail/{challenge_mst_no}", response_model=challenge_schema.ChallengeDetail)
def challenge_detail(challenge_mst_no: int, db: Session = Depends(get_db),
                     _current_user: User = Depends(get_current_user)):
    _challenge = get_challenge_detail(db, user_no=_current_user.USER_NO, challenge_mst_no=challenge_mst_no)

    if not _challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    return _challenge


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
def challenge_create(_challenge_create: challenge_schema.ChallengeCreate,
                     db: Session = Depends(get_db),
                     _current_user: User = Depends(get_current_user)):
    challenge_crud.create_challenge(db, challenge_create=_challenge_create,
                                    current_user=_current_user)
