import jwt
import os
from functools import wraps
from flask import request, jsonify

SECRET_KEY = os.getenv('JWT_SECRET', 'supersecrethleemskey')

def token_required(allowed_roles=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Token is missing or invalid format!'}), 401

            token = auth_header.split(' ')[1]
            try:
                data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                current_user = data
                if allowed_roles and current_user['role'] not in allowed_roles:
                    return jsonify({'error': 'Access denied: insufficient permissions!'}), 403
            except jwt.ExpiredSignatureError:
                return jsonify({'error': 'Token has expired!'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'error': 'Token is invalid!'}), 401

            return f(current_user, *args, **kwargs)
        return decorated
    return decorator
