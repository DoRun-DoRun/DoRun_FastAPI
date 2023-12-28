from datetime import datetime, date

from pydantic import BaseModel, Field
from typing import List, Optional

from models import ChallengeStatusType, InviteAcceptType, ItemType
from enum import Enum


class ChallengeParticipant(BaseModel):
    UID: int
    USER_NM: str
    ACCEPT_STATUS: InviteAcceptType


class DiaryPydantic(BaseModel):
    DAILY_COMPLETE_NO: int

    class Config:
        from_attributes = True


class ItemPydantic(BaseModel):
    ITEM_NO: int
    ITEM_NM: ItemType
    ITEM_USER_NO: int
    COUNT: int


class ChallengeUserList(BaseModel):
    CHALLENGE_USER_NO: int
    PROGRESS: float
    CHARACTER_NO: int
    PET_NO: Optional[int]
    DIARIES: Optional[List[DiaryPydantic]]

    class Config:
        from_attributes = True


class ChallengeUserListModel(BaseModel):
    CHALLENGE_MST_NO: Optional[int] = Field(None)
    CHALLENGE_MST_NM: Optional[str] = Field(None)
    challenge_user: Optional[List[ChallengeUserList]] = Field(None)
    total_page: Optional[int] = Field(0)


class ChallengeMST(BaseModel):
    CHALLENGE_MST_NO: int
    CHALLENGE_MST_NM: str
    START_DT: datetime
    END_DT: datetime
    HEADER_EMOJI: str
    CHALLENGE_STATUS: ChallengeStatusType

    class Config:
        from_attributes = True


class ChallengeMSTProgress(ChallengeMST):
    PROGRESS: Optional[float] = None


class ChallengeList(BaseModel):
    progress_challenges: Optional[List[ChallengeMSTProgress]]
    invited_challenges: Optional[List[ChallengeMSTProgress]]


class ChallengeInvite(ChallengeMST):
    IS_OWNER: bool
    PARTICIPANTS: List[ChallengeParticipant]


class PersonDailyGoalPydantic(BaseModel):
    PERSON_NO: int
    PERSON_NM: Optional[str]
    IS_DONE: bool

    class Config:
        from_attributes = True


# class TeamWeeklyGoalPydantic(BaseModel):
#     TEAM_NO: int
#     TEAM_NM: str
#     IS_DONE: bool
#     CHALLENGE_USER_NO: int
#
#     class Config:
#         from_attributes = True


class AdditionalGoalPydantic(BaseModel):
    ADDITIONAL_NO: int
    ADDITIONAL_NM: str
    IS_DONE: bool
    IMAGE_FILE_NM: Optional[str]
    START_DT: datetime
    END_DT: datetime
    CHALLENGE_USER_NO: int
    CHALLENGE_USER_NN: str
    IS_MINE: bool

    class Config:
        from_attributes = True


class ChallengeDetail(BaseModel):
    CHALLENGE_USER_NO: int
    CHALLENGE_STATUS: ChallengeStatusType
    # teamGoal: List[TeamWeeklyGoalPydantic]
    additionalGoal: List[AdditionalGoalPydantic]


class UserUID(BaseModel):
    USER_UID: int
    INVITE_STATS: InviteAcceptType


class ChallengeCreate(BaseModel):
    CHALLENGE_MST_NM: str
    USERS_UID: List[UserUID]
    START_DT: datetime
    END_DT: datetime
    HEADER_EMOJI: str

    # @validator('*', pre=True)
    # def not_empty(cls, value: Any, field) -> Any:
    #     if isinstance(value, str) and not value.strip():
    #         raise ValueError(f'{field.name} 필드에 빈 값은 허용 되지 않습니다.')
    #     return value


class PutChallengeInvite(BaseModel):
    CHALLENGE_MST_NO: int
    ACCEPT_STATUS: InviteAcceptType


class UserStatus(Enum):
    SLEEPING = "자는중"
    WALKING = "걷는중"
    RUNNING = "뛰는중"


class GetChallengeUserDetail(BaseModel):
    CHALLENGE_USER_NO: int
    USER_NM: str
    CHARACTER_NO: int
    # PROGRESS: float
    COMMENT: str
    ITEM: List[ItemPydantic]
    STATUS: UserStatus
    IS_ME: bool


class EmojiUser(BaseModel):
    CHALLENGE_USER_NO: int
    EMOJI: str


class GetChallengeHistory(BaseModel):
    CHALLENGE_MST_NO: Optional[int]
    CHALLENGE_MST_NM: Optional[str]
    IMAGE_FILE_NM: Optional[str]
    EMOJI: Optional[List[EmojiUser]]
    COMMENT: Optional[str]
    personGoal: Optional[List[PersonDailyGoalPydantic]]
    # teamGoal: Optional[TeamWeeklyGoalPydantic]
    total_size: int
