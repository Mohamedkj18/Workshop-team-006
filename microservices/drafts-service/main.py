# fast API
from fastapi                    import FastAPI

# pymongo
from pymongo.mongo_client       import MongoClient
from pymongo.server_api         import ServerApi

# my modules
from models.drafts              import *
from routes.route               import router
from utils.time_utils           import *
from utils.drafts_utils         import *

##################### Set up logging #####################
#TODO

###################### set up auth #######################
#TODO

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
################### set app and router ####################

app = FastAPI()
app.include_router(router)

##########################################################
###################                    ###################
###################     MIDDLEWARE     ###################
###################                    ###################
##########################################################
