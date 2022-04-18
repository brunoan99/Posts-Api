from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(item: str):
    return pwd_context.hash(item)


def verify(item: str, hashed_item: str):
    return pwd_context.verify(item, hashed_item)
