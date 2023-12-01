from datetime import datetime
import random


def calculate_challenge_progress(start_dt, end_dt):
    total_days = (end_dt - start_dt).days + 1
    elapsed_days = (datetime.utcnow().date() - start_dt).days
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
