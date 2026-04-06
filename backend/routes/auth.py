from flask import Blueprint, request, jsonify
import bcrypt
import jwt
import datetime
import os
from utils.db import get_db_connection

auth_bp = Blueprint('auth', __name__)
SECRET_KEY = os.getenv('JWT_SECRET', 'supersecrethleemskey')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing User ID or password'}), 400

    username = data.get('username') # Maps to their ID now
    password = data.get('password')

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Query base user
            sql = "SELECT * FROM users WHERE id = %s"
            cursor.execute(sql, (username,))
            user = cursor.fetchone()

            if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                profile_data = {}
                if user['role'] == 'student':
                    cursor.execute("SELECT * FROM student WHERE student_id = %s", (user['id'],))
                    student_data = cursor.fetchone()
                    if student_data:
                        profile_data = student_data
                elif user['role'] == 'warden':
                    cursor.execute("SELECT * FROM warden WHERE warden_id = %s", (user['id'],))
                    warden_data = cursor.fetchone()
                    if warden_data:
                        profile_data = warden_data

                token_data = {
                    'user_id': user['id'],
                    'role': user['role'],
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
                }
                token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")
                
                return jsonify({
                    'message': 'Login successful',
                    'token': token,
                    'user': {
                        'id': user['id'],
                        'role': user['role'],
                        'profile': profile_data
                    }
                }), 200
            else:
                return jsonify({'error': 'Invalid User ID or password'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()
