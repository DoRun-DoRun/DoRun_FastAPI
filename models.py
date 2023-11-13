import enum

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Enum, MetaData, ForeignKey, ARRAY
from sqlalchemy.orm import relationship

from database import Base


# Enum 클래스 정의
class LoginType(enum.Enum):
    KAKAO = 'KAKAO'
    APPLE = 'APPLE'
    GUEST = 'GUEST'


# Accept 상태를 위한 Enum 타입 정의
class AcceptType(enum.Enum):
    PENDING = 'PENDING'
    ACCEPTED = 'ACCEPTED'
    DECLINED = 'DECLINED'
    BLOCKED = 'BLOCKED'


class User(Base):
    __tablename__ = "user"

    USER_NO = Column(Integer, primary_key=True)
    REGISTER_DT = Column(DateTime)
    UPDATE_DT = Column(DateTime)
    RECENT_LOGIN_DT = Column(DateTime)
    DISABLE_YN = Column(Boolean, default=False)
    DISABLE_DT = Column(DateTime)
    # Here we define the name for the ENUM type
    SIGN_TYPE = Column(Enum(LoginType, name="LoginType"))
    USER_NM = Column(String)
    UID = Column(Integer, unique=True)
    USER_EMAIL = Column(String, unique=True)

# class Friend(Base):
#     __tablename__ = 'friend'
#     FRIEND_NO = Column(Integer, primary_key=True)
#     SENDER_ID = Column(Integer, ForeignKey('user.USER_NO'), nullable=False)
#     RECIPIENT_ID = Column(Integer, ForeignKey('user.USER_NO'), nullable=False)
#     INSERT_DT = Column(DateTime)
#     ACCEPT_DT = Column(DateTime)
#     STATUS = Column(Enum(accept_type, name="accept_type"), default=accept_type.PENDING)
#
#     # User와 Friend 간의 관계 설정
#     sender = relationship('User', foreign_keys=[SENDER_ID], backref='sent_friend_requests')
#     recipient = relationship('User', foreign_keys=[RECIPIENT_ID], backref='received_friend_requests')
#
# class Character(Base):
#     __tablename__ = 'character'
#     CHARACTER_NO = Column(Integer, primary_key=True)
#     CHARACTER_NM = Column(String)
#     INSERT_DT = Column(DateTime)
#     UPDATE_DT = Column(DateTime)
#
# class Pet(Base):
#     __tablename__ = 'pet'
#     PET_NO = Column(Integer, primary_key=True)
#     PET_NM = Column(String)
#     INSERT_DT = Column(DateTime)
#     UPDATE_DT = Column(DateTime)
#
# class Mypage(Base):
#     __tablename__ = 'mypage'
#     Mypage_NO = Column(Integer, primary_key=True)
#     USER_ID = Column(Integer, ForeignKey('user.USER_NO'))  # 'user' 테이블의 USER_NO를 참조
#     INSERT_DT = Column(DateTime)
#     UPDATE_DT = Column(DateTime)
#     # PostgreSQL의 ARRAY 타입을 사용하여 Character와 Pet의 ID 배열을 저장
#     MY_CHARACTER = Column(ARRAY(Integer))
#     MY_PET = Column(ARRAY(Integer))
#     CURRENT_CHARACTER_NO = Column(Integer, ForeignKey('character.CHARACTER_NO'))
#     CURRENT_PET_NO = Column(Integer, ForeignKey('pet.PET_NO'))
#
#     # 단일 관계 설정
#     CURRENT_CHARACTER = relationship('Character', foreign_keys=[CURRENT_CHARACTER_NO])
#     CURRENT_PET = relationship('Pet', foreign_keys=[CURRENT_PET_NO])


class ChallengeStatus(enum.Enum):
    PENDING = 'PENDING'
    ACTIVE = 'ACTIVE'
    COMPLETE = 'COMPLETE'
    FAILED = 'FAILED'


class ChallengeMaster(Base):
    __tablename__ = 'challenge_master'

    CHALLENGE_MST_NO = Column(Integer, primary_key=True)
    CHALLENGE_MST_NM = Column(String)
    USERS_UID = Column(ARRAY(Integer))
    START_DT = Column(DateTime)
    END_DT = Column(DateTime)
    HEADER_EMOJI = Column(String)
    INSERT_DT = Column(DateTime)
    INSERT_USER_UID = Column(Integer, ForeignKey('user.UID'), nullable=False)
    DELETE_DT = Column(DateTime)
    DELETE_YN = Column(Boolean, default=False)
    CHALLENGE_STATUS = Column(Enum(ChallengeStatus, name='ChallengeStatus'))
    user = relationship('User', backref='challenge_master_users')
