from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from domain.challenge import challenge_router
from domain.challenge.daily import daily_router
from domain.challenge.diary import diary_router
from domain.challenge.weekly import weekly_router
from domain.desc import desc_router
from domain.user import user_router
from domain.friend import friend_router

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
app.include_router(weekly_router.router)

app.include_router(desc_router.router)
