import pytest

from api.database import get_db, Base
from api.main import app
from api import utils, models

from fastapi import status
from fastapi.testclient import TestClient

from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker

from ..config import settings


#! Setup 

SQLALCHEMY_DATABASE_URL = f'{settings.database_database}://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


usernames = ["email@gmail.com", "test@hotmail.com", "whydothat@yahoo.com", "wordhadnosensebro@iknow.com"]
invalid_usernames = ["invalidemail", "emailinvalid", "zemanemail", "testformat"]
passwords = ["password1", "password2", "password3", "password4"]
invalid_type_ids = ["abc", (), [], None]
invalid_ids = [1, 10, 100, 1000, 10000]


"""User Schema:
class User(BaseModel):
    id: int
    email: EmailStr
    password: str // password never should be returned
    created_at: datetime
"""

id_type = int
email_type = str
created_at_type = str
# only case in future the return changes to another structure
collection_type = list


@pytest.fixture
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


#! Tests

#? ROUTE -> CREATE USER -> POST METHOD -> /users
@pytest.mark.parametrize("password",[password for password in passwords])
def test_create_user_without_email(client, password):
    """
    Test containing a request to create a new user, but without email parameter,
    an error is expected, cause the Email Field is defined to don't accept null.
    """
    response = client.post("/users", json={"password": password[0]})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == {'detail': [{'loc': ['body', 'email'], 'msg': 'field required', 'type': 'value_error.missing'}]}


#? ROUTE -> CREATE USER -> POST METHOD -> /users
@pytest.mark.parametrize("invalid_username, password", [(invalid_username, password) for invalid_username, password in [*zip(invalid_usernames, passwords)]])
def test_create_user_with_invalid_email(client, invalid_username, password):
    """
    Test containing a request to create a new user, but email parameter in invalid format,
    an error is expected, cause the parameter needs to bee like an email.
    """
    response = client.post("/users", json={"email": invalid_username, "password": password})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == {'detail': [{'loc': ['body', 'email'], 'msg': 'value is not a valid email address', 'type': 'value_error.email'}]}


#? ROUTE -> CREATE USER -> POST METHOD -> /users
@pytest.mark.parametrize("username", [username for username in usernames])
def test_create_user_without_password(client, username):
    """
    Test containing a request to create a new user, but without password parameter,
    an error is expected, cause the Password Field is defined to don't accept null.
    """
    response = client.post("/users", json={"email": username})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == {'detail':
        [{'loc': ['body', 'password'],
          'msg': 'field required',
          'type': 'value_error.missing'}]}


#? ROUTE -> CREATE USER -> POST METHOD -> /users
@pytest.mark.parametrize("username, password", [(username, password) for username, password in [*zip(usernames, passwords)]])
def test_create_user_with_existing_email(client, session, username, password):
    """
    Test containing a request to create a new user, but with a existing email in db,
    an error is expected, cause the Email Field is setted to be unique.
    """

    # CREATEA USER IN DB
    hashed_password = utils.hash(password)
    user_data = {"email": username, "password": hashed_password}
    user = models.User(**user_data)
    session.add(user)
    session.commit()
    session.refresh(user)

    response = client.post("/users", json={"email": username, "password": password})

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"message": f"user with email: {username} already exist."}


#? ROUTE -> CREATE USER -> POST METHOD -> /users
@pytest.mark.parametrize("username, password", [(username, password) for username, password in [*zip(usernames, passwords)]])
def test_create_user_with_correct_parameters(client, username, password):
    """
    Test containing a request to users, no user was created, 
    then an empty list is expected.
    """
    response = client.post("/users", json={"email": username, "password": password})
    assert response.status_code == status.HTTP_201_CREATED
    assert type(response.json()["id"]) == int
    assert response.json()["email"] == username
    assert "created_at" in response.json()


    #? READ USER SECTION

#? ROUTE -> GET USER -> GET METHOD -> /users
def test_read_empty_users(client):
    """
    Test containing a request to users, no user was created, 
    then an empty list is expected.
    """
    response = client.get("/users")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []
    assert type(response.json()) == collection_type


#? ROUTE -> GET USER -> GET METHOD -> /users
@pytest.mark.parametrize("username, password", [(usernames[:i+1], passwords[:i+1]) for i in range(min(len(usernames), len(passwords)))])
def test_read_list_users(client, session, username, password):
    """
    Test containing a request to users, user was created, 
    then an list with one user is expected.
    """

    # CREATEA USERS IN DB
    for email, password_to_hash in [*zip(username, password)]:
        hashed_password = utils.hash(password_to_hash)
        user_data = {"email": email, "password": hashed_password}
        user = models.User(**user_data)
        session.add(user)
        session.commit()
        session.refresh(user)

    response = client.get("users")
    users_list = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert type(users_list) == collection_type
    # the min() is needed cause needs to be compared with the shortest list, cause in zip, the shortest will limit the larger.
    assert len(users_list) == min(len(username), len(password))
    # zip is needed again to don't throw an error wen the username list is bigger then password list, casue in zip, the sortest will limit the larger.
    for index, pair in enumerate([*zip(username, password)]):
        assert type(users_list[index]["email"]) == email_type
        assert type(users_list[index]["id"]) == id_type
        assert type(users_list[index]["created_at"]) == created_at_type
        assert users_list[index]["email"] == pair[0]


#? ROUTE -> GET USER -> GET METHOD -> /users
@pytest.mark.parametrize("id", [id for id in invalid_type_ids])
def test_read_one_user_with_invalid_type_id(client, id):
    """
    Test containing a request to users with an id in incorrect format parameter,
    then an Not Found for route is expected.
    """
    response = client.get(f"user/{id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND 
    assert response.json() == {"detail": "Not Found"}


#? ROUTE -> GET USER -> GET METHOD -> /users
@pytest.mark.parametrize("id", [id for id in invalid_ids])
def test_read_one_user_with_inexistent_id(client, id):
    """
    Test containing a request to users with an id in correct format parameter,
    no user was created then an 404 Not Found for user is expected.
    """
    response = client.get(f"users/{id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'message': f'user with id: {id} was not found.'}


#? ROUTE -> GET USER -> GET METHOD -> /users
@pytest.mark.parametrize("username, password", [(username, password) for username, password in [*zip(usernames, passwords)]])
def test_read_one_user_by_id(client, session, username, password):
    """
    Test containing a request to users, user was created, 
    then an list with one user is expected.
    """

    # CREATEA USERS IN DB
    hashed_password = utils.hash(password)
    user_data = {"email": username, "password": hashed_password}
    user = models.User(**user_data)
    session.add(user)
    session.commit()
    session.refresh(user)

    response = client.get(f"users/{str(user.id)}")
    user_response = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert type(user_response["id"]) == id_type
    assert type(user_response["email"]) == email_type
    assert type(user_response["created_at"]) == created_at_type
    assert user_response["email"] == user.email


    #? UPDATE USER SECTION 
        #? ROUTE -> UPDATE USER -> PUT METHOD -> /users 

    #? DELETE USER SECTION 
        #? ROUTE -> DELETE USER -> DELETE METHOD -> /users

    #? CHANGE PASSWORD SECTION    
        #? ROUTE -> DELETE USER -> DELETE METHOD -> /users
