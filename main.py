from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

from fastapi import FastAPI, Depends
from pytz import timezone

from database import get_db, SessionLocal
from domain.challenge import challenge_router
from domain.challenge.additional import additional_router
from domain.challenge.challenge_crud import start_challenge_server
from domain.challenge.diary import diary_router
from domain.challenge.item import item_router
from domain.desc import desc_router
from domain.user import user_router, friend_router
from models import ChallengeStatusType, ChallengeMaster

app = FastAPI()

# origins = [
#     "http://127.0.0.1:5173",
# ]
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.include_router(user_router.router)
app.include_router(friend_router.router)
app.include_router(challenge_router.router)
# app.include_router(daily_router.router)
app.include_router(diary_router.router)
# app.include_router(weekly_router.router)
app.include_router(additional_router.router)
app.include_router(item_router.router)
app.include_router(desc_router.router)

scheduler = BackgroundScheduler()
scheduler.configure(timezone=timezone('Asia/Seoul'))


def check_and_start_challenges():
    db = SessionLocal()  # 직접 세션 생성
    try:
        current_date = datetime.utcnow().date()
        challenges_to_start = db.query(ChallengeMaster).filter(
            ChallengeMaster.START_DT <= current_date,
            ChallengeMaster.CHALLENGE_STATUS == ChallengeStatusType.PENDING,
            ChallengeMaster.DELETE_YN == False,
        ).all()

        for challenge in challenges_to_start:
            start_challenge_server(db, challenge)

        # challenges_to_end = db.query(ChallengeMaster).filter(
        #     ChallengeMaster.END_DT <= current_date,
        #     ChallengeMaster.CHALLENGE_STATUS == ChallengeStatusType.PROGRESS,
        #     ChallengeMaster.DELETE_YN == False,
        # ).all()

        # for challenge in challenges_to_end:
         # start_challenge_server(db, challenge)

        db.commit()
    finally:
        db.close()  # 세션 닫기


# 스케줄러에 작업 추가
scheduler.add_job(check_and_start_challenges, 'cron', hour=6)

# 스케줄러 시작
scheduler.start()
