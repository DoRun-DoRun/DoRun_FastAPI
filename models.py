import enum

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Enum, MetaData, ForeignKey, ARRAY, \
    JSON, Date
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
    SIGN_TYPE = Column(Enum(LoginType, name="LoginType"))
    USER_NM = Column(String)
    UID = Column(Integer, unique=True)
    USER_EMAIL = Column(String, unique=True)


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
    START_DT = Column(Date)
    END_DT = Column(Date)
    HEADER_EMOJI = Column(String)
    INSERT_DT = Column(DateTime)
    INSERT_USER_UID = Column(Integer, ForeignKey('user.UID'), nullable=False)
    DELETE_DT = Column(DateTime)
    DELETE_YN = Column(Boolean, default=False)
    CHALLENGE_STATUS = Column(Enum(ChallengeStatus, name='ChallengeStatus'))
    user = relationship('User', backref='challenge_master_users')


class DailyComplete(Base):
    __tablename__ = 'daily_complete'

    # Primary Key
    PERSON_DAILY_NO = Column(Integer, primary_key=True)

    # Foreign Keys
    CHALLENGE_MST_ID = Column(Integer, ForeignKey('challenge_master.CHALLENGE_MST_NO'))
    INSERT_USER_UID = Column(Integer, ForeignKey('user.UID'))
    # EMOJI_SEND_USER_UID = Column(Integer, ForeignKey('user.UID'))

    # Other Columns
    # AUTH_IMAGE_FILE_ID = Column(Integer)
    AUTH_IMAGE_FILE_NM = Column(String)
    INSERT_DT = Column(DateTime)
    COMMENTS = Column(String)
    # MODIFY_DATE = Column(DateTime)

    # JSON Column for List
    PERSON_GOAL_LIST = Column(JSON)  # 리스트 데이터를 JSON 형태로 저장
    REACTION_EMOJI = Column(JSON)  # [{EMOJI: str, UID: Int}, ]

    # Relationships (옵션에 따라 필요한 경우)
    challenge = relationship("ChallengeMaster", backref="daily_complete")
    user = relationship("User", backref="daily_complete")
    # emoji_sender = relationship("User", back_populates="emoji_sends")


class TeamGoal(Base):
    __tablename__ = 'team_goal'

    TEAM_GOAL_NO = Column(Integer, primary_key=True)
    TEAM_GOAL_NM = Column(String, default="주간 팀 목표를 정해주세요")

    # Foreign Keys
    CHALLENGE_MST_ID = Column(Integer, ForeignKey('challenge_master.CHALLENGE_MST_NO'))
    TEAM_LEADER_ID = Column(Integer, ForeignKey('user.UID'))

    COMPLETE_USERS = Column(JSON)
    START_DT = Column(Date)
    END_DT = Column(Date)
    INSERT_DT = Column(DateTime)
    MODIFY_DT = Column(DateTime)

    # Relationships (옵션에 따라 필요한 경우)
    challenge = relationship("ChallengeMaster", backref="team_goal")
    user = relationship("User")
