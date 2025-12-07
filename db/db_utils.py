from datetime import datetime
import re
import logging
import yaml
import pathlib

current_dir = pathlib.Path(__file__).parent

file_path = current_dir.parent / 'resources' / 'district_map.yaml'


with open(file_path, encoding='UTF-8') as f:
    district_map = yaml.full_load(f)

# 개최기간 문자열을 파싱해서 (start_date, end_date, start_time, end_time) 반환
def parse_period(period_text: str):
    try:
        # 공백 제거
        text = period_text.replace(" ", "")
        # 날짜와 시간 분리
        date_part, time_part = text.split("|")

        # 날짜 처리
        start_str, end_str = date_part.split("~")
        start_str = start_str.rstrip(".")
        end_str = end_str.rstrip(".")
        year = start_str.split(".")[0]
        if len(end_str.split(".")) == 2:
            end_str = f"{year}.{end_str}"
        start_date = datetime.strptime(start_str, "%Y.%m.%d").date()
        end_date = datetime.strptime(end_str, "%Y.%m.%d").date()

        # 시간 처리
        time_match = re.search(r"(\d{2}:\d{2})~(\d{2}:\d{2})", time_part)
        if time_match:
            start_time = datetime.strptime(time_match.group(1), "%H:%M").time()
            end_time = datetime.strptime(time_match.group(2), "%H:%M").time()
        else:
            start_time, end_time = None, None

        # H2 DB 호환용 문자열로 변환(MariaDB에 넣는 것도 문제 없음)
        start_date_str = start_date.strftime("%Y-%m-%d") if start_date else None
        end_date_str = end_date.strftime("%Y-%m-%d") if end_date else None
        start_time_str = start_time.strftime("%H:%M:%S") if start_time else None
        end_time_str = end_time.strftime("%H:%M:%S") if end_time else None

        return start_date_str, end_date_str, start_time_str, end_time_str

    except Exception as e:
        print("⚠️ 기간 파싱 실패:", e)
        return None, None, None, None

# 개최 지역 번호 추출    
def get_local_no(full_name : str, db):
    local_district, local_name = split_local_name(full_name)
    logging.debug(f"지역번호 : {local_district}" + f"지역이름 : {local_name}")
    if not local_district or not local_name:
        return None
    
    # 지역 번호 추출 SQL문
    sql = """
    SELECT local_no
    FROM local_govs
    WHERE local_district LIKE ?
        AND local_name LIKE ?
    """

    row = db.fetchone(sql, (f"%{local_district}%", f"%{local_name}%"))

    return row[0] if row else None

# 개최지역 -> 시도명, 시군구명으로 나누는 함수
def split_local_name(full_name : str):
    # "서울시 종로구" → ("서울시", "종로구")
    parts = full_name.split()
    if len(parts) >= 2:
        district = district_map.get(parts[0], parts[0])
        name = parts[1]
        return district, name
    return None, None

# 카테고리 번호 삽입 함수
def get_category_no(category : str, db):
    
    sql = """
    SELECT category_no
    FROM events_categories
    WHERE category_name = ?
    """

    row = db.fetchone(sql, (category,))

    return row[0] if row else None

# 카테고리 테이블에 카테고리명이 없으면 새로 추가
def new_category_no(category : str, db):

    sql = "INSERT INTO events_categories (category_name) VALUES (?)"
    
    db.execute(sql, (category,))

    return get_category_no(category, db)