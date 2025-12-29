import json
import os
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
from config import CONFIG

_client = None

def get_db_connection():
    global _client
    if _client is None:
        _client = MongoClient(CONFIG["MONGODB_URI"])
    return _client

def get_collection():
    client = get_db_connection()
    db = client[CONFIG["DATABASE_NAME"]]
    collection = db[CONFIG["COLLECTION_NAME"]]
    return collection

def init_database():
    try:
        collection = get_collection()
        
        collection.create_index("username", unique=True)
        collection.create_index("email", unique=True)
        collection.create_index("created_at")
        collection.create_index("is_active")
        
        if collection.count_documents({}) == 0:
            load_sample_data()
            
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")

def user_to_dict(user_doc):
    if user_doc is None:
        return None
    
    user_dict = {
        "id": str(user_doc["_id"]),
        "username": user_doc["username"],
        "email": user_doc["email"],
        "created_at": user_doc["created_at"].isoformat() if isinstance(user_doc["created_at"], datetime) else user_doc["created_at"]
    }
    
    if "profile" in user_doc:
        user_dict["profile"] = user_doc["profile"]
    
    if "is_active" in user_doc:
        user_dict["is_active"] = user_doc["is_active"]
    
    if "last_login" in user_doc:
        user_dict["last_login"] = user_doc["last_login"].isoformat() if isinstance(user_doc["last_login"], datetime) else user_doc["last_login"]
    
    return user_dict

def get_all_users(limit=20, skip=0, sort_order='newest'):
    collection = get_collection()
    
    sort_direction = -1 if sort_order == 'newest' else 1
    
    cursor = collection.find().sort("created_at", sort_direction).skip(skip).limit(limit)
    users = [user_to_dict(user) for user in cursor]
    
    total = collection.count_documents({})
    
    return users, total

def get_user_by_id(user_id):
    try:
        obj_id = ObjectId(user_id)
    except Exception:
        raise ValueError("Invalid user ID format")
    
    collection = get_collection()
    user = collection.find_one({"_id": obj_id})
    
    return user_to_dict(user)

def get_user_by_username(username):
    collection = get_collection()
    user = collection.find_one({"username": username})
    
    return user_to_dict(user)

def get_user_by_email(email):
    collection = get_collection()
    user = collection.find_one({"email": email})
    
    return user

def create_user(username, email, password_hash):
    collection = get_collection()
    
    now = datetime.utcnow()
    user_doc = {
        "username": username,
        "email": email,
        "password_hash": password_hash,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
        "last_login": None,
        "profile": {
            "display_name": username,
            "avatar_url": ""
        }
    }
    
    result = collection.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    
    return user_to_dict(user_doc)

def update_last_login(user_id):
    try:
        obj_id = ObjectId(user_id)
    except Exception:
        raise ValueError("Invalid user ID format")
    
    collection = get_collection()
    collection.update_one(
        {"_id": obj_id},
        {"$set": {"last_login": datetime.utcnow(), "updated_at": datetime.utcnow()}}
    )

def load_sample_data():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sample_file = os.path.join(current_dir, "sample_users.json")
        
        with open(sample_file, 'r') as f:
            users = json.load(f)
        
        for user in users:
            if "created_at" in user:
                user["created_at"] = datetime.fromisoformat(user["created_at"].replace('Z', '+00:00'))
            
            user["is_active"] = False
            user["password_hash"] = ""
        
        collection = get_collection()
        collection.insert_many(users)
        
        print(f"Loaded {len(users)} sample users")
    except Exception as e:
        print(f"Error loading sample data: {e}")
