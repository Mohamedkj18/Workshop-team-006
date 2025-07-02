from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import email_generation, reply_generation
from starlette.middleware.base  import BaseHTTPMiddleware
from middleware.middlewares     import log_middleware

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

# middlewares
app.add_middleware(BaseHTTPMiddleware, dispatch=log_middleware)