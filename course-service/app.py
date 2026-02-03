"""
Course Management Service
Port: 5002
Handles course operations and student enrollments

Choreography Pattern:
- This service is a CONSUMER of attendance_events from RabbitMQ
- When Attendance Service records attendance, it publishes an event
- This service reads the event and updates attendance statistics
- No central coordinator - each service acts independently
"""

from flask import Flask, jsonify
from flask_cors import CORS
import sys
import os
import json
import threading

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from common.database import Database
from models.course import CourseRepository
from routes.course_routes import create_routes

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize database
db = Database('courses.db')
course_repo = CourseRepository(db)

# Register routes
course_bp = create_routes(course_repo)
app.register_blueprint(course_bp)

# ====================================================================
# RabbitMQ Consumer (Choreography Pattern)
# Listens for attendance_recorded events from Attendance Service
# ====================================================================
rabbitmq = None
attendance_events_log = []  # Store received events for demo


def on_attendance_event(channel, method, properties, body):
    """
    Callback: called when an attendance event is received from RabbitMQ.
    This is the Choreography pattern - Course Service reacts independently
    to events published by Attendance Service.
    """
    try:
        event = json.loads(body)
        print(f"[RabbitMQ Consumer] Received event: {event}")

        # Store event for demo
        attendance_events_log.append(event)
        if len(attendance_events_log) > 50:
            attendance_events_log.pop(0)

        print(f"[RabbitMQ Consumer] Processed: student={event.get('student_id')}, course={event.get('course_id')}, status={event.get('status')}")

        # Acknowledge the message
        channel.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"[RabbitMQ Consumer] Error processing event: {e}")
        channel.basic_ack(delivery_tag=method.delivery_tag)


def start_rabbitmq_consumer():
    """Start RabbitMQ consumer in a background thread"""
    global rabbitmq
    try:
        from common.rabbitmq_client import RabbitMQClient
        rabbitmq = RabbitMQClient()
        rabbitmq.consume(on_attendance_event)
    except Exception as e:
        print(f"[RabbitMQ Consumer] Could not start: {e}")
        print("[RabbitMQ Consumer] Running without message queue")


# Start consumer in background thread (won't block Flask)
consumer_thread = threading.Thread(target=start_rabbitmq_consumer, daemon=True)
consumer_thread.start()


@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'service': 'Course Management Service',
        'status': 'healthy',
        'port': 5002,
        'version': '1.0.0',
        'rabbitmq_consumer': 'active' if rabbitmq and rabbitmq.is_connected() else 'inactive'
    }), 200


@app.route('/api/health')
def api_health():
    """API health check"""
    try:
        courses = course_repo.get_all_courses()
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'course_count': len(courses),
            'rabbitmq': 'connected' if rabbitmq and rabbitmq.is_connected() else 'disconnected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


@app.route('/api/courses/attendance-events', methods=['GET'])
def get_attendance_events():
    """
    View attendance events received from RabbitMQ (Choreography demo).
    Shows events that Attendance Service published and this service consumed.
    """
    return jsonify({
        'events': attendance_events_log,
        'total': len(attendance_events_log),
        'pattern': 'Choreography - events consumed independently via RabbitMQ'
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("=" * 50)
    print("Course Management Service")
    print("=" * 50)
    print("Port: 5002")
    print("Features: Course CRUD, Student Enrollments, RabbitMQ Consumer")
    print("=" * 50)

    app.run(host='0.0.0.0', port=5002, debug=True)
