"""
Authentication Service
Port: 5007
Implements JWT-based authentication
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import datetime
from functools import wraps
import sys
import os
import hashlib

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from common.database import Database

app = Flask(__name__)
CORS(app)

# JWT Secret Key (In production: use environment variable)
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'smart-attendance-system-jwt-secret-key-2024-x7k9m2')

# Initialize database for user management
db = Database('auth.db')

# Create users table
users_schema = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    email TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
db.create_table(users_schema)


def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def init_default_users():
    """Initialize default admin and teacher users"""
    default_users = [
        {
            'username': 'admin',
            'password': 'admin123',  # Change in production
            'role': 'admin',
            'email': 'admin@university.edu'
        },
        {
            'username': 'teacher',
            'password': 'teacher123',  # Change in production
            'role': 'teacher',
            'email': 'teacher@university.edu'
        }
    ]

    for user_data in default_users:
        # Check if user already exists
        existing = db.fetch_one(
            "SELECT * FROM users WHERE username = ?",
            (user_data['username'],)
        )

        if not existing:
            db.insert('users', {
                'username': user_data['username'],
                'password_hash': hash_password(user_data['password']),
                'role': user_data['role'],
                'email': user_data['email']
            })
            print(f"✅ Created default user: {user_data['username']}")


# Initialize default users on startup
init_default_users()


def require_auth(f):
    """Decorator to protect endpoints with JWT authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'error': 'Token required'}), 401

        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]

            # Decode and validate token
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user = payload

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)

    return decorated


@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'service': 'Authentication Service',
        'status': 'healthy',
        'port': 5007,
        'version': '1.0.0'
    }), 200


@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Login endpoint - returns JWT token

    Request:
    {
        "username": "admin",
        "password": "admin123"
    }

    Response:
    {
        "token": "eyJhbGc...",
        "username": "admin",
        "role": "admin",
        "expires_in": 86400
    }
    """
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400

        # Find user in database
        user = db.fetch_one(
            "SELECT * FROM users WHERE username = ? AND is_active = 1",
            (username,)
        )

        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401

        # Verify password
        password_hash = hash_password(password)
        if user['password_hash'] != password_hash:
            return jsonify({'error': 'Invalid credentials'}), 401

        # Generate JWT token
        expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        token = jwt.encode({
            'user_id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'exp': expiration
        }, SECRET_KEY, algorithm='HS256')

        # Decode token if it's bytes (for older PyJWT versions)
        if isinstance(token, bytes):
            token = token.decode('utf-8')

        return jsonify({
            'token': token,
            'username': user['username'],
            'role': user['role'],
            'email': user['email'],
            'expires_in': 86400  # 24 hours in seconds
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/validate', methods=['POST'])
def validate_token():
    """
    Validate JWT token

    Headers:
    Authorization: Bearer <token>

    Response:
    {
        "valid": true,
        "user": {...}
    }
    """
    try:
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'valid': False, 'error': 'Token required'}), 401

        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]

        # Decode and validate token
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

        return jsonify({
            'valid': True,
            'user': {
                'user_id': payload.get('user_id'),
                'username': payload.get('username'),
                'role': payload.get('role')
            }
        }), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'valid': False, 'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'valid': False, 'error': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)}), 500


@app.route('/api/auth/refresh', methods=['POST'])
@require_auth
def refresh_token():
    """
    Refresh JWT token

    Headers:
    Authorization: Bearer <old_token>

    Response:
    {
        "token": "new_token..."
    }
    """
    try:
        user = request.user

        # Generate new token
        expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        token = jwt.encode({
            'user_id': user.get('user_id'),
            'username': user.get('username'),
            'role': user.get('role'),
            'exp': expiration
        }, SECRET_KEY, algorithm='HS256')

        return jsonify({
            'token': token,
            'expires_in': 86400
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/register', methods=['POST'])
def register():
    """
    Register new user (admin only in production)

    Request:
    {
        "username": "newuser",
        "password": "password123",
        "role": "teacher",
        "email": "user@university.edu"
    }
    """
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('username') or not data.get('password') or not data.get('role'):
            return jsonify({'error': 'Username, password, and role required'}), 400

        # Check if username already exists
        existing = db.fetch_one(
            "SELECT * FROM users WHERE username = ?",
            (data['username'],)
        )

        if existing:
            return jsonify({'error': 'Username already exists'}), 409

        # Validate role
        valid_roles = ['admin', 'teacher', 'student']
        if data['role'] not in valid_roles:
            return jsonify({'error': f'Invalid role. Must be one of: {valid_roles}'}), 400

        # Create user
        user_data = {
            'username': data['username'],
            'password_hash': hash_password(data['password']),
            'role': data['role'],
            'email': data.get('email'),
            'is_active': True
        }

        user_id = db.insert('users', user_data)

        return jsonify({
            'message': 'User registered successfully',
            'user_id': user_id,
            'username': data['username']
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/users', methods=['GET'])
@require_auth
def get_users():
    """Get all users (admin only)"""
    try:
        # Check if user is admin
        if request.user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        users = db.fetch_all("SELECT id, username, role, email, is_active, created_at FROM users")

        return jsonify({
            'count': len(users),
            'users': users
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/me', methods=['GET'])
@require_auth
def get_current_user():
    """Get current authenticated user info"""
    try:
        user_id = request.user.get('user_id')
        user = db.fetch_one(
            "SELECT id, username, role, email, is_active FROM users WHERE id = ?",
            (user_id,)
        )

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify(user), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
    print("🔐 Authentication Service")
    print("=" * 50)
    print("Port: 5007")
    print("Features: JWT Authentication")
    print("\nDefault Users:")
    print("  Username: admin    | Password: admin123")
    print("  Username: teacher  | Password: teacher123")
    print("=" * 50)

    app.run(host='0.0.0.0', port=5007, debug=True)
