from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import email_generation, reply_generation, learning_profile

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(email_generation.router)
app.include_router(reply_generation.router)
app.include_router(learning_profile.router)