from datetime import datetime

from sqlalchemy.orm import Session

from domain.challenge.challenge_schema import ChallengeCreate
from models import ChallengeMaster


def get_challenge_list(db: Session):
    challenge_list = db.query(ChallengeMaster) \
        .all()
    return challenge_list


def create_challenge(db: Session, challenge_create: ChallengeCreate):
    db_challenge = ChallengeMaster(
        CHALLENGE_MST_NM=challenge_create.CHALLENGE_MST_NM,
        USER_ID=challenge_create.USER_ID,
        START_DT=challenge_create.START_DT,
        END_DT=challenge_create.END_DT,
        HEADER_EMOJI=challenge_create.HEADER_EMOJI,
        INSERT_DT=datetime.now(),
        INSERT_USER_ID=challenge_create.INSERT_USER_ID,
        CHALLENGE_STATUS=challenge_create.CHALLENGE_STATUS
    )
    db.add(db_challenge)
    db.commit()
