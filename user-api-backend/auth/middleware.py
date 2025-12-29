from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt

def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Unauthorized access'
            }), 401
    return wrapper

def get_current_user_id():
    return get_jwt_identity()

def get_current_user_claims():
    return get_jwt()
