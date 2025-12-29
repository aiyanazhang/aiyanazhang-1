import bcrypt
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token
from config import CONFIG

def hash_password(password):
    salt = bcrypt.gensalt(rounds=12)
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    return password_hash.decode('utf-8')

def verify_password(password, password_hash):
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def generate_token(user_id, username, email):
    expires = timedelta(seconds=CONFIG["JWT_ACCESS_TOKEN_EXPIRES"])
    
    additional_claims = {
        "username": username,
        "email": email,
        "type": "access"
    }
    
    token = create_access_token(
        identity=str(user_id),
        additional_claims=additional_claims,
        expires_delta=expires
    )
    
    return token
