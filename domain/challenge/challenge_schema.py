from datetime import datetime, date

from pydantic import BaseModel
from typing import List, Any, Dict

from pydantic.v1 import validator

from domain.user.user_schema import User
from models import ChallengeStatus


class Challenge(BaseModel):
    CHALLENGE_MST_NO: int
    CHALLENGE_MST_NM: str
    USERS_UID: List[int]
    START_DT: datetime
    END_DT: datetime
    HEADER_EMOJI: str
    CHALLENGE_STATUS: ChallengeStatus
    USER_UID: int


class ChallengeCreate(BaseModel):
    CHALLENGE_MST_NM: str
    USERS_UID: List[int]
    START_DT: date
    END_DT: date
    HEADER_EMOJI: str
    INSERT_DT: datetime
    CHALLENGE_STATUS: ChallengeStatus

    @validator('*', pre=True)
    def not_empty(cls, value: Any, field) -> Any:
        if isinstance(value, str) and not value.strip():
            raise ValueError(f'{field.name} 필드에 빈 값은 허용 되지 않습니다.')
        return value


class CompleteDailyGoal(BaseModel):
    AUTH_IMAGE_FILE_NM: str
    CHALLENGE_MST_NO: int
    COMMENTS: str
    PERSON_GOAL_LIST: List[Dict[str, str]]


class CompleteWeeklyGoal(BaseModel):
    CHALLENGE_MST_NO: int

