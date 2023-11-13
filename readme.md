## Start
uvicorn main:app --reload

## DB 자동 생성
alembic revision --autogenerate

## migrations에 생성된 리비전 파일로 DB 변경
alembic upgrade head