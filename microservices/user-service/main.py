from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth import router as auth_router

app = FastAPI(
    title="User Authentication Service",
    description="Microservice for user authentication and management",
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
app.include_router(auth_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "User Authentication Service", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "user-service"}