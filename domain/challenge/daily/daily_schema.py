from pydantic import BaseModel


class CompleteDailyGoal(BaseModel):
    AUTH_IMAGE_FILE_NM: str
    CHALLENGE_MST_NO: int
    COMMENTS: str

