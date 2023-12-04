from typing import List

from pydantic import BaseModel


class PersonGoalPydantic(BaseModel):
    PERSON_NM: str
    IS_DONE: bool


class CreateDiary(BaseModel):
    CHALLENGE_USER_NO: int
    IMAGE_FILE_NM: str
    COMMENTS: str
    PERSON_GOAL: List[PersonGoalPydantic]
