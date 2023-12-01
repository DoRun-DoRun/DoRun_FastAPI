## Start
uvicorn main:app --reload

## DB 자동 생성
alembic revision --autogenerate

## migrations에 생성된 리비전 파일로 DB 변경
alembic upgrade head

## 서버 재설정
sudo systemctl start myapi.service