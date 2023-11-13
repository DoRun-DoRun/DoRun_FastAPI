from sqlalchemy.orm import Session
from models import User

from datetime import datetime


def create_guest_user(db: Session, uid: int):
    db_user = User(USER_NM="사용자" + str(uid),
                   SIGN_TYPE="GUEST",
                   REGISTER_DT=datetime.now(),
                   UID=uid)
    db.add(db_user)
    db.commit()
    return db_user


def generate_uid(db: Session) -> int:
    last_user = db.query(User).order_by(User.USER_NO.desc()).first()
    last_uid = last_user.UID if last_user else 1000000
    new_uid = last_uid + 1
    return new_uid


# def get_existing_user(db: Session, user_create: UserCreate):
#     return db.query(User).filter(User.USER_EMAIL == user_create.USER_EMAIL).first()


def get_user(db: Session, uid: int):
    return db.query(User).filter(User.UID == uid).first()
