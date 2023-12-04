from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from domain.challenge import challenge_crud
from domain.user.user_crud import get_current_user
from models import User, AdditionalGoal

router = APIRouter(
    prefix="/additional_goal",
    tags=["Additional Goal"]
)


@router.put("/{additional_goal_no}")
def complete_additional_goal(additional_goal_no: int, image_file_nm: str, challenge_user_no: int,
                             db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user)):
    challenge_user = challenge_crud.get_challenge_user_by_challenge_user_no(db, challenge_user_no)

    goal = db.query(AdditionalGoal).filter(AdditionalGoal.ADDITIONAL_NO == additional_goal_no).first()
    if not goal:
        raise HTTPException(status_code=404, detail="추가목표를 찾을 수 없습니다.")

    if (goal.CHALLENGE_USER_NO != challenge_user_no) or (challenge_user.USER_NO != current_user.USER_NO) :
        raise HTTPException(status_code=401, detail="수정 권한이 없습니다.")

    goal.IS_DONE = True
    goal.IMAGE_FILE_NM = image_file_nm

    db.commit()

    return {"message": "추가목표 완료"}
