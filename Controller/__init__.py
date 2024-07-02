from sqlalchemy.orm import Session
from Database.database import SessionLocal, engine, Base
from Database.models import User  # 모델 파일의 위치에 따라 경로를 조정해야 할 수 있습니다.

# 테이블 생성 (실제 애플리케이션에서는 별도의 마이그레이션 도구를 사용하는 것이 좋습니다)
Base.metadata.create_all(bind=engine)

# 세션 생성 및 사용 예시
def test_create_user():
    # 세션 생성
    db = SessionLocal()
    try:
        # 사용자 생성
        fake_user = User(username="testuser", email="test@example.com", hashed_password="fakehashed")
        db.add(fake_user)
        db.commit()
        
        # 사용자 조회
        user = db.query(User).filter(User.username == "testuser").first()
        print(user.username)
    finally:
        db.close()

if __name__ == "__main__":
    test_create_user()