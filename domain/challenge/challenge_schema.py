from datetime import datetime, date

from pydantic import BaseModel
from typing import List, Optional

from models import ChallengeStatus, AcceptType


class ChallengeParticipant(BaseModel):
    UID: int
    ACCEPT_STATUS: Optional[AcceptType]


class Challenge(BaseModel):
    CHALLENGE_MST_NO: int
    CHALLENGE_MST_NM: str
    START_DT: datetime
    END_DT: datetime
    HEADER_EMOJI: str
    CHALLENGE_STATUS: ChallengeStatus
    PROGRESS: Optional[float] = None
    PARTICIPANTS: Optional[List[ChallengeParticipant]] = None

    class Config:
        from_attributes = True


class PersonDailyGoalPydantic(BaseModel):
    PERSON_NO: int
    PERSON_NM: Optional[str]
    IS_DONE: bool

    class Config:
        from_attributes = True


class TeamWeeklyGoalPydantic(BaseModel):
    TEAM_NO: int
    TEAM_NM: str
    IS_DONE: bool

    class Config:
        from_attributes = True


class AdditionalGoalPydantic(BaseModel):
    ADDITIONAL_NO: int
    ADDITIONAL_NM: str
    IS_DONE: bool
    IMAGE_FILE_NM: Optional[str]
    START_DT: datetime
    END_DT: datetime

    class Config:
        from_attributes = True


class ChallengeDetail(BaseModel):
    CHALLENGE_USER_NO: int
    challenge: Challenge
    personGoal: List[PersonDailyGoalPydantic]
    teamGoal: List[TeamWeeklyGoalPydantic]
    additionalGoal: List[AdditionalGoalPydantic]


class ChallengeCreate(BaseModel):
    CHALLENGE_MST_NM: str
    USERS_UID: List[int]
    START_DT: date
    END_DT: date
    HEADER_EMOJI: str
    INSERT_DT: datetime
    CHALLENGE_STATUS: ChallengeStatus

    # @validator('*', pre=True)
    # def not_empty(cls, value: Any, field) -> Any:
    #     if isinstance(value, str) and not value.strip():
    #         raise ValueError(f'{field.name} 필드에 빈 값은 허용 되지 않습니다.')
    #     return value
