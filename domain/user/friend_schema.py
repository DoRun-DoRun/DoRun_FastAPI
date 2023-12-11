from pydantic import BaseModel
from typing import List, Optional


class FriendInfo(BaseModel):
    UID: int
    USER_NM: str


class FriendListResponse(BaseModel):
    pending: List[FriendInfo]
    accepted: List[FriendInfo]
