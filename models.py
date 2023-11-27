import enum
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Enum, MetaData, ForeignKey, ARRAY, \
    JSON, Date, Table, Double, Sequence, Index
from sqlalchemy.orm import relationship

from database import Base


# Enum 클래스 정의
class SignType(enum.Enum):
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


class ItemType(enum.Enum):
    BOOM = "BOOM"
    HAMMER = "HAMMER"


class CharacterType(enum.Enum):
    CHARACTER_TYPE1 = 'CHARACTER_TYPE1'
    CHARACTER_TYPE2 = 'CHARACTER_TYPE2'
    CHARACTER_TYPE3 = 'CHARACTER_TYPE3'
    CHARACTER_TYPE4 = 'CHARACTER_TYPE4'


class PetType(enum.Enum):
    PET_TYPE1 = 'PET_TYPE1'
    PET_TYPE2 = 'PET_TYPE2'


class OwnerShipType(enum.Enum):
    OWNER: 'OWNER'
    EQUIP: 'EQUIP'
    LACK: 'LACK'


class User(Base):
    __tablename__ = "user"

    USER_NO = Column(Integer, primary_key=True)
    SIGN_TYPE = Column(Enum(SignType, name="SignType"))
    USER_NM = Column(String)
    UID = Column(Integer, Sequence('user_uid_seq', start=1000000), unique=True, index=True)
    USER_EMAIL = Column(String, unique=True)

    INSERT_DT = Column(DateTime, default=datetime.utcnow)
    MODIFY_DT = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    RECENT_LOGIN_DT = Column(DateTime)
    DISABLE_YN = Column(Boolean, default=False)
    DISABLE_DT = Column(DateTime)

    CHALLENGE = relationship('ChallengeMaster', backref="user")


class UserSetting(Base):
    __tablename__ = 'user_setting'

    USER_SETTING_NO = Column(Integer, primary_key=True)
    AGREE_POLICY_YN = Column(Boolean)
    AGREE_POLICY_DT = Column(DateTime)
    NOTICE_PUSH_YN = Column(Boolean)
    NOTICE_PUSH_DT = Column(DateTime)
    NOTICE_PUSH_NIGHT_YN = Column(Boolean)
    NOTICE_PUSH_NIGHT_DT = Column(DateTime)
    USER_NO = Column(Integer, ForeignKey('user.USER_NO'))


class Friend(Base):
    __tablename__ = 'friend'

    FRIEND_NO = Column(Integer, primary_key=True)
    INSERT_DT = Column(DateTime, default=datetime.utcnow)
    ACCEPT_DT = Column(DateTime)
    ACCEPT_STATUS = Column(Enum(AcceptType), name='AcceptType')
    SENDER_UID = Column(Integer, ForeignKey('user.USER_NO'))
    RECIPIENT_UID = Column(Integer, ForeignKey('user.USER_NO'))


class Character(Base):
    __tablename__ = 'character'

    CHARACTER_NO = Column(Integer, primary_key=True)
    CHARACTER_NM = Column(String)
    STATUS = Column(Enum(OwnerShipType, name='OwnerShipType'))
    USER_NO = Column(Integer, ForeignKey('user.USER_NO'))


class Pet(Base):
    __tablename__ = 'pet'

    PET_NO = Column(Integer, primary_key=True)
    PET_NM = Column(Enum(PetType), name='PetType')
    STATUS = Column(Enum(OwnerShipType, name='OwnerShipType'))
    USER_NO = Column(Integer, ForeignKey('user.USER_NO'))


class ChallengeMaster(Base):
    __tablename__ = 'challenge_master'

    CHALLENGE_MST_NO = Column(Integer, primary_key=True)
    CHALLENGE_MST_NM = Column(String)
    START_DT = Column(Date)
    END_DT = Column(Date)
    HEADER_EMOJI = Column(String)
    CHALLENGE_STATUS = Column(Enum(ChallengeStatus, name='ChallengeStatus'))

    INSERT_DT = Column(DateTime, default=datetime.utcnow)
    MODIFY_DT = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    DELETE_DT = Column(DateTime)
    DELETE_YN = Column(Boolean, default=False)

    MEMBER = relationship('User', backref="challenge_master")


class ChallengeUser(Base):
    __tablename__ = 'challenge_users'

    CHALLENGE_USER_NO = Column(Integer, primary_key=True)
    ACCEPT_STATUS = Column(Enum(AcceptType, name="AcceptType"))

    INSERT_DT = Column(DateTime, default=datetime.utcnow)
    MODIFY_DT = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    IS_OWNER = Column(Boolean)
    IS_LEADER = Column(Boolean)

    USER_NO = Column(Integer, ForeignKey('user.USER_NO'))
    CHALLENGE_MST_NO = Column(Integer, ForeignKey('challenge_master.CHALLENGE_MST_NO'))

    # Index('ix_challenge_users_user_no', 'USER_NO')
    # Index('ix_challenge_users_challenge_mst_no', 'CHALLENGE_MST_NO')


class PersonDailyGoal(Base):
    __tablename__ = 'person_daily_goal'

    PERSON_NO = Column(Integer, primary_key=True)
    PERSON_NM = Column(String)
    IS_DONE = Column(Boolean)

    INSERT_DT = Column(DateTime, default=datetime.utcnow)
    UPDATE_DT = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    CHALLENGE_USER = relationship('ChallengeUser', backref="person_daily_goal")
    CHALLENGE_USER_NO = Column(Integer, ForeignKey('challenge_users.CHALLENGE_USER_NO'))


class TeamWeeklyGoal(Base):
    __tablename__ = 'team_weekly_goal'

    TEAM_NO = Column(Integer, primary_key=True)
    TEAM_NM = Column(String)
    IS_DONE = Column(Boolean)
    START_DT = Column(DateTime)
    END_DT = Column(DateTime)

    INSERT_DT = Column(DateTime, default=datetime.utcnow)
    MODIFY_DT = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    CHALLENGE_USER = relationship('ChallengeUser', backref="team_weekly_goal")
    CHALLENGE_USER_NO = Column(Integer, ForeignKey('challenge_users.CHALLENGE_USER_NO'))


class AdditionalGoal(Base):
    __tablename__ = 'additional_goal'

    ADDITIONAL_NO = Column(Integer, primary_key=True)
    ADDITIONAL_NM = Column(String)
    IS_DONE = Column(Boolean)
    START_DT = Column(DateTime)
    END_DT = Column(DateTime)
    IMAGE_FILE_NM = Column(String)

    CHALLENGE_USER = relationship('ChallengeUser', backref="additional_goal")
    CHALLENGE_USER_NO = Column(Integer, ForeignKey('challenge_users.CHALLENGE_USER_NO'))


class PersonDailyGoalComplete(Base):
    __tablename__ = 'person_daily_goal_complete'

    DAILY_COMPLETE_NO = Column(Integer, primary_key=True)
    IMAGE_FILE_NM = Column(String)
    INSERT_DT = Column(DateTime, default=datetime.utcnow)
    COMMENTS = Column(String)

    CHALLENGE_USER = relationship('ChallengeUser', backref="person_daily_goal_complete")
    CHALLENGE_USER_NO = Column(Integer, ForeignKey('challenge_users.CHALLENGE_USER_NO'))


class DailyCompleteUser(Base):
    __tablename__ = 'daily_complete_user'

    DAILY_COMPLETE_USER_NO = Column(Integer, primary_key=True)
    EMOJI = Column(String)
    DAILY_COMPLETE_NO = Column(Integer, ForeignKey('person_daily_goal_complete.DAILY_COMPLETE_NO'))

    CHALLENGE_USER = relationship('ChallengeUser', backref="daily_complete_user")
    CHALLENGE_USER_NO = Column(Integer, ForeignKey('challenge_users.CHALLENGE_USER_NO'))


class ItemUser(Base):
    __tablename__ = 'item_user'

    ITEM_NO = Column(Integer, primary_key=True)
    ITEM_NM = Column(Enum(ItemType, name='ItemType'))
    COUNT = Column(Integer)

    CHALLENGE_USER = relationship('ChallengeUser', backref='item_users')
    CHALLENGE_USER_NO = Column(Integer, ForeignKey('challenge_users.CHALLENGE_USER_NO'))


class ItemLog(Base):
    __tablename__ = 'item_log'

    ITEM_LOG_NO = Column(Integer, primary_key=True)
    ITEM_NM = Column(Enum(ItemType, name='ItemType'))
    INSERT_DT = Column(DateTime, default=datetime.utcnow)
    SENDER_UID = Column(Integer, ForeignKey('challenge_users.CHALLENGE_USER_NO'))
    RECIPIENT_UID = Column(Integer, ForeignKey('challenge_users.CHALLENGE_USER_NO'))

    sender = relationship('ChallengeUser', foreign_keys=[SENDER_UID])
    recipient = relationship('ChallengeUser', foreign_keys=[RECIPIENT_UID])
