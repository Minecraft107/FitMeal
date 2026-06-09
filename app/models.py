import os
import logging
import pymongo
from pymongo import MongoClient
from time import time

logger = logging.getLogger(__name__)

_client = None
_db = None
_profiles_coll = None
_auth_coll = None
_in_memory = True
_in_memory_profiles = {}
_in_memory_auth = {}


def init_db():
    global _client, _db, _profiles_coll, _auth_coll, _in_memory

    uri = os.environ.get("MONGODB_URI")
    if not uri:
        logger.warning("MONGODB_URI not set — using in-memory storage")
        _in_memory = True
        return

    try:
        _client = MongoClient(uri)
        _db = _client.fitmeal
        _profiles_coll = _db.users
        _auth_coll = _db.auth_users
        _profiles_coll.create_index([("email", pymongo.ASCENDING)], unique=True)
        _auth_coll.create_index([("username", pymongo.ASCENDING)], unique=True)
        _in_memory = False
        logger.info("MongoDB connected")
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e} — falling back to in-memory")
        _in_memory = True


def create_user(username, email, password_hash, full_name):
    if _in_memory:
        if username in _in_memory_auth:
            return False
        _in_memory_auth[username] = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "full_name": full_name,
            "created_at": time(),
        }
        return True

    try:
        if _auth_coll.find_one({"username": username}):
            return False
        result = _auth_coll.insert_one({
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "full_name": full_name,
            "created_at": time(),
        })
        return bool(result.inserted_id)
    except Exception as e:
        logger.error(f"create_user error: {e}")
        return False


def get_user_by_username(username):
    if _in_memory:
        return _in_memory_auth.get(username)

    try:
        return _auth_coll.find_one({"username": username})
    except Exception as e:
        logger.error(f"get_user_by_username error: {e}")
        return _in_memory_auth.get(username)


def save_profile(data):
    email = data.get("email")
    if not email:
        logger.error("save_profile: no email")
        return False

    if _in_memory:
        if "_id" not in data:
            data["_id"] = str(int(time() * 1000))
        _in_memory_profiles[email] = data
        return True

    try:
        existing = _profiles_coll.find_one({"email": email})
        if existing:
            result = _profiles_coll.update_one({"email": email}, {"$set": data})
            return bool(result.modified_count)
        result = _profiles_coll.insert_one(data)
        return bool(result.inserted_id)
    except Exception as e:
        logger.error(f"save_profile error: {e}")
        if "_id" not in data:
            data["_id"] = str(int(time() * 1000))
        _in_memory_profiles[email] = data
        return True


def get_profile_by_email(email):
    if _in_memory:
        return _in_memory_profiles.get(email)

    try:
        return _profiles_coll.find_one({"email": email})
    except Exception as e:
        logger.error(f"get_profile_by_email error: {e}")
        return _in_memory_profiles.get(email)
