from db.db_connection import DBManager
from db.db_utils import parse_period
from db.db_utils import get_local_no
from db.db_utils import get_category_no
from db.db_utils import new_category_no

from dotenv import load_dotenv
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import logging
logging.basicConfig(
    format='%(asctime)s %(levelname)s : %(message)s',
    level=logging.DEBUG,
    datefmt='%m/%d/%Y %I:%M:%S %p',
)

logging.getLogger("selenium").setLevel(logging.WARNING)

load_dotenv(".env")

event_url = os.getenv("EVENT_URL")

class EventCrawler:
    def __init__(self, debug : bool = False):

        self.debug = debug 

        # 데이터베이스 불러오는 함수
        self.db = DBManager()
        self.driver = webdriver.Chrome()
        self.driver.get(event_url)

        self.event_counter = 0

    # n개의 이벤트만 크롤링
    def crawl_events(self, limit = None, max_pages = None):
        page = 1
        crawled = 0

        while True:
            # 현재 페이지에서 이벤트 링크 가져오기
            event_links = self.get_event_links(page)
            if not event_links:
                break # 더 이상 페이지 없음

            processed = self.process_event_links(event_links, limit, crawled)
            crawled += processed

            if limit and crawled >= limit:
                break

            page += 1
            if max_pages and page > max_pages:
                break

    # 페이지 이동 후 이벤트 상세 링크 리스트 반환
    def get_event_links(self, page : int) -> list[str]:
        if page == 1:
            url = event_url   # 기본 URL (pCurrentPage 없음)
        else:
            url = f"{event_url}?pCurrentPage={page}"
        self.driver.get(url)

        try:
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, "go"))
            )
            return [
                link.get_attribute("href")
                for link in self.driver.find_elements(By.CLASS_NAME, "go")
            ]

        except TimeoutError:
            return []
        
    
    # 이벤트 상세 페이지 크롤링 및 처리한 개수 반환
    def process_event_links(self, event_links : list[str], limit : int, crawled : int) -> int:
        count = 0

        for ev_url in event_links:
            if limit and crawled + count >= limit:
                break
            self.driver.get(ev_url)
            self.scrape_event()
            count += 1

        return count

    # 상세 페이지에서 데이터 크롤링
    def scrape_event(self):
        d = self.driver

        # 타이틀 크롤링

        title = d.find_element(By.CLASS_NAME, "view_title").text.strip()
        rows = d.find_elements(By.CSS_SELECTOR, "dl")

        # 상세정보 (dl > dt/dd 구조)
        details = {}
        category_no = None
        local_no = None
        start_date, end_date, start_time, end_time = None, None, None, None
        for row in rows:
            try:
                dts = row.find_elements(By.TAG_NAME, "dt")
                dds = row.find_elements(By.TAG_NAME, "dd")
                for dt, dd in zip(dts, dds):
                    key = dt.text.strip()
                    value = dd.text.strip()

                    if "개최지역" in key:
                        local_no = get_local_no(value, self.db)

                    elif "개최기간" in key:
                        start_date, end_date, start_time, end_time = parse_period(value)

                    elif "축제성격" in key:
                        category_no = get_category_no(value, self.db)

                        if category_no is None:
                            category_no = new_category_no(value, self.db)

                            logging.debug(f"카테고리 만들었음! : {category_no}")
                    details[key] = value

                    print(f"key : {key}, value : {value}")
            except Exception:
                continue

        # 축제 설명 저장
        description = d.find_element(By.CLASS_NAME, "view_con").text.strip()

        columns, values = self.build_event_record(
            title, details, local_no, category_no,
            start_date, end_date, start_time, end_time,
            description
        )

        sql = f"""
        INSERT INTO events ({', '.join(columns)})
        VALUES ({', '.join(['?'] * len(values))})
        """

        try:
            self.db.execute(sql, values)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logging.error(f"DB 저장 실패: {e}")

        # 이벤트 카운터 증가
        self.event_counter += 1

        rows = self.db.fetchall("SELECT * FROM events")
        logging.info(rows)

        logging.info("✅ DB 저장 완료")


    # 축제 레코드 생성
    def build_event_record(self, title, details, local_no, category_no, 
                        start_date, end_date, start_time, end_time, description):

        columns = [
            "event_no",
            "local_no",
            "category_no",
            "event_name",
            "event_address",
            "event_start_date", "event_end_date", "event_start_time", "event_end_time",
            "event_url",
            "event_price",
            "event_type",
            "event_inquiry",
            "event_description"
        ]

        values = [
            self.event_counter,
            local_no,
            category_no,
            title,
            details.get("개최지역"),
            start_date, end_date, start_time, end_time,
            details.get("관련 누리집"),
            details.get("요금"),
            details.get("축제성격"),
            details.get("문의"),
            description
        ]

        if "연령제한" in details and details["연령제한"]:
            columns.insert(-2, "age_restriction")   # 위치를 원하는 곳으로 조정 가능
            values.insert(-2, details["연령제한"])

        return columns, values

if __name__ == "__main__":
    crawler = EventCrawler()
    crawler.db.close()









