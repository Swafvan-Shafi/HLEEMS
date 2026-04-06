from flask import Blueprint, request, jsonify
from utils.db import get_db_connection
from utils.auth_middleware import token_required
from utils.email_service import send_late_warning_email
from datetime import datetime

warden_bp = Blueprint('warden', __name__)

@warden_bp.route('/requests', methods=['GET'])
@token_required(allowed_roles=['warden'])
def get_requests(current_user):
    # Dynamic Query Filters parsing
    req_type = request.args.get('type', 'all')
    search_id = request.args.get('search', '').strip()
    status_filter = request.args.get('status', 'pending') # Add status filter

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT block_id FROM warden WHERE warden_id = %s", (current_user['user_id'],))
            warden_data = cursor.fetchone()
            if not warden_data:
                return jsonify({'error': 'Warden details not found'}), 404
            
            block_id = warden_data['block_id']

            sql = """
            SELECT pr.*, s.name as student_name, s.room_number 
            FROM permission_request pr
            JOIN student s ON pr.student_id = s.student_id
            WHERE s.block_id = %s 
            """
            params = [block_id]

            if status_filter == 'resolved':
                sql += " AND pr.status IN ('approved', 'rejected')"
            else:
                sql += " AND pr.status = 'pending'"

            if req_type in ['exit', 'late_entry']:
                sql += " AND pr.request_type = %s"
                params.append(req_type)
            
            if search_id:
                sql += " AND pr.student_id LIKE %s"
                params.append(f"%{search_id}%")

            sql += " ORDER BY pr.created_at DESC"

            cursor.execute(sql, tuple(params))
            requests = cursor.fetchall()
            
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

@warden_bp.route('/requests/<int:request_id>', methods=['PUT'])
@token_required(allowed_roles=['warden'])
def update_request(current_user, request_id):
    data = request.get_json()
    status = data.get('status')
    if status not in ['approved', 'rejected']:
        return jsonify({'error': 'Invalid status'}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE permission_request SET status = %s, warden_id = %s WHERE request_id = %s"
            cursor.execute(sql, (status, current_user['user_id'], request_id))
        connection.commit()
        return jsonify({'message': f'Request {status} successfully'}), 200
    except Exception as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

@warden_bp.route('/students/<student_id>', methods=['GET'])
@token_required(allowed_roles=['warden'])
def view_single_student(current_user, student_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # We enforce that the Warden can only view students in their assigned Block
            cursor.execute("SELECT block_id FROM warden WHERE warden_id = %s", (current_user['user_id'],))
            warden_data = cursor.fetchone()

            sql = """
            SELECT student_id, name, email, phone, room_number, block_id
            FROM student
            WHERE student_id = %s AND block_id = %s
            """
            cursor.execute(sql, (student_id, warden_data['block_id']))
            student = cursor.fetchone()
            
            if not student:
                 return jsonify({'error': 'Student not found in your assigned block.'}), 404
            
        return jsonify({'student': student}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

@warden_bp.route('/logs/entry', methods=['POST'])
@token_required(allowed_roles=['warden'])
def record_entry(current_user):
    data = request.get_json()
    student_id = data.get('student_id')
    entry_time_str = data.get('entry_time') 
    
    if not student_id or not entry_time_str:
        return jsonify({'error': 'Missing student_id or entry_time'}), 400

    try:
        entry_time = datetime.fromisoformat(entry_time_str.replace('Z', '+00:00'))
    except ValueError:
        return jsonify({'error': 'Invalid datetime format. Need ISO format.'}), 400

    is_late = entry_time.hour >= 21

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO entry_record (student_id, entry_time, is_late, recorded_by) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (student_id, entry_time_str, is_late, current_user['user_id']))
            connection.commit()

            # Dynamic 5-Threshold Late Warning Evaluator
            cursor.execute("SELECT COUNT(record_id) as late_count FROM entry_record WHERE student_id = %s AND is_late = TRUE", (student_id,))
            res = cursor.fetchone()
            if res and res['late_count'] >= 5:
                cursor.execute("SELECT name, email, late_warning_sent FROM student WHERE student_id = %s", (student_id,))
                student = cursor.fetchone()
                if student and not student['late_warning_sent']:
                    # Initiate threshold email
                    success = send_late_warning_email(student['email'], student['name'], res['late_count'])
                    if success:
                        cursor.execute("UPDATE student SET late_warning_sent = TRUE WHERE student_id = %s", (student_id,))
                        connection.commit()

        return jsonify({'message': 'Entry recorded successfully', 'is_late': is_late}), 201
    except Exception as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

@warden_bp.route('/logs/exit', methods=['POST'])
@token_required(allowed_roles=['warden'])
def record_exit(current_user):
    data = request.get_json()
    student_id = data.get('student_id')
    exit_time_str = data.get('exit_time')
    
    if not student_id or not exit_time_str:
        return jsonify({'error': 'Missing student_id or exit_time'}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO exit_record (student_id, exit_time, recorded_by) VALUES (%s, %s, %s)"
            cursor.execute(sql, (student_id, exit_time_str, current_user['user_id']))
        connection.commit()
        return jsonify({'message': 'Exit recorded successfully'}), 201
    except Exception as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

@warden_bp.route('/students', methods=['GET'])
@token_required(allowed_roles=['warden'])
def get_students(current_user):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT block_id FROM warden WHERE warden_id = %s", (current_user['user_id'],))
            warden_data = cursor.fetchone()
            if not warden_data:
                 return jsonify({'error': 'Warden details not found'}), 404
            
            sql = """
            SELECT student_id, name, room_number, phone, email
            FROM student
            WHERE block_id = %s
            """
            cursor.execute(sql, (warden_data['block_id'],))
            students = cursor.fetchall()
        return jsonify({'students': students}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()
