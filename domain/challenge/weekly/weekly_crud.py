from datetime import datetime

from sqlalchemy.orm import Session

from models import User, TeamGoal, ChallengeMaster


def complete_weekly_goal(db: Session,
                         current_challenge: ChallengeMaster,
                         current_user: User):
    # 팀 목표 찾기
    team_goal = db.query(TeamGoal).filter(
        TeamGoal.CHALLENGE_MST_ID == current_challenge.CHALLENGE_MST_NO,
        TeamGoal.USER_ID == current_user.USER_NO
    ).first()

    if not team_goal:
        return None

    # IS_DONE 상태 업데이트
    team_goal.IS_DONE = True
    team_goal.MODIFY_DT = datetime.now()  # 변경 날짜 업데이트

    db.commit()
    return team_goal
