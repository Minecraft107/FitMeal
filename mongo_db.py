import os
import logging
import pymongo
from pymongo import MongoClient
from urllib.parse import quote_plus

# Configure logging
logging.basicConfig(level=logging.DEBUG)

mongodb_uri = os.environ.get("MONGODB_URI")

mongodb_simulation = mongodb_uri is None

client = None
db = None
users_collection = None
auth_collection = None

in_memory_profiles = {}
in_memory_auth = {}

def init_mongodb():
    global client, db, users_collection, auth_collection
    
    if mongodb_simulation:
        logging.warning("MongoDB URI not provided. Using in-memory storage instead.")
        return True
    
    try:
        client = MongoClient(mongodb_uri)
        db = client.fitmeal
        
        users_collection = db.users
        auth_collection = db.auth_users
        
        users_collection.create_index([("email", pymongo.ASCENDING)], unique=True)
        auth_collection.create_index([("username", pymongo.ASCENDING)], unique=True)
        
        logging.info("MongoDB connection established successfully")
        return True
    
    except Exception as e:
        logging.error(f"Error connecting to MongoDB: {str(e)}")
        logging.warning("Falling back to in-memory storage.")
        return True

def save_user(user_data):
    global in_memory_profiles
    
    if not users_collection and not mongodb_simulation:
        if not init_mongodb():
            return False
    
    email = user_data.get("email")
    if not email:
        logging.error("Cannot save user without email address")
        return False
    
    if mongodb_simulation:
        if email in in_memory_profiles:
            in_memory_profiles[email].update(user_data)
        else:
            if "_id" not in user_data:
                import time
                user_data["_id"] = str(int(time.time() * 1000))
            in_memory_profiles[email] = user_data
        return True
    
    try:
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            result = users_collection.update_one(
                {"email": email},
                {"$set": user_data}
            )
            return bool(result.modified_count)
        else:
            result = users_collection.insert_one(user_data)
            return bool(result.inserted_id)
    
    except Exception as e:
        logging.error(f"Error saving user data to MongoDB: {str(e)}")
        if email in in_memory_profiles:
            in_memory_profiles[email].update(user_data)
        else:
            if "_id" not in user_data:
                import time
                user_data["_id"] = str(int(time.time() * 1000))
            in_memory_profiles[email] = user_data
        return True

def get_user_by_email(email):
    global in_memory_profiles
    
    if not users_collection and not mongodb_simulation:
        if not init_mongodb():
            return None
    
    if mongodb_simulation:
        return in_memory_profiles.get(email)
    
    try:
        return users_collection.find_one({"email": email})
    
    except Exception as e:
        logging.error(f"Error getting user data from MongoDB: {str(e)}")
        return in_memory_profiles.get(email)

def get_user_by_id(user_id):
    global in_memory_profiles
    
    if not users_collection and not mongodb_simulation:
        if not init_mongodb():
            return None
    
    if mongodb_simulation:
        for user in in_memory_profiles.values():
            if user.get("_id") == user_id:
                return user
        return None
    
    try:
        from bson.objectid import ObjectId
        obj_id = ObjectId(user_id)
        return users_collection.find_one({"_id": obj_id})
    
    except Exception as e:
        logging.error(f"Error getting user data from MongoDB: {str(e)}")
        for user in in_memory_profiles.values():
            if user.get("_id") == user_id:
                return user
        return None

def delete_user(email):
    global in_memory_profiles
    
    if not users_collection and not mongodb_simulation:
        if not init_mongodb():
            return False
    
    if mongodb_simulation:
        if email in in_memory_profiles:
            del in_memory_profiles[email]
            return True
        return False
    
    try:
        result = users_collection.delete_one({"email": email})
        return bool(result.deleted_count)
    
    except Exception as e:
        logging.error(f"Error deleting user data from MongoDB: {str(e)}")
        if email in in_memory_profiles:
            del in_memory_profiles[email]
            return True
        return False

def create_user(username, email, password_hash, full_name):
    global in_memory_auth
    
    if not auth_collection and not mongodb_simulation:
        if not init_mongodb():
            return False
    
    user_data = {
        "username": username,
        "email": email,
        "password_hash": password_hash,
        "full_name": full_name,
        "created_at": __import__('time').time()
    }
    
    if mongodb_simulation:
        if username in in_memory_auth:
            return False
        in_memory_auth[username] = user_data
        return True
    
    try:
        existing = auth_collection.find_one({"username": username})
        if existing:
            return False
        result = auth_collection.insert_one(user_data)
        return bool(result.inserted_id)
    except Exception as e:
        logging.error(f"Error creating user: {str(e)}")
        if username not in in_memory_auth:
            in_memory_auth[username] = user_data
        return True

def get_user_by_username(username):
    global in_memory_auth
    
    if not auth_collection and not mongodb_simulation:
        if not init_mongodb():
            return None
    
    if mongodb_simulation:
        return in_memory_auth.get(username)
    
    try:
        return auth_collection.find_one({"username": username})
    except Exception as e:
        logging.error(f"Error getting user by username: {str(e)}")
        return in_memory_auth.get(username)