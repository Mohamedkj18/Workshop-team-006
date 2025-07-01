from fastapi import FastAPI
from routes.email import router as email_router
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base  import BaseHTTPMiddleware
from middleware.middlewares     import log_middleware
from logger.loggers             import root_logger

app = FastAPI(
    title="Email Service",
    description="Handles sending and receiving emails for users",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(email_router)

@app.on_event("startup")
async def startup_event():
    root_logger.info("Email service is starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    root_logger.info("Email service is shutting down...")

# middlewares
app.add_middleware(BaseHTTPMiddleware, dispatch=log_middleware)
