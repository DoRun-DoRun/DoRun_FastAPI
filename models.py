import enum
from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, ForeignKey, Sequence
from sqlalchemy.orm import relationship

from database import Base


# Enum 클래스 정의
class SignType(enum.Enum):
    KAKAO = 'KAKAO'
    APPLE = 'APPLE'
    GUEST = 'GUEST'


class ChallengeStatusType(enum.Enum):
    PENDING = 'PENDING'
    PROGRESS = 'PROGRESS'
    COMPLETE = 'COMPLETE'
    FAILED = 'FAILED'


class InviteAcceptType(enum.Enum):
    PENDING = 'PENDING'
    ACCEPTED = 'ACCEPTED'
    DECLINED = 'DECLINED'
    DELETED = 'DELETED'


class ItemType(enum.Enum):
    BOOM = "BOOM"
    HAMMER = "HAMMER"


class AvatarType(enum.Enum):
    CHARACTER = "CHARACTER"
    PET = "PET"


class User(Base):
    __tablename__ = "user"

    USER_NO = Column(Integer, primary_key=True)
    SIGN_TYPE = Column(Enum(SignType, name="SignType"))
    USER_NM = Column(String)
    UID = Column(Integer, Sequence('user_uid_seq', start=1000000), unique=True, index=True)
    USER_EMAIL = Column(String)
    ID_TOKEN = Column(String)

    INSERT_DT = Column(DateTime, default=datetime.utcnow)
    MODIFY_DT = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    RECENT_LOGIN_DT = Column(DateTime, default=datetime.utcnow)
    DISABLE_YN = Column(Boolean, default=False)
    DISABLE_DT = Column(DateTime)

    CHALLENGES = relationship('ChallengeUser', back_populates='USER')


class UserSetting(Base):
    __tablename__ = 'user_setting'

    USER_SETTING_NO = Column(Integer, primary_key=True)
    AGREE_POLICY_YN = Column(Boolean, default=False)
    AGREE_POLICY_DT = Column(DateTime, onupdate=datetime.utcnow)
    NOTICE_PUSH_YN = Column(Boolean, default=False)
    NOTICE_PUSH_DT = Column(DateTime, onupdate=datetime.utcnow)
    NOTICE_PUSH_AD_YN = Column(Boolean, default=False)
    NOTICE_PUSH_AD_DT = Column(DateTime, onupdate=datetime.utcnow)
    NOTICE_PUSH_NIGHT_YN = Column(Boolean, default=False)
    NOTICE_PUSH_NIGHT_DT = Column(DateTime, onupdate=datetime.utcnow)
    USER_NO = Column(Integer, ForeignKey('user.USER_NO'))


class Friend(Base):
    __tablename__ = 'friend'

    FRIEND_NO = Column(Integer, primary_key=True)
    INSERT_DT = Column(DateTime, default=datetime.utcnow)
    ACCEPT_DT = Column(DateTime)
    ACCEPT_STATUS = Column(Enum(InviteAcceptType), name='InviteAcceptType', default=InviteAcceptType.PENDING)
    SENDER_NO = Column(Integer, ForeignKey('user.USER_NO'))
    RECIPIENT_NO = Column(Integer, ForeignKey('user.USER_NO'))


class Avatar(Base):
    __tablename__ = 'avatar'

    AVATAR_NO = Column(Integer, primary_key=True)
    AVATAR_NM = Column(String, nullable=False)
    AVATAR_TYPE = Column(Enum(AvatarType, name='AvatarType'))


class AvatarUser(Base):
    __tablename__ = 'avatar_user'

    AVATAR_USER_NO = Column(Integer, primary_key=True)
    IS_EQUIP = Column(Boolean)
    AVATAR_NO = Column(Integer, ForeignKey('avatar.AVATAR_NO'))
    USER_NO = Column(Integer, ForeignKey('user.USER_NO'))


class ChallengeMaster(Base):
    __tablename__ = 'challenge_master'

    CHALLENGE_MST_NO = Column(Integer, primary_key=True)
    CHALLENGE_MST_NM = Column(String)
    START_DT = Column(DateTime)
    END_DT = Column(DateTime)
    HEADER_EMOJI = Column(String)
    CHALLENGE_STATUS = Column(Enum(ChallengeStatusType, name='ChallengeStatusType'),
                              default=ChallengeStatusType.PENDING)

    INSERT_DT = Column(DateTime, default=datetime.utcnow)
    MODIFY_DT = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    DELETE_DT = Column(DateTime)
    DELETE_YN = Column(Boolean, default=False)

    USERS = relationship('ChallengeUser', back_populates='CHALLENGE_MST')


class ChallengeUser(Base):
    __tablename__ = 'challenge_users'

    CHALLENGE_USER_NO = Column(Integer, primary_key=True)
    ACCEPT_STATUS = Column(Enum(InviteAcceptType, name="InviteAcceptType", default=InviteAcceptType.PENDING))
    COMMENT = Column(String)

    INSERT_DT = Column(DateTime, default=datetime.utcnow)
    MODIFY_DT = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    IS_OWNER = Column(Boolean)
    # IS_LEADER = Column(Boolean, default=False)
    IS_VIEW = Column(Boolean, default=False)

    USER_NO = Column(Integer, ForeignKey('user.USER_NO'))
    USER = relationship('User', back_populates='CHALLENGES')

    CHALLENGE_MST_NO = Column(Integer, ForeignKey('challenge_master.CHALLENGE_MST_NO'))
    CHALLENGE_MST = relationship('ChallengeMaster', back_populates='USERS')

    # Index('ix_challenge_users_user_no', 'USER_NO')
    # Index('ix_challenge_users_challenge_mst_no', 'CHALLENGE_MST_NO')


class PersonDailyGoal(Base):
    __tablename__ = 'person_daily_goal'

    PERSON_NO = Column(Integer, primary_key=True)
    PERSON_NM = Column(String)
    IS_DONE = Column(Boolean, default=False)

    INSERT_DT = Column(DateTime, default=datetime.utcnow)
    UPDATE_DT = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    CHALLENGE_USER = relationship('ChallengeUser', backref="person_daily_goal")
    CHALLENGE_USER_NO = Column(Integer, ForeignKey('challenge_users.CHALLENGE_USER_NO'))

    DAILY_COMPLETE = relationship('PersonDailyGoalComplete')
    DAILY_COMPLETE_NO = Column(Integer, ForeignKey('person_daily_goal_complete.DAILY_COMPLETE_NO'))


# class TeamWeeklyGoal(Base):
#     __tablename__ = 'team_weekly_goal'
#
#     TEAM_NO = Column(Integer, primary_key=True)
#     TEAM_NM = Column(String, default="팀 목표를 입력해주세요")
#     IS_DONE = Column(Boolean, default=False)
#     START_DT = Column(DateTime)
#     END_DT = Column(DateTime)
#
#     INSERT_DT = Column(DateTime, default=datetime.utcnow)
#     MODIFY_DT = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#
#     CHALLENGE_USER = relationship('ChallengeUser', backref="team_weekly_goal")
#     CHALLENGE_USER_NO = Column(Integer, ForeignKey('challenge_users.CHALLENGE_USER_NO'))


def get_end_dt():
    return datetime.utcnow() + timedelta(hours=24)


class AdditionalGoal(Base):
    __tablename__ = 'additional_goal'

    ADDITIONAL_NO = Column(Integer, primary_key=True)
    ADDITIONAL_NM = Column(String)
    IS_DONE = Column(Boolean, default=False)
    START_DT = Column(DateTime, default=datetime.utcnow)
    END_DT = Column(DateTime, default=get_end_dt())
    IMAGE_FILE_NM = Column(String)

    CHALLENGE_USER = relationship('ChallengeUser', backref="additional_goal")
    CHALLENGE_USER_NO = Column(Integer, ForeignKey('challenge_users.CHALLENGE_USER_NO'))


class PersonDailyGoalComplete(Base):
    __tablename__ = 'person_daily_goal_complete'

    DAILY_COMPLETE_NO = Column(Integer, primary_key=True)
    IMAGE_FILE_NM = Column(String)
    INSERT_DT = Column(DateTime, default=datetime.utcnow)
    COMMENT = Column(String)

    CHALLENGE_USER = relationship('ChallengeUser', backref="person_daily_goal_complete")
    CHALLENGE_USER_NO = Column(Integer, ForeignKey('challenge_users.CHALLENGE_USER_NO'))


class DailyCompleteUser(Base):
    __tablename__ = 'daily_complete_user'

    DAILY_COMPLETE_USER_NO = Column(Integer, primary_key=True)
    EMOJI = Column(String)
    DAILY_COMPLETE_NO = Column(Integer, ForeignKey('person_daily_goal_complete.DAILY_COMPLETE_NO'))

    CHALLENGE_USER = relationship('ChallengeUser', backref="daily_complete_user")
    CHALLENGE_USER_NO = Column(Integer, ForeignKey('challenge_users.CHALLENGE_USER_NO'))


class Item(Base):
    __tablename__ = 'item'

    ITEM_NO = Column(Integer, primary_key=True)
    ITEM_NM = Column(Enum(ItemType, name="ItemType"), nullable=False)


class ItemUser(Base):
    __tablename__ = 'item_user'

    ITEM_USER_NO = Column(Integer, primary_key=True)
    COUNT = Column(Integer, default=0)

    ITEM_NO = Column(Integer, ForeignKey("item.ITEM_NO"))

    CHALLENGE_USER = relationship('ChallengeUser', backref='item_users')
    CHALLENGE_USER_NO = Column(Integer, ForeignKey('challenge_users.CHALLENGE_USER_NO'))


class ItemLog(Base):
    __tablename__ = 'item_log'

    ITEM_LOG_NO = Column(Integer, primary_key=True)
    INSERT_DT = Column(DateTime, default=datetime.utcnow)
    IS_VIEW = Column(Boolean, default=False)

    # ITEM_NO = Column(Integer, ForeignKey("item.ITEM_NO"))
    SENDER_NO = Column(Integer, ForeignKey('challenge_users.CHALLENGE_USER_NO', ondelete='CASCADE'))
    RECIPIENT_NO = Column(Integer, ForeignKey('challenge_users.CHALLENGE_USER_NO', ondelete='CASCADE'))

    ITEM_NO = Column(Integer, ForeignKey("item.ITEM_NO"))

    sender = relationship('ChallengeUser', foreign_keys=[SENDER_NO])
    recipient = relationship('ChallengeUser', foreign_keys=[RECIPIENT_NO])
