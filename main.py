from crawler.event_crawler import EventCrawler

def main():
    crawler = EventCrawler(debug=True)

    try:
        crawler.crawl_events(limit=10, max_pages=2)

    finally:
        crawler.driver.quit()
        crawler.db.close()

if __name__ == "__main__":
    main()