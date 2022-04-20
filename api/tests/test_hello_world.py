from api.main import app

from fastapi import status
from fastapi.testclient import TestClient

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    response.json() == {"message": "Welcome to my API"}
