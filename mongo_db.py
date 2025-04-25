import os
import logging
import pymongo
from pymongo import MongoClient
from urllib.parse import quote_plus

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# MongoDB connection string
# For deployment, we use MongoDB Atlas or another hosted MongoDB service
# This is a fallback URI for development (won't work in Replit without proper config)
# For Replit, we'll need to set the MONGODB_URI environment variable with a valid connection string
mongodb_uri = os.environ.get("MONGODB_URI")

# If no MongoDB URI is provided, we'll use a simulation mode where data is stored in memory
mongodb_simulation = mongodb_uri is None

# MongoDB client
client = None

# Database and collection references
db = None
users_collection = None

# In-memory storage when MongoDB is not available
in_memory_users = {}

def init_mongodb():
    """Initialize MongoDB connection or set up in-memory storage"""
    global client, db, users_collection
    
    if mongodb_simulation:
        logging.warning("MongoDB URI not provided. Using in-memory storage instead.")
        return True
    
    try:
        # Connect to MongoDB
        client = MongoClient(mongodb_uri)
        
        # Access the database
        db = client.nutrition_assistant
        
        # Access the collections
        users_collection = db.users
        
        # Create indexes for better query performance
        users_collection.create_index([("email", pymongo.ASCENDING)], unique=True)
        
        logging.info("MongoDB connection established successfully")
        return True
    
    except Exception as e:
        logging.error(f"Error connecting to MongoDB: {str(e)}")
        logging.warning("Falling back to in-memory storage.")
        return True  # Still return True to continue with in-memory mode

def save_user(user_data):
    """Save or update user data to MongoDB or in-memory storage"""
    global in_memory_users
    
    # Initialize MongoDB or in-memory storage if needed
    if not users_collection and not mongodb_simulation:
        if not init_mongodb():
            return False
    
    # Make sure we have an email
    email = user_data.get("email")
    if not email:
        logging.error("Cannot save user without email address")
        return False
    
    # Handle in-memory storage
    if mongodb_simulation:
        # If user exists, update
        if email in in_memory_users:
            in_memory_users[email].update(user_data)
        else:
            # Create a new user with a simple timestamp-based ID
            if "_id" not in user_data:
                import time
                user_data["_id"] = str(int(time.time() * 1000))
            in_memory_users[email] = user_data
        return True
    
    # Handle MongoDB storage
    try:
        # Check if user already exists by email
        existing_user = users_collection.find_one({"email": email})
        
        if existing_user:
            # Update existing user
            result = users_collection.update_one(
                {"email": email},
                {"$set": user_data}
            )
            return bool(result.modified_count)
        else:
            # Insert new user
            result = users_collection.insert_one(user_data)
            return bool(result.inserted_id)
    
    except Exception as e:
        logging.error(f"Error saving user data to MongoDB: {str(e)}")
        
        # Fallback to in-memory storage
        if email in in_memory_users:
            in_memory_users[email].update(user_data)
        else:
            if "_id" not in user_data:
                import time
                user_data["_id"] = str(int(time.time() * 1000))
            in_memory_users[email] = user_data
        
        return True

def get_user_by_email(email):
    """Get user data by email from MongoDB or in-memory storage"""
    global in_memory_users
    
    # Initialize MongoDB or in-memory storage if needed
    if not users_collection and not mongodb_simulation:
        if not init_mongodb():
            return None
    
    # Handle in-memory storage
    if mongodb_simulation:
        return in_memory_users.get(email)
    
    # Handle MongoDB storage
    try:
        return users_collection.find_one({"email": email})
    
    except Exception as e:
        logging.error(f"Error getting user data from MongoDB: {str(e)}")
        
        # Fallback to in-memory storage
        return in_memory_users.get(email)

def get_user_by_id(user_id):
    """Get user data by ID from MongoDB or in-memory storage"""
    global in_memory_users
    
    # Initialize MongoDB or in-memory storage if needed
    if not users_collection and not mongodb_simulation:
        if not init_mongodb():
            return None
    
    # Handle in-memory storage
    if mongodb_simulation:
        for user in in_memory_users.values():
            if user.get("_id") == user_id:
                return user
        return None
    
    # Handle MongoDB storage
    try:
        # Convert string ID to ObjectId
        from bson.objectid import ObjectId
        obj_id = ObjectId(user_id)
        return users_collection.find_one({"_id": obj_id})
    
    except Exception as e:
        logging.error(f"Error getting user data from MongoDB: {str(e)}")
        
        # Fallback to in-memory storage
        for user in in_memory_users.values():
            if user.get("_id") == user_id:
                return user
        return None

def delete_user(email):
    """Delete user data by email from MongoDB or in-memory storage"""
    global in_memory_users
    
    # Initialize MongoDB or in-memory storage if needed
    if not users_collection and not mongodb_simulation:
        if not init_mongodb():
            return False
    
    # Handle in-memory storage
    if mongodb_simulation:
        if email in in_memory_users:
            del in_memory_users[email]
            return True
        return False
    
    # Handle MongoDB storage
    try:
        result = users_collection.delete_one({"email": email})
        return bool(result.deleted_count)
    
    except Exception as e:
        logging.error(f"Error deleting user data from MongoDB: {str(e)}")
        
        # Fallback to in-memory storage
        if email in in_memory_users:
            del in_memory_users[email]
            return True
        return False