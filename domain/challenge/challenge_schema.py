from datetime import datetime, date

from pydantic import BaseModel
from typing import List, Optional

from models import ChallengeStatusType, InviteAcceptType


class ChallengeParticipant(BaseModel):
    UID: int
    USER_NM: str
    ACCEPT_STATUS: InviteAcceptType


class ChallengeUserList(BaseModel):
    CHALLENGE_USER_NO: int
    PROGRESS: float
    CHARACTER_NO: int
    PET_NO: Optional[int]

    class Config:
        from_attributes = True


class ChallengeUserListModel(BaseModel):
    CHALLENGE_MST_NO: int
    CHALLENGE_MST_NM: str
    challenge_user: list[ChallengeUserList]


class ChallengeMST(BaseModel):
    CHALLENGE_MST_NO: int
    CHALLENGE_MST_NM: str
    START_DT: datetime
    END_DT: datetime
    HEADER_EMOJI: str
    CHALLENGE_STATUS: ChallengeStatusType

    class Config:
        from_attributes = True


class ChallengeList(ChallengeMST):
    PROGRESS: Optional[float] = None


class ChallengeInvite(ChallengeMST):
    PARTICIPANTS: List[ChallengeParticipant]


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
    CHALLENGE_USER_NO: int

    class Config:
        from_attributes = True


class AdditionalGoalPydantic(BaseModel):
    ADDITIONAL_NO: int
    ADDITIONAL_NM: str
    IS_DONE: bool
    IMAGE_FILE_NM: Optional[str]
    START_DT: datetime
    END_DT: datetime
    CHALLENGE_USER_NO: int

    class Config:
        from_attributes = True


class ChallengeDetail(BaseModel):
    CHALLENGE_USER_NO: int
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

    # @validator('*', pre=True)
    # def not_empty(cls, value: Any, field) -> Any:
    #     if isinstance(value, str) and not value.strip():
    #         raise ValueError(f'{field.name} 필드에 빈 값은 허용 되지 않습니다.')
    #     return value


class PutChallengeInvite(BaseModel):
    CHALLENGE_MST_NO: int
    ACCEPT_STATUS: InviteAcceptType


class GetChallengeUserDetail(BaseModel):
    CHALLENGE_USER_NO: int
    USER_NM: str
    CHARACTER_NO: int
    PROGRESS: float
    COMMENT: str
    personGoal: List[PersonDailyGoalPydantic]


class EmojiUser(BaseModel):
    CHALLENGE_USER_NO: int
    EMOJI: str


class GetChallengeHistory(BaseModel):
    CHALLENGE_MST_NO: int
    CHALLENGE_MST_NM: str
    IMAGE_FILE_NM: Optional[str]
    EMOJI: Optional[List[EmojiUser]]
    COMMENT: Optional[str]
    personGoal: Optional[List[PersonDailyGoalPydantic]]
    teamGoal: Optional[List[TeamWeeklyGoalPydantic]]
