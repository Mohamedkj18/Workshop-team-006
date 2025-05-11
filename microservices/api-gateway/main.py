# main.py
from fastapi import FastAPI
from routers import ai, drafts, users, emails

app = FastAPI()

# Register routes
app.include_router(ai.router, prefix="/ai")
app.include_router(drafts.router, prefix="/drafts")

@app.get("/")
def root():
    return {"message": "API Gateway is running"}
