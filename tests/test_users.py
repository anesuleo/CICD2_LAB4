import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app, get_db
from app.models import Base

TEST_DB_URL = "sqlite+pysqlite:///file::memory:?cache=shared"  #Allow to share in memory DB since actual DB does not exist                        
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False, "uri": True})
TestingSessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base.metadata.create_all(bind=engine)

#Test database client
@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine)  #Clear database after each test run to avoid conflicts
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

#Test create user
def test_create_user(client):
    r = client.post("/api/users",
        json={"name":"Paul","email":"pl@atu.ie","age":25,"student_id":"S1234567"})
    assert r.status_code == 201