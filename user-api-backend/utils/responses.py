from flask import jsonify

def success_response(data, status=200):
    return jsonify({
        'success': True,
        'data': data
    }), status

def error_response(message, status=400, errors=None):
    response = {
        'success': False,
        'message': message
    }
    
    if errors:
        response['errors'] = errors
    
    return jsonify(response), status
