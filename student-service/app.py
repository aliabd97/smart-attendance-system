"""
Student Management Service
Port: 5001
Implements Excel Adapter Pattern for importing legacy student data
"""

from flask import Flask, jsonify
from flask_cors import CORS
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from common.database import Database
from models.student import StudentRepository
from routes.student_routes import create_routes

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize database
db = Database('students.db')
student_repo = StudentRepository(db)

# Register routes
student_bp = create_routes(student_repo)
app.register_blueprint(student_bp)


@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'service': 'Student Management Service',
        'status': 'healthy',
        'port': 5001,
        'version': '1.0.0'
    }), 200


@app.route('/api/health')
def api_health():
    """API health check"""
    try:
        # Test database connection
        students = student_repo.get_all_students()
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'student_count': len(students)
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
    print("🎓 Student Management Service")
    print("=" * 50)
    print("Port: 5001")
    print("Features: Excel Adapter Pattern")
    print("=" * 50)

    app.run(host='0.0.0.0', port=5001, debug=True)
