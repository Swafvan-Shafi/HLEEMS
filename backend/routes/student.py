from flask import Blueprint, request, jsonify
from utils.db import get_db_connection
from utils.auth_middleware import token_required
import bcrypt

student_bp = Blueprint('student', __name__)

@student_bp.route('/password', methods=['PUT'])
@token_required(allowed_roles=['student'])
def change_password(current_user):
    data = request.get_json()
    current_pw = data.get('current_password')
    new_pw = data.get('new_password')
    confirm_pw = data.get('confirm_password')

    if not all([current_pw, new_pw, confirm_pw]):
        return jsonify({'error': 'All password fields are required'}), 400
    if new_pw != confirm_pw:
        return jsonify({'error': 'New passwords do not match'}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT password_hash FROM users WHERE id = %s", (current_user['user_id'],))
            user = cursor.fetchone()
            if not user or not bcrypt.checkpw(current_pw.encode('utf-8'), user['password_hash'].encode('utf-8')):
                return jsonify({'error': 'Incorrect current password'}), 401
            
            hashed = bcrypt.hashpw(new_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (hashed, current_user['user_id']))
        connection.commit()
        return jsonify({'message': 'Password updated successfully'}), 200
    except Exception as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()


@student_bp.route('/requests', methods=['POST'])
@token_required(allowed_roles=['student'])
def create_request(current_user):
    data = request.get_json()
    req_type = data.get('request_type')
    reason = data.get('reason')

    if not req_type or not reason:
        return jsonify({'error': 'Missing required fields (request_type, reason)'}), 400

    entry_date = None
    entry_time = None
    exit_time = None
    reentry_time = None

    if req_type == 'late_entry':
        entry_date = data.get('entry_date')
        entry_time = data.get('entry_time')
        if not entry_date or not entry_time:
            return jsonify({'error': 'Entry date and time are required for late entry request'}), 400
    elif req_type == 'exit':
        exit_time = data.get('exit_time')
        reentry_time = data.get('reentry_time')
        if not exit_time or not reentry_time:
            return jsonify({'error': 'Exit time and Re-entry time are required for exit request'}), 400
        
        # Validate Re-entry is greater than exit natively in python
        if reentry_time <= exit_time:
            return jsonify({'error': 'Re-entry time must be strictly after the exit time!'}), 400
    else:
        return jsonify({'error': 'Invalid request type'}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Check for overlapping active requests
            overlap_check = """
            SELECT * FROM permission_request 
            WHERE student_id = %s AND request_type = %s AND status = 'pending'
            """
            cursor.execute(overlap_check, (current_user['user_id'], req_type))
            if cursor.fetchone():
                return jsonify({'error': f'You already have a pending {req_type} request'}), 400

            # Insert request (warden_id defaults to NULL)
            sql = """INSERT INTO permission_request 
                     (student_id, request_type, entry_date, entry_time, exit_time, reentry_time, reason, status)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending')"""
            cursor.execute(sql, (current_user['user_id'], req_type, entry_date, entry_time, exit_time, reentry_time, reason))
        connection.commit()
        return jsonify({'message': 'Request submitted successfully'}), 201
    except Exception as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

@student_bp.route('/requests', methods=['GET'])
@token_required(allowed_roles=['student'])
def get_requests(current_user):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM permission_request WHERE student_id = %s ORDER BY created_at DESC"
            cursor.execute(sql, (current_user['user_id'],))
            requests = cursor.fetchall()
            
            # Format times for JSON safety
            for req in requests:
                if req['entry_date']:
                    req['entry_date'] = str(req['entry_date'])
                if req['entry_time']:
                    req['entry_time'] = str(req['entry_time'])
                if req['exit_time']:
                    req['exit_time'] = str(req['exit_time'])
                if req['reentry_time']:
                    req['reentry_time'] = str(req['reentry_time'])
                req['created_at'] = req['created_at'].isoformat()
                
        return jsonify({'requests': requests}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

@student_bp.route('/profile', methods=['GET'])
@token_required(allowed_roles=['student'])
def get_profile(current_user):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM student WHERE student_id = %s", (current_user['user_id'],))
            student = cursor.fetchone()
        return jsonify({'profile': student}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()
