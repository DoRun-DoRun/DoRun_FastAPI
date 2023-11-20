from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.challenge import challenge_schema, challenge_crud
from domain.challenge.challenge_crud import get_challenge_list, get_challenge_detail
from domain.user.user_router import get_current_user
from models import User

router = APIRouter(
    prefix="/challenge",
    tags=["challenge"]
)


@router.get("/all", response_model=list[challenge_schema.Challenge])
def challenge_list(_current_user: User = Depends(get_current_user)):
    _challenge_list = get_challenge_list(current_user=_current_user)

    if not _challenge_list:
        raise HTTPException(status_code=404, detail="Challenges not found")

    return _challenge_list


@router.get("/{challenge_mst_no}", response_model=challenge_schema.Challenge)
def challenge_detail(challenge_mst_no: int, db: Session = Depends(get_db),
                     _current_user: User = Depends(get_current_user)):
    _challenge = get_challenge_detail(db, challenge_no=challenge_mst_no)

    if not _challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    return _challenge


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
def challenge_create(_challenge_create: challenge_schema.ChallengeCreate,
                     db: Session = Depends(get_db),
                     _current_user: User = Depends(get_current_user)):
    challenge_crud.create_challenge(db, challenge_create=_challenge_create,
                                    current_user=_current_user)
