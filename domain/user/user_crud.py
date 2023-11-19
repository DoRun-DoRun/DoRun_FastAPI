from sqlalchemy.orm import Session
from models import User

from datetime import datetime


# 추후 사용자 이름을 랜덤 문자열 조합으로 만들면 좋겠음
# 형용사 + 명사 (ex 부드러운 + 치즈케잌)
def create_guest_user(db: Session):
    db_user = User(USER_NM="Guest", SIGN_TYPE="GUEST")
    db.add(db_user)
    db.commit()
    return db_user.UID


def get_user(db: Session, uid: int):
    return db.query(User).filter(User.UID == uid).first()
