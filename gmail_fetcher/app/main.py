from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from app.routes.email import router as email_router
from app.routes.auth import router as auth_router


from app.routes import auth, email

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create FastAPI app
app = FastAPI(title="Gmail Fetcher API")



# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(email_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to Gmail Fetcher API"}