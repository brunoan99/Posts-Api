from api.main import app

from fastapi import status
from fastapi.testclient import TestClient

client = TestClient(app)


def test_read_posts_list_like():
    response = client.get("/posts")
    assert response.status_code == status.HTTP_200_OK
    assert type(response.json()) == list


def test_create_post_without_login():
    response = client.post("/posts")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


 
def test_search_post_id_non_int():
    response = client.get(f"/posts/test")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == {'detail':
        [{'loc': 
            ['path', 'post_id'],
            'msg': 'value is not a valid integer',
            'type': 'type_error.integer'}]}


def test_search_no_post_id_zero():
    response = client.get(f"/posts/{str(0)}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"message": f"post with id: {str(0)} was not found."}
