# fast API
from fastapi                    import Depends, FastAPI, HTTPException, Request, status, Query
from fastapi.staticfiles        import StaticFiles
from fastapi.responses          import FileResponse
from fastapi.middleware.cors    import CORSMiddleware
from fastapi.security           import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# my modules
from models.drafts              import *
from security_middleware        import rate_limit_middleware
from routes.route               import router
from utils.time_utils           import *
from utils.draft_utils          import *

# pymongo
from pymongo.mongo_client       import MongoClient
from pymongo.server_api         import ServerApi

# additional
from starlette.middleware.base  import BaseHTTPMiddleware
from starlette.responses        import JSONResponse
import logging
from typing                     import Optional, List
from uuid                       import uuid4
from datetime                   import datetime, timezone, timedelta
from collections                import defaultdict, deque
from jose                       import JWTError, jwt
from passlib.context            import CryptContext

SECRET_KEY = "c54cf3a049fba660dc8a9ee4c560282fa8895689d83be1f7b66041e0a3af5aae"
ASLORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

##################### Set up logging #####################
logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


################### Connect to MongoDB ###################
MONGO_USERNAME = "abomokh"
MONGO_PASSWORD = "UhU86crgAotnAz5W"
uri = f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@cluster0.79pz2ce.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


###################### set up auth #######################
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="Token")




app = FastAPI()
app.include_router(router)



##########################################################
###################                    ###################
###################     MIDDLEWARE     ###################
###################                    ###################
##########################################################





