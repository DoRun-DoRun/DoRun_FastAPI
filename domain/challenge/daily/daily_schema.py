from pydantic import BaseModel


class CreatePersonGoal(BaseModel):
    CHALLENGE_USER_NO: int
    PERSON_NM: str


class GetPersonGoal(BaseModel):
    PERSON_NO: int
    PERSON_NM: str
    IS_DONE: bool


class UpdatePersonGoal(BaseModel):
    PERSON_NO: int
    PERSON_NM: str
    IS_DONE: bool
