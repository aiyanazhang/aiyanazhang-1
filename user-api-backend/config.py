import os
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    "MONGODB_URI": os.getenv("MONGODB_URI", "mongodb://localhost:27017/"),
    "DATABASE_NAME": os.getenv("DATABASE_NAME", "user_database"),
    "COLLECTION_NAME": os.getenv("COLLECTION_NAME", "users"),
    "DEBUG_MODE": os.getenv("DEBUG_MODE", "True") == "True",
    "CORS_ORIGINS": os.getenv("CORS_ORIGINS", "*"),
    "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production"),
    "JWT_ACCESS_TOKEN_EXPIRES": int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "3600"))
}
