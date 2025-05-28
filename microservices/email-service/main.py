from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.emails import router as email_router

app = FastAPI(
    title="Email Service",
    description="Microservice for email operations with Gmail integration",
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
app.include_router(email_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Email Service", "status": "running"}

@app.get("/health")
async def health():
    """
    Health check endpoint
    """
    from datetime import datetime
    import httpx
    from config import settings
    
    health_status = {
        "status": "healthy",
        "service": "email-service",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Check database connectivity
    try:
        from db.mongodb import get_email_collection
        email_collection = get_email_collection()
        email_collection.find_one()
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check user service connectivity
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.USER_SERVICE_URL}/health")
            if response.status_code == 200:
                health_status["checks"]["user_service"] = "healthy"
            else:
                health_status["checks"]["user_service"] = f"unhealthy: status {response.status_code}"
                health_status["status"] = "degraded"
    except Exception as e:
        health_status["checks"]["user_service"] = f"unreachable: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status