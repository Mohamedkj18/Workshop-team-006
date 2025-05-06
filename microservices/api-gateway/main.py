# main.py
from fastapi import FastAPI
from routers import ai  # import our ai routes

app = FastAPI()

# Register routes
app.include_router(ai.router, prefix="/ai")

@app.get("/")
def root():
    return {"message": "API Gateway is running"}
