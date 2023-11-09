import enum

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Enum, MetaData, ForeignKey, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Enum 클래스 정의
class login_type(enum.Enum):
    Kakao = 'Kakao'
    Apple = 'Apple'
    Guest = 'Guest'

# Accept 상태를 위한 Enum 타입 정의
class accept_type(enum.Enum):
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
    SIGN_TYPE = Column(Enum(login_type, name="login_type"))
    AGREE_POLICY_YN = Column(Boolean)
    AGREE_POLICY_DT = Column(DateTime)
    AGREE_PRIVACYPOLICY_YN = Column(Boolean)
    AGREE_PRIVACYPOLICY_DT = Column(DateTime)
    USER_NM = Column(String(50))
    UID = Column(String(8))
    NOTICE_PUSH_YN = Column(Boolean)
    USER_EMAIL = Column(String(255))

class Friend(Base):
    __tablename__ = 'friend'
    FRIEND_NO = Column(Integer, primary_key=True)
    SENDER_ID = Column(Integer, ForeignKey('user.USER_NO'), nullable=False)
    RECIPIENT_ID = Column(Integer, ForeignKey('user.USER_NO'), nullable=False)
    INSERT_DT = Column(DateTime)
    ACCEPT_DT = Column(DateTime)
    STATUS = Column(Enum(accept_type, name="accept_type"), default=accept_type.PENDING)

    # User와 Friend 간의 관계 설정
    sender = relationship('User', foreign_keys=[SENDER_ID], backref='sent_friend_requests')
    recipient = relationship('User', foreign_keys=[RECIPIENT_ID], backref='received_friend_requests')

class Character(Base):
    __tablename__ = 'character'
    CHARACTER_NO = Column(Integer, primary_key=True)
    CHARACTER_NM = Column(String)
    INSERT_DT = Column(DateTime)
    UPDATE_DT = Column(DateTime)

class Pet(Base):
    __tablename__ = 'pet'
    PET_NO = Column(Integer, primary_key=True)
    PET_NM = Column(String)
    INSERT_DT = Column(DateTime)
    UPDATE_DT = Column(DateTime)

class Mypage(Base):
    __tablename__ = 'mypage'
    Mypage_NO = Column(Integer, primary_key=True)
    USER_ID = Column(Integer, ForeignKey('user.USER_NO'))  # 'user' 테이블의 USER_NO를 참조
    INSERT_DT = Column(DateTime)
    UPDATE_DT = Column(DateTime)
    # PostgreSQL의 ARRAY 타입을 사용하여 Character와 Pet의 ID 배열을 저장
    MY_CHARACTER = Column(ARRAY(Integer))
    MY_PET = Column(ARRAY(Integer))
    CURRENT_CHARACTER_NO = Column(Integer, ForeignKey('character.CHARACTER_NO'))
    CURRENT_PET_NO = Column(Integer, ForeignKey('pet.PET_NO'))

    # 단일 관계 설정
    CURRENT_CHARACTER = relationship('Character', foreign_keys=[CURRENT_CHARACTER_NO])
    CURRENT_PET = relationship('Pet', foreign_keys=[CURRENT_PET_NO])