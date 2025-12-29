from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import datetime
import models
from config import CONFIG
from auth.routes import auth_bp
from auth.middleware import jwt_required

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = CONFIG['JWT_SECRET_KEY']
CORS(app)

jwt = JWTManager(app)

models.init_database()

app.register_blueprint(auth_bp)

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        models.get_collection()
        return jsonify({
            'success': True,
            'data': {
                'status': 'healthy',
                'database': 'connected',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Health check failed: {str(e)}'
        }), 500

@app.route('/api/users', methods=['GET'])
@jwt_required
def get_users():
    try:
        limit = request.args.get('limit', default=20, type=int)
        skip = request.args.get('skip', default=0, type=int)
        sort = request.args.get('sort', default='newest', type=str)
        
        if limit <= 0 or limit > 100:
            return jsonify({
                'success': False,
                'message': 'Limit must be between 1 and 100'
            }), 400
        
        if skip < 0:
            return jsonify({
                'success': False,
                'message': 'Skip must be non-negative'
            }), 400
        
        if sort not in ['newest', 'oldest']:
            return jsonify({
                'success': False,
                'message': 'Sort must be "newest" or "oldest"'
            }), 400
        
        users, total = models.get_all_users(limit, skip, sort)
        
        return jsonify({
            'success': True,
            'data': {
                'users': users,
                'count': len(users),
                'total': total
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/users/<user_id>', methods=['GET'])
@jwt_required
def get_user_by_id(user_id):
    try:
        user = models.get_user_by_id(user_id)
        
        if user is None:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': user
        }), 200
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/users/username/<username>', methods=['GET'])
@jwt_required
def get_user_by_username(username):
    try:
        user = models.get_user_by_username(username)
        
        if user is None:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': user
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({
        'success': False,
        'message': f'An unexpected error occurred: {str(e)}'
    }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
