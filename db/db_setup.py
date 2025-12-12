import csv
import os
from db.db_connection import DBManager

# CSV 파일을 읽어 localgov.local_govs 테이블에 지자체 정보를 삽입하는 함수
def load_local_govs_from_csv(db_manager: DBManager, csv_path : str):
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        full_csv_path = os.path.join(project_root, csv_path)

        # 지자체 데이터 추출
        data_to_insert = []
        with open(full_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader) # 헤더 스킵

        for row in reader:
            data_to_insert.append((row[1], row[2]))

        sql = "INSERT IGNORE INTO localgov.local_govs (local_district, local_name) VALUES (%s, %s)"

        cursor = db_manager.conn.cursor()
        cursor.executemany(sql, data_to_insert)
        db_manager.conn.commit()
        print(f"{cursor.rowcount}개의 지자체 정보가 local_govs 테이블에 삽입되었습니다.")

    except FileNotFoundError:
        print(f"Error: CSV 파일 '{full_csv_path}'을 찾을 수 없습니다.")
        # 에러 처리
    except Exception as e:
        print(f"DB 삽입 중 오류 발생: {e}")
        db_manager.conn.rollback()
    # 에러 처리
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()

# localgov.local_govs 테이블 데이터 여부 확인
def is_local_govs_data_exists(db_manager: DBManager) -> bool:
    query = "SELECT EXISTS (SELECT 1 FROM localgov.local_govs LIMIT 1)"

    result = db_manager.fetchone(query)

    return result[0] == 1 if result else False