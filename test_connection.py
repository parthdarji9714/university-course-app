import os
from pymongo import MongoClient

mongo_uri = os.getenv('MONGODB_URI')

try:
    mongo = MongoClient(mongo_uri)
    print("Connection successful!")
    print(mongo.server_info())
except Exception as e:
    print(f"Connection failed: {e}")
