from flask import Blueprint, request
from pymongo.errors import DuplicateKeyError
import models
from auth import validators, utils as auth_utils
from auth.middleware import jwt_required, get_current_user_id
from utils.responses import success_response, error_response

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not username or not email or not password:
            return error_response('Username, email, and password are required', 400)
        
        is_valid, error_msg = validators.validate_username(username)
        if not is_valid:
            return error_response(error_msg, 400, {'username': [error_msg]})
        
        is_valid, error_msg = validators.validate_email(email)
        if not is_valid:
            return error_response(error_msg, 400, {'email': [error_msg]})
        
        is_valid, error_msg = validators.validate_password(password)
        if not is_valid:
            return error_response(error_msg, 400, {'password': [error_msg]})
        
        existing_user = models.get_user_by_email(email)
        if existing_user:
            return error_response('Email already registered', 409, {'email': ['Email already registered']})
        
        existing_user = models.get_user_by_username(username)
        if existing_user:
            return error_response('Username already taken', 409, {'username': ['Username already taken']})
        
        password_hash = auth_utils.hash_password(password)
        
        try:
            user = models.create_user(username, email, password_hash)
        except DuplicateKeyError:
            return error_response('Username or email already exists', 409)
        
        token = auth_utils.generate_token(user['id'], user['username'], user['email'])
        
        return success_response({
            'token': token,
            'user': user
        }, 201)
        
    except Exception as e:
        return error_response(f'Registration failed: {str(e)}', 500)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return error_response('Email and password are required', 400)
        
        user = models.get_user_by_email(email)
        
        if not user:
            return error_response('Invalid credentials', 401)
        
        if not user.get('password_hash'):
            return error_response('Account not activated. Please contact support.', 401)
        
        if not auth_utils.verify_password(password, user['password_hash']):
            return error_response('Invalid credentials', 401)
        
        if not user.get('is_active', True):
            return error_response('Account is inactive', 401)
        
        user_id = str(user['_id'])
        models.update_last_login(user_id)
        
        token = auth_utils.generate_token(user_id, user['username'], user['email'])
        
        from models import user_to_dict
        user_dict = user_to_dict(user)
        
        return success_response({
            'token': token,
            'user': user_dict
        }, 200)
        
    except Exception as e:
        return error_response(f'Login failed: {str(e)}', 500)

@auth_bp.route('/me', methods=['GET'])
@jwt_required
def get_current_user():
    try:
        user_id = get_current_user_id()
        user = models.get_user_by_id(user_id)
        
        if not user:
            return error_response('User not found', 404)
        
        return success_response({'user': user}, 200)
        
    except Exception as e:
        return error_response(f'Failed to get user: {str(e)}', 500)
