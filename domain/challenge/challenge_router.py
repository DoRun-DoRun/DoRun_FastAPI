from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.challenge import challenge_schema, challenge_crud
from models import ChallengeMaster

router = APIRouter(
    prefix="/api/challenge",
)


@router.get("/list", response_model=list[challenge_schema.Challenge])
def challenge_list(db: Session = Depends(get_db)):
    _challenge_list = challenge_crud.get_challenge_list(db)
    return _challenge_list


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
def challenge_create(_challenge_create: challenge_schema.ChallengeCreate,
                     db: Session = Depends(get_db)):
    challenge_crud.create_challenge(db=db, challenge_create=_challenge_create)
