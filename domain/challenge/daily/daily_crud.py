from datetime import datetime

from sqlalchemy.orm import Session

from domain.challenge.daily.daily_schema import CompleteDailyGoal
from models import User, ChallengeMaster, DailyComplete


def complete_daily_goal(db: Session,
                        complete_daily: CompleteDailyGoal,
                        current_user: User,
                        current_challenge: ChallengeMaster):
    db_daily = DailyComplete(
        AUTH_IMAGE_FILE_NM=complete_daily.AUTH_IMAGE_FILE_NM,
        COMMENTS=complete_daily.COMMENTS,
        CHALLENGE=current_challenge,
        USER=current_user,
    )
    db.add(db_daily)
    db.commit()
