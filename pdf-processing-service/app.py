"""
PDF Processing Service (OMR)
Port: 5004
Processes scanned bubble sheets and extracts attendance data
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
from datetime import datetime
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from processors.omr_processor import OMRProcessor
from common.database import Database

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Initialize processor
omr_processor = OMRProcessor(
    bubble_service_url=os.getenv('BUBBLE_SERVICE_URL', 'http://localhost:5003')
)

# Database for processing history
db = Database('processing_history.db')
db.create_table("""
    CREATE TABLE IF NOT EXISTS processing_jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id TEXT UNIQUE NOT NULL,
        lecture_id TEXT,
        total_pages INTEGER,
        total_students INTEGER,
        present_count INTEGER,
        absent_count INTEGER,
        attendance_percentage REAL,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")


@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'service': 'PDF Processing (OMR)',
        'status': 'healthy',
        'port': os.getenv('PORT', 5004),
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@app.route('/health', methods=['GET'])
def health():
    """Health endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'pdf-processing-service'
    }), 200


@app.route('/api/process', methods=['POST'])
def process_scanned_sheet():
    """
    Process scanned bubble sheet PDF

    Form data:
        file: PDF file (scanned attendance sheet)
        send_to_attendance: boolean (optional, default: true)

    Returns:
    {
        "job_id": "JOB-xxx",
        "lecture_id": "LEC-xxx",
        "total_pages": 3,
        "total_students": 90,
        "present": 88,
        "absent": 2,
        "attendance_percentage": 97.78,
        "sent_to_attendance_service": true,
        "attendance_result": {...},
        "status": "success"
    }
    """
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                'error': 'No file provided',
                'status': 'error'
            }), 400

        # Circuit Breaker: Check state before processing
        from common.circuit_breaker import CircuitState

        if omr_processor.attendance_cb.state == CircuitState.OPEN:
            # Check if timeout expired (should attempt reset to HALF_OPEN)
            if not omr_processor.attendance_cb._should_attempt_reset():
                # Still in timeout - reject immediately
                return jsonify({
                    'error': '🚫 Circuit Breaker OPEN - Request Rejected',
                    'message': 'Cannot process PDF - Circuit Breaker is OPEN. Wait for timeout to expire.',
                    'circuit_breaker_state': omr_processor.attendance_cb.get_state(),
                    'pattern': 'Circuit Breaker (Fail Fast)',
                    'status': 'circuit_breaker_open'
                }), 503
            # else: timeout expired, allow request to proceed (CB will transition to HALF_OPEN during call)

        file = request.files['file']

        if file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'status': 'error'
            }), 400

        if not file.filename.endswith('.pdf'):
            return jsonify({
                'error': 'File must be a PDF',
                'status': 'error'
            }), 400

        # Save uploaded file
        import uuid
        job_id = f"JOB-{uuid.uuid4().hex[:12].upper()}"
        pdf_path = os.path.join(UPLOAD_FOLDER, f'{job_id}.pdf')
        file.save(pdf_path)

        # Create output folder for this job
        output_folder = os.path.join(PROCESSED_FOLDER, job_id)
        os.makedirs(output_folder, exist_ok=True)

        # Process PDF
        result = omr_processor.process_scanned_pdf(pdf_path, output_folder)

        # Save to database
        db.insert('processing_jobs', {
            'job_id': job_id,
            'lecture_id': result.get('lecture_id'),
            'total_pages': result.get('total_pages'),
            'total_students': result.get('total_students'),
            'present_count': result.get('present'),
            'absent_count': result.get('absent'),
            'attendance_percentage': result.get('attendance_percentage'),
            'status': result.get('status')
        })

        # Send to Attendance Service if requested
        send_to_attendance = request.form.get('send_to_attendance', 'true').lower() == 'true'
        attendance_result = None
        final_status = 'success'

        if send_to_attendance and result.get('attendance_records'):
            attendance_service_url = os.getenv(
                'ATTENDANCE_SERVICE_URL',
                'http://localhost:5005'
            )
            attendance_result = omr_processor.send_to_attendance_service(
                result['attendance_records'],
                attendance_service_url
            )

            # Check Circuit Breaker state directly
            if attendance_result:
                cb_state = attendance_result.get('circuit_breaker_state', {}).get('state', '')

                if cb_state == 'open':
                    final_status = 'circuit_breaker_open'
                elif cb_state == 'half_open':
                    final_status = 'circuit_breaker_testing'
                elif attendance_result.get('success', 0) < len(result.get('attendance_records', [])):
                    final_status = 'partial_success'

        # Return response
        return jsonify({
            'job_id': job_id,
            'lecture_id': result.get('lecture_id'),
            'total_pages': result.get('total_pages'),
            'total_students': result.get('total_students'),
            'present': result.get('present'),
            'absent': result.get('absent'),
            'attendance_percentage': result.get('attendance_percentage'),
            'sent_to_attendance_service': send_to_attendance,
            'attendance_result': attendance_result,
            'visualization_url': f'/api/visualization/{job_id}' if output_folder else None,
            'status': final_status
        }), 201

    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/api/visualization/<job_id>', methods=['GET'])
def get_visualization(job_id):
    """
    Get visualization images for a processing job

    Args:
        job_id: Job ID

    Returns:
        List of visualization image URLs
    """
    try:
        output_folder = os.path.join(PROCESSED_FOLDER, job_id)

        if not os.path.exists(output_folder):
            return jsonify({
                'error': 'Job not found',
                'status': 'error'
            }), 404

        # List all visualization images
        visualizations = []
        for filename in os.listdir(output_folder):
            if filename.endswith('_detected.png'):
                visualizations.append({
                    'filename': filename,
                    'url': f'/api/visualization/{job_id}/{filename}'
                })

        return jsonify({
            'job_id': job_id,
            'visualizations': visualizations,
            'total': len(visualizations),
            'status': 'success'
        }), 200

    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/api/visualization/<job_id>/<filename>', methods=['GET'])
def download_visualization(job_id, filename):
    """Download specific visualization image"""
    try:
        file_path = os.path.join(PROCESSED_FOLDER, job_id, filename)

        if not os.path.exists(file_path):
            return jsonify({
                'error': 'File not found',
                'status': 'error'
            }), 404

        return send_file(
            file_path,
            mimetype='image/png',
            as_attachment=False
        )

    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/api/jobs', methods=['GET'])
def list_processing_jobs():
    """
    List all processing jobs

    Returns:
    {
        "jobs": [...],
        "total": 10
    }
    """
    try:
        jobs = db.fetch_all(
            "SELECT * FROM processing_jobs ORDER BY created_at DESC LIMIT 50"
        )

        return jsonify({
            'jobs': jobs,
            'total': len(jobs),
            'status': 'success'
        }), 200

    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/api/jobs/<job_id>', methods=['GET'])
def get_job_details(job_id):
    """Get details of a specific processing job"""
    try:
        job = db.fetch_one(
            "SELECT * FROM processing_jobs WHERE job_id = ?",
            (job_id,)
        )

        if not job:
            return jsonify({
                'error': 'Job not found',
                'status': 'error'
            }), 404

        return jsonify({
            'job': job,
            'status': 'success'
        }), 200

    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get processing statistics"""
    try:
        total_jobs = db.fetch_one(
            "SELECT COUNT(*) as count FROM processing_jobs"
        )
        total_students_processed = db.fetch_one(
            "SELECT SUM(total_students) as total FROM processing_jobs"
        )
        avg_attendance = db.fetch_one(
            "SELECT AVG(attendance_percentage) as avg FROM processing_jobs"
        )

        return jsonify({
            'total_jobs': total_jobs['count'] if total_jobs else 0,
            'total_students_processed': total_students_processed['total'] if total_students_processed else 0,
            'average_attendance_percentage': round(avg_attendance['avg'], 2) if avg_attendance and avg_attendance['avg'] else 0,
            'status': 'success'
        }), 200

    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


# ====================================================================
# Circuit Breaker Demo Endpoints
# These endpoints let you test and observe the Circuit Breaker in action
# ====================================================================

@app.route('/api/pdf/cb-status', methods=['GET'])
def get_cb_status():
    """
    Get current Circuit Breaker state.
    Shows: state (CLOSED/OPEN/HALF_OPEN), failure count, time until retry
    """
    return jsonify({
        'circuit_breaker': omr_processor.attendance_cb.get_state(),
        'circuit_breaker_library': omr_processor.attendance_cb_library.get_state(),
        'description': {
            'closed': 'Normal - requests pass through to Attendance Service',
            'open': 'Failing - requests are rejected immediately (no HTTP call made)',
            'half_open': 'Testing - one request allowed through to test if service recovered'
        }
    }), 200


@app.route('/api/pdf/test-cb', methods=['POST'])
def test_circuit_breaker():
    """
    Test Circuit Breaker by sending a test record to Attendance Service.
    Use this to demonstrate CB state transitions:
    1. Service up: CB stays CLOSED
    2. Stop Attendance Service, send 3 requests: CB opens
    3. Requests rejected immediately while CB is OPEN
    4. Start Attendance Service, wait 15s: CB goes HALF_OPEN then CLOSED
    """
    import requests as http_requests

    attendance_url = os.getenv('ATTENDANCE_SERVICE_URL', 'http://localhost:5005')

    test_record = {
        'student_id': 'TEST-001',
        'course_id': 'TEST-COURSE',
        'date': '2024-01-01',
        'status': 'present'
    }

    try:
        def call_attendance():
            response = http_requests.post(
                f"{attendance_url}/api/attendance",
                json=test_record,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            if response.status_code not in [200, 201]:
                raise Exception(f"HTTP {response.status_code}")
            return response

        result = omr_processor.attendance_cb.call(call_attendance)

        return jsonify({
            'result': 'SUCCESS - Attendance Service responded',
            'circuit_breaker': omr_processor.attendance_cb.get_state()
        }), 200

    except Exception as e:
        return jsonify({
            'result': f'FAILED - {str(e)}',
            'circuit_breaker': omr_processor.attendance_cb.get_state()
        }), 503


@app.route('/api/pdf/test-library-cb', methods=['POST'])
def test_library_circuit_breaker():
    """
    Test Circuit Breaker using pybreaker LIBRARY (for comparison).
    Same behavior as manual CB, but using a proven library.
    """
    import requests as http_requests
    from common.circuit_breaker_library import LibraryCircuitBreaker

    if not hasattr(app, '_library_cb'):
        app._library_cb = LibraryCircuitBreaker(
            name="attendance-service-lib",
            failure_threshold=3,
            timeout=15
        )

    attendance_url = os.getenv('ATTENDANCE_SERVICE_URL', 'http://localhost:5005')

    test_record = {
        'student_id': 'TEST-LIB-001',
        'course_id': 'TEST-COURSE',
        'date': '2024-01-01',
        'status': 'present'
    }

    try:
        def call_attendance():
            response = http_requests.post(
                f"{attendance_url}/api/attendance",
                json=test_record,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            if response.status_code not in [200, 201]:
                raise Exception(f"HTTP {response.status_code}")
            return response

        result = app._library_cb.call(call_attendance)

        return jsonify({
            'result': 'SUCCESS - Attendance Service responded (Library CB)',
            'circuit_breaker': app._library_cb.get_state(),
            'comparison': 'Using pybreaker library - same concept, less code'
        }), 200

    except Exception as e:
        return jsonify({
            'result': f'FAILED - {str(e)}',
            'circuit_breaker': app._library_cb.get_state(),
            'comparison': 'Using pybreaker library - same concept, less code'
        }), 503


@app.route('/api/pdf/cb-reset', methods=['POST'])
def reset_circuit_breaker():
    """Manually reset the Circuit Breaker to CLOSED state"""
    omr_processor.attendance_cb.reset()
    return jsonify({
        'message': 'Circuit Breaker has been reset to CLOSED',
        'circuit_breaker': omr_processor.attendance_cb.get_state()
    }), 200


@app.route('/api/pdf/cb-logs', methods=['GET'])
def get_cb_logs():
    """
    Get accumulated Circuit Breaker logs.
    Returns all state transitions and events captured by both Manual and Library CBs.
    """
    # Combine logs from both CBs
    manual_logs = omr_processor.attendance_cb.get_logs()
    library_logs = omr_processor.attendance_cb_library.get_logs()

    # Merge and sort by timestamp
    all_logs = manual_logs + library_logs
    all_logs.sort(key=lambda x: x['timestamp'])

    return jsonify({
        'logs': all_logs,
        'circuit_breaker_state': omr_processor.attendance_cb.get_state(),
        'circuit_breaker_library_state': omr_processor.attendance_cb_library.get_state()
    }), 200


@app.route('/api/pdf/cb-logs', methods=['DELETE'])
def clear_cb_logs():
    """Clear Circuit Breaker logs for both Manual and Library CBs"""
    omr_processor.attendance_cb.clear_logs()
    omr_processor.attendance_cb_library.clear_logs()
    return jsonify({
        'message': 'Logs cleared successfully'
    }), 200


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5004))
    debug_mode = os.getenv('FLASK_ENV', 'development') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
