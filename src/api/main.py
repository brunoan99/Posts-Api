from fastapi import FastAPI

from .routers import post, user, auth, comment, like_comment, like_post
from .database import engine
from . import models


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(comment.router)
app.include_router(like_comment.router)
app.include_router(like_post.router)


@app.get("/")
def hello_world():
    return {"message": "Welcome to my API"}
