from datetime import datetime

from pydantic import BaseModel, field_validator
from typing import List, Any

from pydantic.v1 import validator

from models import challenge_status


class Challenge(BaseModel):
    CHALLENGE_MST_NO: int
    CHALLENGE_MST_NM: str
    USER_ID: List[int]
    START_DT: datetime
    END_DT: datetime
    HEADER_EMOJI: str
    INSERT_DT: datetime
    INSERT_USER_ID: int
    CHALLENGE_STATUS: challenge_status


class ChallengeCreate(BaseModel):
    CHALLENGE_MST_NM: str
    USER_ID: List[int]
    START_DT: datetime
    END_DT: datetime
    HEADER_EMOJI: str
    INSERT_DT: datetime
    INSERT_USER_ID: int
    CHALLENGE_STATUS: challenge_status

    @validator('*', pre=True)
    def not_empty(cls, value: Any, field) -> Any:
        if isinstance(value, str) and not value.strip():
            raise ValueError(f'{field.name} 필드에 빈 값은 허용 되지 않습니다.')
        return value
