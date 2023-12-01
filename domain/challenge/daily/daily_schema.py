from pydantic import BaseModel


class CreatePersonGoal(BaseModel):
    CHALLENGE_MST_NO: int
    PERSON_GOAL_NM: str


class GetPersonGoal(BaseModel):
    PERSON_GOAL_NO: int
    PERSON_GOAL_NM: str
    IS_DONE: bool


class UpdatePersonGoal(BaseModel):
    PERSON_GOAL_NO: int
    PERSON_GOAL_NM: str
    IS_DONE: bool


class DeletePersonGoal(BaseModel):
    PERSON_GOAL_NO: int


class CompleteDailyGoal(BaseModel):
    AUTH_IMAGE_FILE_NM: str
    CHALLENGE_USER_NO: int
    COMMENTS: str
