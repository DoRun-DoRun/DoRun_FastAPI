from pydantic import BaseModel


class CompleteWeeklyGoal(BaseModel):
    CHALLENGE_MST_NO: int

