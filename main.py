import os
import sys
from dotenv import load_dotenv

from db.db_setup import is_local_govs_data_exists, load_local_govs_from_csv

# 현재 실행 중인 파일(main.py)의 절대 경로를 얻음
current_file_path = os.path.abspath(__file__)
# 스크립트가 위치한 디렉토리(프로젝트 루트) 계산
project_root = os.path.dirname(current_file_path)

# 프로젝트 루트를 모듈 검색 경로에 추가하여 'crawler' 패키지를 찾도록 함
sys.path.append(project_root)

# .env 파일의 절대 경로를 계산하여 환경 변수 로드
dotenv_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path)

from crawler.event_crawler import EventCrawler

def main():
    crawler = EventCrawler(debug=True)

    try:
        db_manager = crawler.db

        if not is_local_govs_data_exists(db_manager):
            print("local_govs 초기 데이터가 없습니다. CSV 파일로부터 데이터를 로드합니다.")
            csv_file_path = 'resources/국토교통부_전국 법정동_20250807.csv'
            load_local_govs_from_csv(db_manager, csv_file_path)
            print("local_govs 초기 데이터 로드 완료")
        else:
            print("local_govs 데이터가 이미 존재합니다. 초기 데이터 로드를 건너뜁니다.")
        crawler.crawl_events(limit=10, max_pages=2)

    finally:
        crawler.driver.quit()
        crawler.db.close()

if __name__ == "__main__":
    main()