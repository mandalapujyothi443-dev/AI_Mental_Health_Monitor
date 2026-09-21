import pytest
from app import create_app

@pytest.fixture()
def client(tmp_path):
    app = create_app()
    app.config["TESTING"] = True
    app.config["DATABASE_PATH"] = str(tmp_path / "test.db")
    from utils.database import init_db
    with app.app_context():
        init_db()
    return app.test_client()

def test_home(client):
    response = client.get("/")
    assert response.status_code == 302
