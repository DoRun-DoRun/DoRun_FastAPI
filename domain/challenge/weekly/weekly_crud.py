from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import User, TeamWeeklyGoal, ChallengeMaster


# 팀 목표 가져오기
def get_team_goal(db: Session,
                  challenge_user_no: int):
    team_goal = (db.query(TeamWeeklyGoal)
                 .filter(TeamWeeklyGoal.CHALLENGE_USER_NO == challenge_user_no)
                 .first())

    if not team_goal:
        raise HTTPException(status_code=404, detail="요청하신 팀 목표를 찾을 수 없습니다.")

    return team_goal


def complete_weekly_goal(db: Session,
                         db_team_goal: TeamWeeklyGoal):
    db_team_goal.IS_DONE = True  # IS_DONE 상태 업데이트
    db_team_goal.MODIFY_DT = datetime.now()  # 변경 날짜 업데이트

    db.commit()
    return db_team_goal
