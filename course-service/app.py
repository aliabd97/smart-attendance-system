"""
Course Management Service
Port: 5002
Handles course operations and student enrollments
"""

from flask import Flask, jsonify
from flask_cors import CORS
import sys
import os

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


@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'service': 'Course Management Service',
        'status': 'healthy',
        'port': 5002,
        'version': '1.0.0'
    }), 200


@app.route('/api/health')
def api_health():
    """API health check"""
    try:
        # Test database connection
        courses = course_repo.get_all_courses()
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'course_count': len(courses)
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


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
    print("📚 Course Management Service")
    print("=" * 50)
    print("Port: 5002")
    print("Features: Course CRUD, Student Enrollments")
    print("=" * 50)

    app.run(host='0.0.0.0', port=5002, debug=True)
