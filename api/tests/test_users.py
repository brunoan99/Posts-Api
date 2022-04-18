from api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_read_users_list_like():
    response = client.get("/users")
    assert response.status_code == 200
    assert type(response.json()) == list
