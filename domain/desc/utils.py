import enum
from datetime import datetime
import random

from sqlalchemy import not_

from models import Item, AvatarUser, Avatar


def calculate_challenge_progress(start_dt, end_dt):
    # datetime.datetime을 datetime.date로 변환
    start_date = start_dt.date()
    end_date = end_dt.date()

    total_days = (end_date - start_date).days + 1
    elapsed_days = (datetime.utcnow().date() - start_date).days
    return min(max(elapsed_days / total_days * 100, 0), 100)  # 0에서 100 사이의 값을 반환


adjectives = [
    "가냘픈", "강직한", "고결한", "고고한", "귀여운", "그윽한",
    "까다로운", "깔끔한", "깜찍한", "날렵한", "낭만적인", "넉넉한", "노련한",
    "다정한", "단단한", "담백한", "당당한", "대범한", "도도한", "독창적인", "독특한",
    "똑똑한", "따뜻한", "따스한", "맑은눈의", "매력적인", "매끈한", "멋진",
    "명랑한", "몽환적인", "무심한", "미려한", "반짝이는", "부드러운", "불타는",
    "사랑스런", "사려깊은", "상냥한", "새침한", "서글픈", "소중한", "수줍은", "신비로운",
    "싱그러운", "아름다운"
]

beans = [
    "콩", "팥", "완두콩", "강낭콩", "녹두", "렌틸콩", "검은콩", "서리태", "병아리콩", "땅콩",
    "흰콩", "리마콩", "네이비콩", "소야콩", "적두", "보리콩", "자이언트콩", "파바콩", "커피콩"
]


def random_user():
    adjective = random.choice(adjectives)
    noun = random.choice(beans)
    username = adjective + " " + noun
    return username


class RewardType(enum.Enum):
    AVATAR = "Avatar"
    ITEM = "Item"
    NOTHING = "Nothing"


def select_randomly_with_probability(avatar, item, nothing, duration):
    choices = list(RewardType)
    total_prob = avatar + duration + item + nothing
    selected = \
        random.choices(choices, weights=[(avatar + duration) / total_prob, item / total_prob, nothing / total_prob],
                       k=1)[0]

    return selected


def get_random_item(db_session):
    # Item 테이블에서 모든 요소 가져오기
    items = db_session.query(Item).all()

    if not items:
        return None  # 아이템이 없는 경우

    # 무작위로 하나의 아이템 선택
    random_item = random.choice(items)
    return random_item


def get_random_avatar_not_owned_by_user(db_session, user_no):
    # 유저가 소유한 악세사리의 목록을 가져옴
    owned_avatars = db_session.query(AvatarUser.AVATAR_NO).filter(AvatarUser.USER_NO == user_no).all()
    owned_avatars_ids = [avatar.AVATAR_NO for avatar in owned_avatars]

    # 유저가 소유하지 않은 악세사리를 찾음
    available_avatars = db_session.query(Avatar).filter(not_(Avatar.AVATAR_NO.in_(owned_avatars_ids))).all()

    if not available_avatars:
        return None  # 사용자가 모든 악세사리를 소유하고 있거나 사용 가능한 악세사리가 없는 경우

    # 랜덤하게 하나의 악세사리 선택
    random_avatar = random.choice(available_avatars)
    return random_avatar
