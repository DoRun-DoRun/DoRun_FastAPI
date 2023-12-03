from pydantic import BaseModel


class UpdateWeeklyGoal(BaseModel):
    TEAM_NO: int
    TEAM_NM: str
    IS_DONE: bool
