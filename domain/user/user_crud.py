from sqlalchemy.orm import Session
from domain.user.user_schema import UserCreate
from models import User


def create_user(db: Session, user_create: UserCreate):
    db_user = User(username=user_create.username,
                   SIGN_TYPE=user_create.SIGN_TYPE,
                   USER_EMAIL=user_create.email)
    db.add(db_user)
    db.commit()

def get_existing_user(db: Session, user_create: UserCreate):
    return db.query(User).filter(
        (User.username == user_create.username) |
        (User.email == user_create.email)
    ).first()

def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()
