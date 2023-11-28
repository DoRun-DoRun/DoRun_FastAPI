from datetime import datetime


def calculate_progress(start_dt, end_dt):
    total_days = (end_dt - start_dt).days + 1
    elapsed_days = (datetime.utcnow().date() - start_dt).days
    return min(max(elapsed_days / total_days * 100, 0), 100)  # 0에서 100 사이의 값을 반환

