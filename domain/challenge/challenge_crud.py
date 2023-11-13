from datetime import datetime

from sqlalchemy.orm import Session

from domain.challenge.challenge_schema import ChallengeCreate
from models import ChallengeMaster, User


def get_challenge_list(db: Session):
    challenge_list = db.query(ChallengeMaster) \
        .all()
    return challenge_list


def create_challenge(db: Session, challenge_create: ChallengeCreate, current_user: User):
    db_challenge = ChallengeMaster(
        CHALLENGE_MST_NM=challenge_create.CHALLENGE_MST_NM,
        USERS_UID=challenge_create.USERS_ID,
        START_DT=challenge_create.START_DT,
        END_DT=challenge_create.END_DT,
        HEADER_EMOJI=challenge_create.HEADER_EMOJI,
        INSERT_DT=datetime.now(),
        CHALLENGE_STATUS=challenge_create.CHALLENGE_STATUS,
        user=current_user
    )
    db.add(db_challenge)
    db.commit()
