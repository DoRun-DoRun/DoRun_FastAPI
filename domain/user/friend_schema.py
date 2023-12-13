from pydantic import BaseModel
from typing import List, Optional


class FriendInfo(BaseModel):
    UID: int
    USER_NM: str
    FRIEND_NO: int


class FriendListResponse(BaseModel):
    pending: List[FriendInfo]
    accepted: List[FriendInfo]
