from datetime import datetime

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from database import get_db, upload_file
from domain.challenge import challenge_schema, challenge_crud
from domain.challenge.challenge_crud import get_challenge
from domain.user.user_router import get_current_user
from models import User

router = APIRouter(
    prefix="/api/challenge",
)


@router.get("/all", response_model=list[challenge_schema.Challenge])
def challenge_list(db: Session = Depends(get_db), _current_user: User = Depends(get_current_user)):
    _challenge_list = challenge_crud.get_challenge_list(db, user_uid=_current_user.UID)
    return _challenge_list


@router.get("/{challenge_mst_no}", response_model=challenge_schema.Challenge)
def challenge_detail(challenge_mst_no: int, db: Session = Depends(get_db),
                     _current_user: User = Depends(get_current_user)):
    # 챌린지 정보를 가져옵니다.
    _challenge = get_challenge(db, challenge_id=challenge_mst_no)

    # 챌린지가 존재하는지 확인합니다.
    if not _challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    # 챌린지에 team_goal 속성이 있는지 확인합니다.
    if not hasattr(_challenge, 'team_goal') or not _challenge.team_goal:
        raise HTTPException(status_code=404, detail="Team goal not found for the challenge")

    return _challenge


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
def challenge_create(_challenge_create: challenge_schema.ChallengeCreate,
                     db: Session = Depends(get_db),
                     _current_user: User = Depends(get_current_user)):
    challenge_crud.create_challenge(db, challenge_create=_challenge_create,
                                    current_user=_current_user)
    challenge_crud.create_team(db, challenge_create=_challenge_create)


@router.post("/upload/image")
async def upload_image(_current_user: User = Depends(get_current_user), image_file: UploadFile = File(...)):
    # 이미지 형식만 허용
    if image_file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    # 이미지 크기 제한 (예: 5MB)
    max_size = 5 * 1024 * 1024  # 5MB

    # 파일의 현재 위치 확인 (파일 크기)
    image_file.file.seek(0, 2)  # 파일의 끝으로 이동
    file_size = image_file.file.tell()  # 파일 크기 확인
    image_file.file.seek(0)  # 파일 포인터를 다시 시작 위치로 이동

    # 파일 크기가 최대 크기를 초과하면 오류 발생
    if file_size > max_size:
        raise HTTPException(status_code=413, detail="File is too large.")

    # 고유 파일 이름 생성
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    file_extension = image_file.filename.split(".")[-1]
    file_name = f"{_current_user.UID}_{current_time}.{file_extension}"

    # 파일 업로드 및 URL 획득
    file_url = await upload_file(file_name, image_file)
    return {"url": file_url, "fileName": file_name}


@router.post("/complete/daily", status_code=status.HTTP_204_NO_CONTENT)
def complete_daily(_complete_daily: challenge_schema.CompleteDailyGoal,
                   db: Session = Depends(get_db),
                   _current_user: User = Depends(get_current_user)):
    _challenge = get_challenge(db, challenge_id=_complete_daily.CHALLENGE_MST_NO)
    challenge_crud.complete_daily_goal(db, complete_daily=_complete_daily,
                                       current_challenge=_challenge,
                                       current_user=_current_user)


@router.put("/complete/weekly/{challenge_mst_no}", status_code=status.HTTP_204_NO_CONTENT)
def complete_weekly(challenge_mst_no: int, db: Session = Depends(get_db),
                    _current_user: User = Depends(get_current_user)):
    # 챌린지 정보를 가져옵니다.
    _challenge = get_challenge(db, challenge_id=challenge_mst_no)

    # 챌린지가 존재하는지 확인합니다.
    if not _challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    # 챌린지에 team_goal 속성이 있는지 확인합니다.
    if not hasattr(_challenge, 'team_goal') or not _challenge.team_goal:
        raise HTTPException(status_code=404, detail="Team goal not found for the challenge")

    for team_goal in _challenge.team_goal:
        challenge_crud.complete_weekly_goal(db, db_team=team_goal, current_user=_current_user)
