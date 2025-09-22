from datetime import datetime

from db.db_connection import DBManager
from dotenv import load_dotenv
import re
import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By

load_dotenv(".env")

event_url = os.getenv("EVENT_URL")

class EventCrawler:
    def __init__(self, debug=False, startPage=1):
        # 데이터베이스 불러오는 함수
        self.db = DBManager()
        self.driver = webdriver.Chrome()
        self.driver.get(event_url)

        # 페이지가 완전히 로딩되도록 3초동안 기다림
        time.sleep(3)

        # 이벤트 번호 카운터 초기화
        self.event_counter = 0
        self.local_counter = 0
        self.category_counter = 0


    # n개의 이벤트만 크롤링
    def crawl_events(self, limit=None, max_pages=None):
        page = 1
        crawled = 0

        while True:
            # 리스트 페이지 직접 이동 (새 DOM 보장)
            if page == 1:
                url = event_url   # 기본 URL (pCurrentPage 없음)
            else:
                url = f"{event_url}?pCurrentPage={page}"
            self.driver.get(url)
            time.sleep(2)

            # 현재 페이지의 모든 이벤트 링크를 문자열로 수집
            event_links = [
                link.get_attribute("href")
                for link in self.driver.find_elements(By.CLASS_NAME, "go")
            ]

            if not event_links:
                break  # 더 이상 페이지 없음

            for ev_url in event_links:
                self.driver.get(ev_url)   # 상세 페이지 직접 이동
                self.scrape_event()
                crawled += 1

                if limit and crawled >= limit:
                    return  # 크롤링 종료

            page += 1
            if max_pages and page > max_pages:
                break


    # 상세 페이지에서 데이터 크롤링
    def scrape_event(self, limit=None):
        d = self.driver

        # 타이틀 크롤링

        title = d.find_element(By.CLASS_NAME, "view_title").text.strip()

        # 상세정보 (dl > dt/dd 구조)
        details = {}
        local_no = None
        start_date, end_date, start_time, end_time = None, None, None, None
        rows = d.find_elements(By.CSS_SELECTOR, "dl")
        for row in rows:
            try:
                dts = row.find_elements(By.TAG_NAME, "dt")
                dds = row.find_elements(By.TAG_NAME, "dd")
                for dt, dd in zip(dts, dds):
                    key = dt.text.strip()
                    value = dd.text.strip()

                    if "개최지역" in key:
                        local_no = get_local_no(value, self.db)
                        print("asdf",local_no)

                    elif "개최기간" in key:
                        start_date, end_date, start_time, end_time = parse_period(value)
                    details[key] = value

                print(f"key : {key}, value : {value}")
            except Exception:
                continue

        # 축제 설명 저장
        description = d.find_element(By.CLASS_NAME, "view_con").text.strip()

        # 축제 DB에 저장
        columns = [
            "event_no", "local_no", "category_no", "event_name", "event_address",
            "event_start_date", "event_end_date",
            "event_start_time", "event_end_time",
            "event_url", "event_price", "event_type",
            "event_inquiry", "event_description"
        ]

        values = [
            self.event_counter,        # event_no
            local_no, 
            self.category_counter,     # category_no
            title, details.get("개최지역"),
            start_date, end_date,
            start_time, end_time,
            details.get("관련 누리집"), details.get("요금"), details.get("축제성격"),
            details.get("문의"), description
        ]

        # "연령제한"이 있으면 추가
        if "연령제한" in details and details["연령제한"]:
            columns.insert(-2, "age_restriction")   # 위치를 원하는 곳으로 조정 가능
            values.insert(-2, details["연령제한"])

        # SQL 문자열 동적 생성
        sql = f"""
        INSERT INTO events ({', '.join(columns)})
        VALUES ({', '.join(['?'] * len(values))})
        """

        self.db.execute(sql, values)
        # self.db.commit()

        # 카운터 증가
        self.event_counter += 1
        self.local_counter += 1
        self.category_counter += 1

        # 조회
        rows = self.db.fetchall("SELECT * FROM events")
        print(rows)

        print("✅ DB 저장 완료")

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

DISTRICT_MAP = {
    "서울시": "서울특별시",
    "부산시": "부산광역시",
    "대구시": "대구광역시",
    "인천시": "인천광역시",
    "광주시": "광주광역시",
    "대전시": "대전광역시",
    "울산시": "울산광역시",
    "세종시": "세종특별자치시",
    "경기도": "경기도",
    "강원도": "강원도",
    "충청북도": "충청북도",
    "충청남도": "충청남도",
    "전라북도": "전라북도",
    "전라남도": "전라남도",
    "경상북도": "경상북도",
    "경상남도": "경상남도",
    "제주도": "제주특별자치도",
}

# 개최 지역 번호 추출    
def get_local_no(full_name : str, db):
    local_district, local_name = split_local_name(full_name)
    print("냠", local_district, local_name)
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

def split_local_name(full_name: str):
    # "서울시 종로구" → ("서울시", "종로구")
    parts = full_name.split()
    if len(parts) >= 2:
        district = DISTRICT_MAP.get(parts[0], parts[0])
        name = parts[1]
        return district, name
    return None, None




if __name__ == "__main__":
    crawler = EventCrawler()
    crawler.db.close()









