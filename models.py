import enum
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Enum, MetaData, ForeignKey, ARRAY, \
    JSON, Date, Table, Double, Sequence
from sqlalchemy.orm import relationship

from database import Base


# Enum 클래스 정의
class LoginType(enum.Enum):
    KAKAO = 'KAKAO'
    APPLE = 'APPLE'
    GUEST = 'GUEST'


class ChallengeStatus(enum.Enum):
    PENDING = 'PENDING'
    ACTIVE = 'ACTIVE'
    COMPLETE = 'COMPLETE'
    FAILED = 'FAILED'


# Accept 상태를 위한 Enum 타입 정의
class AcceptType(enum.Enum):
    PENDING = 'PENDING'
    ACCEPTED = 'ACCEPTED'
    DECLINED = 'DECLINED'
    BLOCKED = 'BLOCKED'


# 챌린지와 유저 간의 다대다 관계를 위한 연결 테이블
Challenge_User = Table(
    'challenge_user',
    Base.metadata,
    Column('USER_NO', Integer, ForeignKey('user.USER_NO'), primary_key=True),
    Column('CHALLENGE_MST_NO', Integer, ForeignKey('challenge_master.CHALLENGE_MST_NO'), primary_key=True),
    Column('PROGRESS', Double, default=0.0),
    Column('STATUS', Enum(AcceptType, name='AcceptType'), default="PENDING"),
    Column('INSERT_DT', DateTime, default=datetime.now()),
    Column('MODIFY_DT', DateTime),
)

# challenge_user_item = Table(
#     'challenge_user_item',
#     Base.metadata,
#     Column('USER_NO', Integer, ForeignKey('user.USER_NO'), primary_key=True),
#     Column('CHALLENGE_MST_NO', Integer, ForeignKey('challenge_master.CHALLENGE_MST_NO'), primary_key=True),
#     Column('ITEM_NO', Integer),
#     Column('ITEM_CNT', Integer),
# )


# 완료모달과 유저 간의 다대다 관계를 위한 연결 테이블
DailyComplete_User = Table(
    'daily_complete_user',
    Base.metadata,
    Column('USER_NO', Integer, ForeignKey('user.USER_NO'), primary_key=True),
    Column('DAILY_COMPLETE_NO', Integer, ForeignKey('daily_complete.DAILY_COMPLETE_NO'), primary_key=True),
    Column('EMOJI', String)
)


class User(Base):
    __tablename__ = "user"

    USER_NO = Column(Integer, primary_key=True)
    SIGN_TYPE = Column(Enum(LoginType, name="LoginType"))
    USER_NM = Column(String)
    UID = Column(Integer, Sequence('user_uid_seq', start=1000000), unique=True)
    USER_EMAIL = Column(String, unique=True)

    REGISTER_DT = Column(DateTime, default=datetime.now())
    UPDATE_DT = Column(DateTime, default=datetime.now())
    RECENT_LOGIN_DT = Column(DateTime)
    DISABLE_YN = Column(Boolean, default=False)
    DISABLE_DT = Column(DateTime)

    CHALLENGE = relationship('ChallengeMaster', secondary=Challenge_User, backref="Challenge_User")
    DAILY_COMPLETE = relationship("DailyComplete", secondary=DailyComplete_User, backref="DailyComplete_User")


class ChallengeMaster(Base):
    __tablename__ = 'challenge_master'

    CHALLENGE_MST_NO = Column(Integer, primary_key=True)
    CHALLENGE_MST_NM = Column(String)
    START_DT = Column(Date)
    END_DT = Column(Date)
    HEADER_EMOJI = Column(String)
    CHALLENGE_STATUS = Column(Enum(ChallengeStatus, name='ChallengeStatus'))

    INSERT_DT = Column(DateTime)
    MODIFY_DT = Column(DateTime)
    DELETE_DT = Column(DateTime)
    DELETE_YN = Column(Boolean, default=False)

    USER_ID = Column(Integer, ForeignKey("user.USER_NO"))
    USER = relationship("User", backref="Challenge_Master")

    MEMBER = relationship('User', secondary=Challenge_User, backref="Challenge_User")


# 하루가 넘어가면, 해당 TodoItem들을 복사해 생성하기
class PersonGoal(Base):
    __tablename__ = "person_goal"

    PERSON_GOAL_NO = Column(Integer, primary_key=True)
    PERSON_GOAL_NM = Column(String, nullable=False)
    IS_DONE = Column(Boolean, default=False)

    INSERT_DT = Column(DateTime, default=datetime.now())

    CHALLENGE_MST_ID = Column(Integer, ForeignKey('challenge_master.CHALLENGE_MST_NO'))
    CHALLENGE = relationship("ChallengeMaster", backref="Person_Goal")
    USER_ID = Column(Integer, ForeignKey("user.USER_NO"))
    USER = relationship("User", backref="Person_Goal")


class TeamGoal(Base):
    __tablename__ = "team_goal"

    TEAM_GOAL_NO = Column(Integer, primary_key=True)
    TEAM_GOAL_NM = Column(String, nullable=False)
    IS_DONE = Column(Boolean, default=False)

    INSERT_DT = Column(DateTime)
    MODIFY_DT = Column(DateTime)

    CHALLENGE_MST_ID = Column(Integer, ForeignKey('challenge_master.CHALLENGE_MST_NO'))
    CHALLENGE = relationship("ChallengeMaster", backref="Team_goal")
    USER_ID = Column(Integer, ForeignKey("user.USER_NO"))
    LEADER_ID = Column(Integer, ForeignKey("user.USER_NO"))

    USER = relationship("User", foreign_keys=[USER_ID], backref="team_goals_as_member")
    LEADER = relationship("User", foreign_keys=[LEADER_ID], backref="team_goals_as_leader")


class AdditionalGoal(Base):
    __tablename__ = "additional_goal"

    ADDITIONAL_GOAL = Column(Integer, primary_key=True)
    ADDITIONAL_GOAL_NM = Column(String, nullable=False)
    IS_DONE = Column(Boolean, default=False)

    START_DT = Column(DateTime)
    END_DT = Column(DateTime)

    AUTH_IMAGE_FILE_NM = Column(String)

    CHALLENGE_MST_ID = Column(Integer, ForeignKey('challenge_master.CHALLENGE_MST_NO'))
    CHALLENGE = relationship("ChallengeMaster", backref="Additional_goal")
    USER_ID = Column(Integer, ForeignKey("user.USER_NO"))
    USER = relationship("User", backref="Additional_goal")


class DailyComplete(Base):
    __tablename__ = 'daily_complete'

    DAILY_COMPLETE_NO = Column(Integer, primary_key=True)
    AUTH_IMAGE_FILE_NM = Column(String)
    COMMENTS = Column(String)

    INSERT_DT = Column(DateTime)

    CHALLENGE_MST_ID = Column(Integer, ForeignKey('challenge_master.CHALLENGE_MST_NO'))
    CHALLENGE = relationship("ChallengeMaster", backref="Daily_Complete")
    USER_ID = Column(Integer, ForeignKey("user.USER_NO"))
    USER = relationship("User", backref="Daily_Complete")

    EMOJI_USER = relationship('User', secondary=DailyComplete_User, backref="DailyComplete_User")
