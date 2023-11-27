from pydantic import BaseModel


class CreateTodoItem(BaseModel):
    CHALLENGE_MST_NO: int
    PERSON_GOAL_NM: str


class GetTodoItem(BaseModel):
    PERSON_GOAL_NO: int
    PERSON_GOAL_NM: str
    IS_DONE: bool


class UpdateTodoItem(BaseModel):
    PERSON_GOAL_NO: int
    PERSON_GOAL_NM: str
    IS_DONE: bool


class DeleteTodoItem(BaseModel):
    PERSON_GOAL_NO: int


class CompleteDailyGoal(BaseModel):
    AUTH_IMAGE_FILE_NM: str
    CHALLENGE_MST_NO: int
    COMMENTS: str
