from fastapi                    import FastAPI
from pymongo.mongo_client       import MongoClient
from pymongo.server_api         import ServerApi
from os                         import getenv

# my modules
from routes.route               import router
from starlette.middleware.base  import BaseHTTPMiddleware
from middleware.middlewares     import log_middleware
from logger.loggers             import root_logger


# Connect to MongoDB
DRAFTS_MONGO_USERNAME = getenv("DRAFTS_MONGO_USERNAME")
DRAFTS_MONGO_PASSWORD = getenv("DRAFTS_MONGO_PASSWORD")
uri = f"mongodb+srv://{DRAFTS_MONGO_USERNAME}:{DRAFTS_MONGO_PASSWORD}@cluster0.79pz2ce.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))
try:
    client.admin.command('ping')
    root_logger.info("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    root_logger.error(f"MongoDB connection failed: {e}")

app = FastAPI()

# Register routers
app.include_router(router)

# middlewares
app.add_middleware(BaseHTTPMiddleware, dispatch=log_middleware)
