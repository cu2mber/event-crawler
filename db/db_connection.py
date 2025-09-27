from dotenv import load_dotenv
import os
import jaydebeapi
import logging
logging.basicConfig(
    format='%(asctime)s %(levelname)s : %(message)s',
    level=logging.DEBUG,
    datefmt='%m/%d/%Y %I:%M:%S %p',
)

logging.getLogger("selenium").setLevel(logging.WARNING)

class DBManager:

    def __init__(self):
        load_dotenv(".env")
        self.db_url = os.getenv("DB_URL")
        self.db_user = os.getenv("DB_USER")
        self.db_password = os.getenv("DB_PASSWORD")
        self.db_driver = os.getenv("DB_DRIVER")
        self.db_jar = os.getenv("DB_JAR")  # H2나 MariaDB JDBC JAR 경로

        # DB 연결
        self.conn = jaydebeapi.connect(
            self.db_driver,
            self.db_url,
            [self.db_user, self.db_password],
            self.db_jar
        )
        self.cursor = self.conn.cursor()

    def execute(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor
        # 스택 트레이스까지 보고싶을 때
        except Exception as e:
            logging.error("⚠️ SQL 실행 오류", exc_info=True)
            return None

    def fetchall(self, query, params=None):
        cur = self.execute(query, params)
        return cur.fetchall() if cur else []

    def fetchone(self, query, params=None):
        cur = self.execute(query, params)
        return cur.fetchone() if cur else None

    def commit(self):
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def rollback(self):
        self.conn.rollback()

