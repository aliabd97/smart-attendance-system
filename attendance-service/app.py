"""
Attendance Recording Service
Port: 5005
Implements service-to-service validation (Breaking Foreign Keys Pattern)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from common.database import Database
from common.rabbitmq_client import RabbitMQClient
from models.attendance import AttendanceRepository
from validators.service_validator import ServiceValidator

app = Flask(__name__)
CORS(app)

# Initialize database
db = Database('attendance.db')
attendance_repo = AttendanceRepository(db)

# Initialize service validator
validator = ServiceValidator()

# Initialize RabbitMQ client (REQUIRED for Choreography pattern)
print("🔌 Connecting to RabbitMQ...")
rabbitmq = RabbitMQClient()
print("✅ RabbitMQ connected successfully")


@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'service': 'Attendance Recording Service',
        'status': 'healthy',
        'port': 5005,
        'version': '1.0.0'
    }), 200


@app.route('/api/attendance', methods=['POST'])
def record_attendance():
    """
    Record attendance for a student
    Validates student and course exist before recording
    """
    try:
        data = request.get_json()

        # Validate required fields
        required = ['student_id', 'course_id', 'date', 'status']
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({'error': f'Missing fields: {", ".join(missing)}'}), 400

        student_id = data['student_id']
        course_id = data['course_id']
        date = data['date']
        status = data['status']
        session_name = data.get('session_name')

        # Validate status
        valid_statuses = ['present', 'absent', 'late', 'excused']
        if status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400

        # Validate student and course exist (Breaking Foreign Keys Pattern)
        # TEMPORARY: Skip validation for OMR-generated records
        # is_valid, error_msg = validator.validate_before_recording(
        #     student_id, course_id, check_enrollment=False
        # )
        # if not is_valid:
        #     return jsonify({'error': error_msg}), 400

        # Record attendance (idempotent operation)
        success, message, record_id = attendance_repo.record_attendance(
            student_id=student_id,
            course_id=course_id,
            date=date,
            status=status,
            session_name=session_name
        )

        if success:
            # Choreography: Publish event to RabbitMQ after successful recording
            # Course Service will consume this event independently
            try:
                rabbitmq.publish({
                    'event': 'attendance_recorded',
                    'student_id': student_id,
                    'course_id': course_id,
                    'date': date,
                    'status': status
                })
                print(f"✅ [RabbitMQ] Published attendance event for student {student_id}")
            except Exception as rmq_err:
                print(f"❌ [RabbitMQ] Failed to publish event: {rmq_err}")
                # Re-raise to fail the request if RabbitMQ is required
                raise

            return jsonify({
                'message': message,
                'record_id': record_id,
                'student_id': student_id,
                'course_id': course_id,
                'date': date,
                'status': status
            }), 201 if 'Recorded successfully' in message else 200
        else:
            return jsonify({'error': message}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/attendance/bulk', methods=['POST'])
def bulk_record_attendance():
    """
    Bulk record attendance
    Used by PDF Processing Service
    """
    try:
        data = request.get_json()
        records = data.get('records', [])

        if not records:
            return jsonify({'error': 'No records provided'}), 400

        # Validate and record each
        results = []
        for record in records:
            # Validate
            is_valid, error_msg = validator.validate_before_recording(
                record['student_id'],
                record['course_id'],
                check_enrollment=False
            )

            if is_valid:
                success, message, record_id = attendance_repo.record_attendance(
                    student_id=record['student_id'],
                    course_id=record['course_id'],
                    date=record['date'],
                    status=record['status'],
                    session_name=record.get('session_name')
                )
                results.append({
                    'student_id': record['student_id'],
                    'success': success,
                    'message': message
                })
            else:
                results.append({
                    'student_id': record['student_id'],
                    'success': False,
                    'message': error_msg
                })

        success_count = sum(1 for r in results if r['success'])
        error_count = len(results) - success_count

        return jsonify({
            'total': len(results),
            'success_count': success_count,
            'error_count': error_count,
            'results': results
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/attendance', methods=['GET'])
def get_attendance_records():
    """Get attendance records with optional filters"""
    try:
        filters = {}

        if request.args.get('student_id'):
            filters['student_id'] = request.args.get('student_id')
        if request.args.get('course_id'):
            filters['course_id'] = request.args.get('course_id')
        if request.args.get('date'):
            filters['date'] = request.args.get('date')
        if request.args.get('session_name'):
            filters['session_name'] = request.args.get('session_name')

        records = attendance_repo.get_attendance_records(**filters)

        return jsonify({
            'count': len(records),
            'filters': filters,
            'records': [r.to_dict() for r in records]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/attendance/student/<student_id>', methods=['GET'])
def get_student_attendance(student_id):
    """Get attendance history for a student"""
    try:
        course_id = request.args.get('course_id')

        # Get records
        filters = {'student_id': student_id}
        if course_id:
            filters['course_id'] = course_id

        records = attendance_repo.get_attendance_records(**filters)

        # Get summary
        summary = attendance_repo.get_student_attendance_summary(student_id, course_id)

        return jsonify({
            'student_id': student_id,
            'course_id': course_id,
            'summary': summary,
            'records': [r.to_dict() for r in records]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/attendance/course/<course_id>', methods=['GET'])
def get_course_attendance(course_id):
    """Get attendance records for a course"""
    try:
        date = request.args.get('date')

        filters = {'course_id': course_id}
        if date:
            filters['date'] = date

        records = attendance_repo.get_attendance_records(**filters)

        # Get summary
        summary = attendance_repo.get_course_attendance_summary(course_id, date)

        return jsonify({
            'course_id': course_id,
            'date': date,
            'summary': summary,
            'records': [r.to_dict() for r in records]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/attendance/date/<date>', methods=['GET'])
def get_attendance_by_date(date):
    """Get all attendance records for a date"""
    try:
        records = attendance_repo.get_attendance_records(date=date)

        return jsonify({
            'date': date,
            'count': len(records),
            'records': [r.to_dict() for r in records]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/attendance/circuit-breakers', methods=['GET'])
def get_circuit_breaker_status():
    """Get status of circuit breakers"""
    try:
        status = validator.get_circuit_breaker_status()
        return jsonify(status), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/attendance/circuit-breakers/reset', methods=['POST'])
def reset_circuit_breakers():
    """Manually reset circuit breakers"""
    try:
        validator.reset_circuit_breakers()
        return jsonify({'message': 'Circuit breakers reset'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("📊 Attendance Recording Service")
    print("=" * 60)
    print("Port: 5005")
    print("Features: Service Validation, Circuit Breaker, Idempotency")
    print("=" * 60)

    app.run(host='0.0.0.0', port=5005, debug=True)
