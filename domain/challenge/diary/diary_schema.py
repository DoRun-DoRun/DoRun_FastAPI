from pydantic import BaseModel


class CompleteDailyGoalAll(BaseModel):
    CHALLENGE_USER_NO: int
    IMAGE_FILE_NM: str
    COMMENTS: str
