"""
API Gateway
Port: 5000
Central entry point for all microservices with JWT authentication
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import jwt
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = Flask(__name__)
CORS(app)

# JWT Secret Key (must match auth-service)
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production-2024')

# Service registry - maps service names to URLs
SERVICES = {
    'students': os.getenv('STUDENT_SERVICE_URL', 'http://localhost:5001'),
    'courses': os.getenv('COURSE_SERVICE_URL', 'http://localhost:5002'),
    'bubble-sheet': os.getenv('BUBBLE_SERVICE_URL', 'http://localhost:5003'),
    'pdf-processing': os.getenv('PDF_SERVICE_URL', 'http://localhost:5004'),
    'attendance': os.getenv('ATTENDANCE_SERVICE_URL', 'http://localhost:5005'),
    'reporting': os.getenv('REPORTING_SERVICE_URL', 'http://localhost:5009'),
    'auth': os.getenv('AUTH_SERVICE_URL', 'http://localhost:5007'),
}


def validate_token():
    """
    Validate JWT token from request headers

    Returns:
        Tuple of (user_payload, error_response, status_code)
    """
    token = request.headers.get('Authorization')

    if not token:
        return None, {'error': 'Token required'}, 401

    try:
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]

        # Decode and validate token
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload, None, None

    except jwt.ExpiredSignatureError:
        return None, {'error': 'Token expired'}, 401
    except jwt.InvalidTokenError:
        return None, {'error': 'Invalid token'}, 401
    except Exception as e:
        return None, {'error': str(e)}, 401


@app.route('/')
def index():
    """API Gateway Root - Use Next.js Dashboard at http://localhost:3000"""
    return jsonify({
        'service': 'API Gateway',
        'status': 'healthy',
        'message': 'Welcome to Smart Attendance System API',
        'frontend': 'http://localhost:3000',
        'docs': '/api/services',
        'health': '/health'
    }), 200


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'service': 'API Gateway',
        'status': 'healthy',
        'port': 5000,
        'version': '1.0.0',
        'available_services': list(SERVICES.keys())
    }), 200


@app.route('/api/health')
def api_health():
    """Check health of all services"""
    health_status = {}

    for service_name, service_url in SERVICES.items():
        try:
            response = requests.get(f"{service_url}/", timeout=3)
            health_status[service_name] = {
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'url': service_url,
                'response_code': response.status_code
            }
        except Exception as e:
            health_status[service_name] = {
                'status': 'unreachable',
                'url': service_url,
                'error': str(e)
            }

    all_healthy = all(s['status'] == 'healthy' for s in health_status.values())

    return jsonify({
        'gateway_status': 'healthy',
        'services': health_status,
        'all_services_healthy': all_healthy
    }), 200 if all_healthy else 503


# Auth routes - no token required for login
@app.route('/api/auth/<path:path>', methods=['GET', 'POST'])
def auth_route(path):
    """
    Forward authentication requests (no token required)
    """
    url = f"{SERVICES['auth']}/api/auth/{path}"

    try:
        if request.method == 'GET':
            response = requests.get(url, params=request.args, timeout=5)
        else:
            response = requests.post(url, json=request.get_json(), timeout=5)

        return jsonify(response.json()), response.status_code

    except requests.exceptions.Timeout:
        return jsonify({'error': 'Auth service timeout'}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Auth service unavailable'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Protected routes - require authentication

# Route for /api/<service>/<path>
@app.route('/api/<service>/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def gateway_route(service, path):
    """
    Main gateway - validates token then forwards request to appropriate service

    Args:
        service: Service name (students, courses, etc.)
        path: API path within the service
    """
    # Validate token
    user, error, status = validate_token()
    if error:
        return jsonify(error), status

    # Check if service exists
    if service not in SERVICES:
        return jsonify({
            'error': 'Service not found',
            'available_services': list(SERVICES.keys())
        }), 404

    # Build target URL - forward to service's /api/<path>
    url = f"{SERVICES[service]}/api/{path}"

    # Add user info to headers (so services know who is making the request)
    headers = {
        'X-User-ID': str(user.get('user_id', '')),
        'X-Username': user.get('username', ''),
        'X-Role': user.get('role', ''),
        'Content-Type': 'application/json'
    }

    try:
        # Forward request to service
        if request.method == 'GET':
            response = requests.get(
                url,
                headers=headers,
                params=request.args,
                timeout=30
            )
        elif request.method == 'POST':
            # Handle file uploads
            if request.files:
                files = {}
                for key, file in request.files.items():
                    files[key] = (file.filename, file.stream, file.content_type)
                response = requests.post(
                    url,
                    headers={k: v for k, v in headers.items() if k != 'Content-Type'},
                    files=files,
                    data=request.form,
                    timeout=30
                )
            else:
                response = requests.post(
                    url,
                    headers=headers,
                    json=request.get_json(),
                    timeout=30
                )
        elif request.method == 'PUT':
            response = requests.put(
                url,
                headers=headers,
                json=request.get_json(),
                timeout=30
            )
        elif request.method == 'DELETE':
            response = requests.delete(
                url,
                headers=headers,
                timeout=30
            )

        # Return response from service
        try:
            return jsonify(response.json()), response.status_code
        except:
            # If response is not JSON, return as text
            return response.text, response.status_code

    except requests.exceptions.Timeout:
        return jsonify({
            'error': f'{service} service timeout',
            'service': service,
            'url': url
        }), 504
    except requests.exceptions.ConnectionError:
        return jsonify({
            'error': f'{service} service unavailable',
            'service': service,
            'url': url
        }), 503
    except Exception as e:
        return jsonify({
            'error': f'Gateway error: {str(e)}',
            'service': service
        }), 500


@app.route('/api/services', methods=['GET'])
def list_services():
    """List all available services"""
    return jsonify({
        'services': SERVICES,
        'count': len(SERVICES)
    }), 200


# Enrollments endpoint - Get all enrollments
@app.route('/api/enrollments', methods=['GET'])
def get_all_enrollments():
    """Get all enrollments by fetching from courses service"""
    token = request.headers.get('Authorization')

    try:
        # Get all courses and their students
        courses_response = requests.get(
            f"{SERVICES['courses']}/api/courses",
            headers={'Authorization': token},
            timeout=10
        )

        if courses_response.status_code != 200:
            return jsonify({'error': 'Failed to fetch courses'}), courses_response.status_code

        courses_data = courses_response.json()
        courses = courses_data.get('courses', courses_data)

        enrollments = []

        # For each course, get enrolled students
        for course in courses:
            course_id = course.get('id')
            if not course_id:
                continue

            students_response = requests.get(
                f"{SERVICES['courses']}/api/courses/{course_id}/students",
                headers={'Authorization': token},
                timeout=10
            )

            if students_response.status_code == 200:
                students_data = students_response.json()
                # Get enrollments from response
                course_enrollments = students_data.get('enrollments', [])

                for enrollment in course_enrollments:
                    enrollments.append({
                        'student_id': enrollment.get('student_id'),
                        'student_name': 'N/A',  # Will fetch student name separately if needed
                        'course_id': course_id,
                        'course_name': course.get('name'),
                        'enrolled_at': enrollment.get('enrollment_date')
                    })

        return jsonify(enrollments), 200

    except Exception as e:
        print(f"❌ Error fetching enrollments: {str(e)}")
        return jsonify({'error': str(e)}), 500


# Enroll student endpoint - Proxy to course service
@app.route('/api/courses/<course_id>/enroll', methods=['POST'])
def enroll_student(course_id):
    """Enroll a student in a course"""
    # Validate token
    user, error, status = validate_token()
    if error:
        return jsonify(error), status

    try:
        token = request.headers.get('Authorization')
        data = request.get_json()

        response = requests.post(
            f"{SERVICES['courses']}/api/courses/{course_id}/enroll",
            headers={'Authorization': token},
            json=data,
            timeout=10
        )

        return jsonify(response.json()), response.status_code

    except Exception as e:
        print(f"❌ Error enrolling student: {str(e)}")
        return jsonify({'error': str(e)}), 500


# Unenroll student endpoint - Proxy to course service
@app.route('/api/courses/<course_id>/unenroll', methods=['POST'])
def unenroll_student(course_id):
    """Unenroll a student from a course"""
    # Validate token
    user, error, status = validate_token()
    if error:
        return jsonify(error), status

    try:
        token = request.headers.get('Authorization')
        data = request.get_json()

        response = requests.post(
            f"{SERVICES['courses']}/api/courses/{course_id}/unenroll",
            headers={'Authorization': token},
            json=data,
            timeout=10
        )

        return jsonify(response.json()), response.status_code

    except Exception as e:
        print(f"❌ Error unenrolling student: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/architecture/status', methods=['GET'])
def architecture_status():
    """
    Architecture Status - Shows all Software Architecture concepts in this project.
    Useful for demo: shows service health, Circuit Breaker state, and RabbitMQ status.
    """
    # Check each service health
    services_status = {}
    for name, url in SERVICES.items():
        try:
            response = requests.get(f"{url}/", timeout=3)
            services_status[name] = 'healthy' if response.status_code == 200 else 'unhealthy'
        except:
            services_status[name] = 'unreachable'

    # Get Circuit Breaker status from PDF Processing Service
    cb_status = None
    try:
        cb_response = requests.get(f"{SERVICES['pdf-processing']}/api/pdf/cb-status", timeout=3)
        if cb_response.status_code == 200:
            cb_status = cb_response.json()
    except:
        cb_status = {'error': 'PDF Processing Service unreachable'}

    # Get RabbitMQ events from Course Service
    rabbitmq_status = None
    try:
        rmq_response = requests.get(f"{SERVICES['courses']}/api/courses/attendance-events", timeout=3)
        if rmq_response.status_code == 200:
            rmq_data = rmq_response.json()
            rabbitmq_status = {
                'events_received': rmq_data.get('total', 0),
                'pattern': rmq_data.get('pattern')
            }
    except:
        rabbitmq_status = {'error': 'Course Service unreachable'}

    return jsonify({
        'architecture_patterns': {
            'microservices': f'{len(SERVICES)} independent services',
            'api_gateway': 'This service (port 5000) - single entry point',
            'database_per_service': 'Each service has its own SQLite database',
            'health_check': 'Every service exposes /health endpoint',
            'authentication': 'JWT tokens via Auth Service',
            'circuit_breaker_manual': 'State Pattern (CLOSED/OPEN/HALF_OPEN) in PDF Processing',
            'circuit_breaker_library': 'pybreaker library (same concept, less code)',
            'message_broker': 'RabbitMQ for async event communication',
            'choreography': 'Attendance -> RabbitMQ -> Course (no central coordinator)'
        },
        'services': services_status,
        'circuit_breaker': cb_status,
        'rabbitmq': rabbitmq_status
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'tip': 'Use /api/<service>/<path> format'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("🌐 API Gateway - Central Entry Point")
    print("=" * 60)

    # Get port from environment variable (for Render.com compatibility)
    port = int(os.getenv('PORT', 5000))
    print(f"Port: {port}")
    print("Features: JWT Authentication, Request Routing")
    print("\nAvailable Services:")
    for name, url in SERVICES.items():
        print(f"  - {name:20} → {url}")
    print("=" * 60)
    print("\nEndpoint Format: /api/<service>/<path>")
    print("Example: /api/students/students")
    print("=" * 60)

    # Use production settings when deployed
    debug_mode = os.getenv('FLASK_ENV', 'development') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
