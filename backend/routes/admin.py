from flask import Blueprint, request, jsonify
from utils.db import get_db_connection
from utils.auth_middleware import token_required
import bcrypt

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['GET'])
@token_required(allowed_roles=['admin'])
def get_users(current_user):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT u.id, u.role, u.created_at, 
            COALESCE(s.name, w.name, 'Admin') as name,
            COALESCE(s.email, w.email, 'N/A') as email
            FROM users u
            LEFT JOIN student s ON u.id = s.student_id
            LEFT JOIN warden w ON u.id = w.warden_id
            """)
            users = cursor.fetchall()
        return jsonify({'users': users}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

@admin_bp.route('/users/<user_id>', methods=['GET'])
@token_required(allowed_roles=['admin'])
def get_user_profile(current_user, user_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT role, created_at FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            profile = {'id': user_id, 'role': user['role'], 'created_at': user['created_at']}
            
            if user['role'] == 'student':
                cursor.execute("SELECT name, email, phone, room_number, block_id FROM student WHERE student_id = %s", (user_id,))
                profile.update(cursor.fetchone() or {})
            elif user['role'] == 'warden':
                cursor.execute("SELECT name, email, phone, block_id FROM warden WHERE warden_id = %s", (user_id,))
                profile.update(cursor.fetchone() or {})
                
        return jsonify({'user': profile}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

@admin_bp.route('/users/<user_id>', methods=['PUT'])
@token_required(allowed_roles=['admin'])
def update_user_profile(current_user, user_id):
    data = request.get_json()
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT role FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if user['role'] == 'student':
                cursor.execute("""
                    UPDATE student 
                    SET name=%s, email=%s, phone=%s, room_number=%s, block_id=%s 
                    WHERE student_id=%s
                """, (data.get('name'), data.get('email'), data.get('phone'), data.get('room_number'), data.get('block_id'), user_id))
            elif user['role'] == 'warden':
                cursor.execute("""
                    UPDATE warden 
                    SET name=%s, email=%s, phone=%s, block_id=%s 
                    WHERE warden_id=%s
                """, (data.get('name'), data.get('email'), data.get('phone'), data.get('block_id'), user_id))
            
        connection.commit()
        return jsonify({'message': 'Profile updated successfully'}), 200
    except Exception as e:
        connection.rollback()
        if "Duplicate entry" in str(e) and "email" in str(e):
            return jsonify({'error': 'Email address is already in use by another user.'}), 400
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

@admin_bp.route('/users/student', methods=['POST'])
@token_required(allowed_roles=['admin'])
def create_student(current_user):
    data = request.get_json()
    student_id = data.get('user_id')
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    room_number = data.get('room_number')
    phone = data.get('phone', '')
    block_id = data.get('block_id')

    if not all([student_id, name, email, password, room_number, block_id]):
        return jsonify({'error': 'Missing required fields for student'}), 400

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE id = %s", (student_id,))
            if cursor.fetchone():
                return jsonify({'error': 'StudentID already exists'}), 400
            
            cursor.execute("INSERT INTO users (id, password_hash, role) VALUES (%s, %s, 'student')", (student_id, hashed))
            cursor.execute("INSERT INTO student (student_id, name, email, room_number, phone, block_id) VALUES (%s, %s, %s, %s, %s, %s)",
                           (student_id, name, email, room_number, phone, block_id))
        connection.commit()
        return jsonify({'message': 'Student created successfully'}), 201
    except Exception as e:
        connection.rollback()
        if "Duplicate entry" in str(e) and "email" in str(e):
            return jsonify({'error': 'Email address is already in use.'}), 400
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

@admin_bp.route('/users/warden', methods=['POST'])
@token_required(allowed_roles=['admin'])
def create_warden(current_user):
    data = request.get_json()
    warden_id = data.get('user_id')
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone', '')
    block_id = data.get('block_id')

    if not all([warden_id, name, email, password]):
        return jsonify({'error': 'Missing required fields for warden'}), 400

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE id = %s", (warden_id,))
            if cursor.fetchone():
                return jsonify({'error': 'WardenID already exists'}), 400

            cursor.execute("INSERT INTO users (id, password_hash, role) VALUES (%s, %s, 'warden')", (warden_id, hashed))
            cursor.execute("INSERT INTO warden (warden_id, name, email, phone, block_id) VALUES (%s, %s, %s, %s, %s)",
                           (warden_id, name, email, phone, block_id))
        connection.commit()
        return jsonify({'message': 'Warden created successfully'}), 201
    except Exception as e:
        connection.rollback()
        if "Duplicate entry" in str(e) and "email" in str(e):
            return jsonify({'error': 'Email address is already in use.'}), 400
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

@admin_bp.route('/users/admin', methods=['POST'])
@token_required(allowed_roles=['admin'])
def create_admin(current_user):
    data = request.get_json()
    admin_id = data.get('user_id')
    password = data.get('password')

    if not all([admin_id, password]):
        return jsonify({'error': 'Missing required fields for admin'}), 400

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE id = %s", (admin_id,))
            if cursor.fetchone():
                return jsonify({'error': 'AdminID already exists'}), 400

            cursor.execute("INSERT INTO users (id, password_hash, role) VALUES (%s, %s, 'admin')", (admin_id, hashed))
        connection.commit()
        return jsonify({'message': 'Admin created successfully'}), 201
    except Exception as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

@admin_bp.route('/users/<user_id>', methods=['DELETE'])
@token_required(allowed_roles=['admin'])
def delete_user(current_user, user_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        connection.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

@admin_bp.route('/blocks', methods=['GET'])
@token_required(allowed_roles=['admin'])
def get_blocks(current_user):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM hostel_block")
            blocks = cursor.fetchall()
        return jsonify({'blocks': blocks}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()
