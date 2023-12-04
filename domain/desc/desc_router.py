from datetime import datetime

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException

from database import upload_file
from domain.user.user_crud import get_current_user
from models import User


router = APIRouter(
    prefix="/desc",
    tags=["Desc"]
)


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