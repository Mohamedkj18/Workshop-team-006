from fastapi                    import FastAPI
from fastapi.middleware.cors    import CORSMiddleware
from middleware                 import log_middleware
from starlette.middleware.base  import BaseHTTPMiddleware
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

# middleware
app.add_middleware(BaseHTTPMiddleware, dispatch=log_middleware)

# Root health check (optional)
@app.get("/")
def read_root():
    return {"message": "API Gateway is running."}


