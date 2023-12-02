from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from domain.challenge.weekly.weekly_schema import UpdateWeeklyGoal
from models import TeamWeeklyGoal


# 팀 목표 가져오기
def get_team_goal(db: Session,
                  team_no: int):
    team_goal = (db.query(TeamWeeklyGoal)
                 .filter(TeamWeeklyGoal.TEAM_NO == team_no)
                 .first())

    if not team_goal:
        raise HTTPException(status_code=404, detail="요청하신 팀 목표를 찾을 수 없습니다.")

    return team_goal


def update_weekly_goal(db: Session,
                       db_team_goal: TeamWeeklyGoal,
                       weekly_team_goal_update: UpdateWeeklyGoal):
    db_team_goal.TEAM_NM = weekly_team_goal_update.TEAM_NM
    db_team_goal.IS_DONE = weekly_team_goal_update.IS_DONE
    db_team_goal.MODIFY_DT = datetime.now()  # 변경 날짜 업데이트

    db.add(db_team_goal)
    db.commit()
