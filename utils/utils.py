import numpy as np
import datetime
import re

DAYS = ["요일", "(월)", "(화)", "(수)", "(목)", "(금)", "(토)", "(일)"]
CORNER_KEYWORDS = ["교직원", "교직원식당", "학생식당", "조식", "중식", "석식", "든든", "우아", "푸짐", "아침", "점심", "저녁", "T/O", "소담", "비빔코너", "One", "SET", "Self", "A", "B", "C"]

def to_py_type(x):
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        return float(x)
    if isinstance(x, (list, tuple)):
        return [to_py_type(v) for v in x]
    if isinstance(x, dict):
        return {k: to_py_type(v) for k, v in x.items()}
    return x

def parse_korean_date(text: str):
    current_year = datetime.date.today().year

    text = re.sub(r'[ \(\)\[\]{}월화수목금토일]', '', text)

    patterns = [
        r'(?P<month>\d{1,2})월(?P<day>\d{1,2})일',
        r'(?P<month>\d{1,2})월(?P<day>\d{1,2})',
        r'(?P<month>\d{1,2})일(?P<day>\d{1,2})',  # 혹시 순서 바뀐 경우
        r'(?P<month>\d{1,2})[/-](?P<day>\d{1,2})',
        r'(?P<month>\d{1,2})(?P<day>\d{1,2})',  # 12월15일 -> 1215
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            month = int(m.group('month'))
            day = int(m.group('day'))
            try:
                return datetime.date(current_year, month, day)
            except ValueError:
                return None
    return None

def parse_date_range_flexible(text):
    match = re.search(r'(\d+[\.\d]*)\s*[~\-]\s*(\d+[\.\d]*)', text)
    if not match:
        return None, None

    left_str_raw = match.group(1)
    right_str_raw = match.group(2)
    left_str = re.sub(r'\D', '', left_str_raw)
    right_str = re.sub(r'\D', '', right_str_raw)

    current_year = datetime.date.today().year
    start_date, end_date = None, None

    if len(left_str) == 6:
        y, m, d = int(left_str[:2]), int(left_str[2:4]), int(left_str[4:])
        start_date = datetime.date(2000 + y, m, d)
    elif len(left_str) == 4 and len(left_str_raw) <= 5:
        m, d = int(left_str[:2]), int(left_str[2:])
        start_date = datetime.date(current_year, m, d)
    else:
        parts = left_str_raw.split('.')
        if len(parts) == 3:
            y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
            try:
                start_date = datetime.date(2000 + y, m, d)
            except Exception:
                start_date = None
    
    if not start_date:
        return None, None

    if len(right_str) == 6:
        y, m, d = int(right_str[:2]), int(right_str[2:4]), int(right_str[4:])
        end_date = datetime.date(2000 + y, m, d)
    elif len(right_str) == 4 and len(right_str_raw) <= 5:
        m, d = int(right_str[:2]), int(right_str[2:])
        end_year = start_date.year
        if m < start_date.month:
            end_year += 1
        end_date = datetime.date(end_year, m, d)
    elif len(right_str) == 2 and len(left_str) >= 4:
        m = int(left_str[2:4]) if len(left_str) == 6 else int(left_str[:2])
        d = int(right_str)
        end_date = datetime.date(start_date.year, m, d)
    else:
        print("right_str_raw:", right_str_raw)
        parts = right_str_raw.split('.')
        if len(parts) == 3:
            y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
            try:
                end_date = datetime.date(2000 + y, m, d)
            except Exception:
                end_date = None
        
    return start_date, end_date