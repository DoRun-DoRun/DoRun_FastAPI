import boto3
from botocore.exceptions import NoCredentialsError
from fastapi import File, UploadFile
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from starlette.config import Config

config = Config('.env')
SQLALCHEMY_DATABASE_URL = config('SQLALCHEMY_DATABASE_URL')

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# S3 설정
ACCESS_KEY = config('S3_ACCESS_KEY')
SECRET_KEY = config('S3_SECRET_KEY')
BUCKET_NAME = 'do-run'

s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                  aws_secret_access_key=SECRET_KEY)


async def upload_file(file_name: str, file: UploadFile = File(...)):
    try:
        s3.upload_fileobj(file.file, BUCKET_NAME, file_name)
        file_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{file_name}"
        return file_url
    except NoCredentialsError:
        return "Credentials not available"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
