import os
from dotenv import load_dotenv
import pymysql
from crawler.event_crawler import EventCrawler

load_dotenv(".env")
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

def test_crawl_7_events_mariadb():
    # MariaDB 연결(트랜잭션 수동 제어)
    conn =pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        charset='utf8mb4',
        autocommit=False
    )
    try:
        crawler = EventCrawler()
        crawler.crawl_events(limit=7)

        cursor = conn.cursor()
        rows = crawler.db.fetchall("SELECT COUNT(*) FROM events")
        print("DB에 저장된 축제 개수", rows[0][0])

        conn.rollback()

    finally:
        cursor.close()
        conn.close()
        crawler.driver.quit()

if __name__ == "__main__":
    test_crawl_7_events_mariadb()