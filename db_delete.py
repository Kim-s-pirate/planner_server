from sqlalchemy import create_engine, text

# 스키마 이름을 설정합니다.
SCHEMA_NAME = "planner"

# 데이터베이스 이름을 제외한 URL을 사용합니다.
DATABASE_URL = "mysql+mysqlconnector://rocknroll:rocknroll@localhost:3306/"

# 데이터베이스 서버에 연결하기 위한 엔진을 생성합니다.
temp_engine = create_engine(DATABASE_URL)

# 스키마 삭제 SQL 명령을 실행합니다.
with temp_engine.connect() as conn:
    conn.execute(text(f"DROP DATABASE IF EXISTS {SCHEMA_NAME}"))
    conn.commit()