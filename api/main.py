from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import post, user, auth, comment, like_comment, like_post

origins = ["*"]

app = FastAPI(
    title="PostsApp", 
    version="0.0.1",
    contact={"name": "Bruno Andrade", 
             "email": "brunoan99@gmail.com"}
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(comment.router)
app.include_router(like_post.router)
app.include_router(like_comment.router)


@app.get("/")
def hello_world():
    return {"message": "Welcome to my API"}
