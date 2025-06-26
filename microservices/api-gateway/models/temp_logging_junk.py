################################################################################
######                                                                    ######
######                                                                    ######
######      this is the main file edited by the agent to add logging      ######
######                                                                    ######
######                                                                    ######
################################################################################


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx
import logging
import time
import os
import uuid
from pythonjsonlogger import jsonlogger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os

# Import routers
from routers import ai, auth, drafts, emails, style, users

app = FastAPI(title="Lazy Mail API Gateway")

# CORS middleware (update origin in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes under /api prefix
app.include_router(ai.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(drafts.router, prefix="/api")
app.include_router(emails.router, prefix="/api")
app.include_router(style.router, prefix = "/api")
app.include_router(users.router, prefix="/api")

# Root health check (optional)
@app.get("/")
def read_root():
    
    return {"message": "API Gateway is running."}

# Load environment variables
load_dotenv()

# Logging setup
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logger = logging.getLogger("api-gateway")
logger.setLevel(LOG_LEVEL)


# JSON formatter for logs
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s %(method)s %(path)s %(status_code)s %(duration)s %(params)s'
)
logHandler.setFormatter(formatter)
logger.handlers = [logHandler]

# Optional: Rotating file handler (commented out)
print("logger handler:", logger.handlers)  # See all attached handlers
print("######################################################")
print("###            Rotating file handler...            ###")
print("###                                                ###")
print("###                  WORKING                       ###")
from logging.handlers import RotatingFileHandler
file_handler = RotatingFileHandler('gateway.log', maxBytes=10*1024*1024, backupCount=5)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
print("###                                                ###")
print("###          Rotating file handler DONE!!          ###")
print("######################################################")

# Optional: Cloud logging handler (e.g., Google, AWS, Datadog) can be added here

SENSITIVE_FIELDS = {"password", "token", "access_token", "refresh_token", "secret"}

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 🔍 Print working directory
        print("Working directory:", os.getcwd())
        print("logger handler:", logger.handlers)  # See all attached handlers
        start_time = time.time()
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        # Attach request_id to response header for downstream tracing
        request.state.request_id = request_id
        method = request.method
        path = request.url.path
        params = dict(request.query_params)
        # Try to get body if possible (exclude sensitive fields)
        body_params = {}
        if method in ("POST", "PUT", "PATCH"):  # Only parse body for relevant methods
            try:
                body = await request.json()
                body_params = {k: ("***" if k in SENSITIVE_FIELDS else v) for k, v in body.items()}
            except Exception:
                pass
        # Merge query and body params
        all_params = {**params, **body_params}
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as exc:
            status_code = 500
            logger.error(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                    "duration": round((time.time() - start_time) * 1000, 2),
                    "params": all_params,
                },
            )
            raise
        duration = round((time.time() - start_time) * 1000, 2)
        logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration": duration,
                "params": all_params,
            },
        )
        # Add X-Request-ID to response for tracing
        if isinstance(response, Response):
            response.headers["X-Request-ID"] = request_id
        return response

# Add logging middleware
app.add_middleware(LoggingMiddleware)