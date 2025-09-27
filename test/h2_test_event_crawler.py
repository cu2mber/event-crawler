import os
from dotenv import load_dotenv

from crawler.event_crawler import EventCrawler

load_dotenv(".env")
event_url = os.getenv("EVENT_URL")

# h2 database
# pytest로 통합 테스트. 7개 지역 축제 크롤링
def test_crawl_7_events():
    crawler = EventCrawler()
    crawler.crawl_events(limit=7)

    rows = crawler.db.fetchall("SELECT COUNT(*) FROM events")
    print("DB에 저장된 축제 개수:", rows[0][0])

    crawler.db.close()
    crawler.driver.quit()

if __name__ == "__main__":
    test_crawl_7_events()