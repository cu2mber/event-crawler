from crawler.event_crawler import EventCrawler
from db.db_connection import DBManager

def test_crawl_7_events_mariadb():
    
    conn = DBManager()

    try:

        crawler = EventCrawler()
        crawler.crawl_events(limit=20)

        rows = crawler.db.fetchall("SELECT COUNT(*) FROM events")
        print("DB에 저장된 축제 개수", rows[0][0])

        conn.rollback()

    finally:
        conn.close()
        crawler.driver.quit()

if __name__ == "__main__":
    test_crawl_7_events_mariadb()