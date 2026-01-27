"""
Bubble Sheet Generator Service
Port: 5003
Generates PDF attendance sheets with QR codes and bubble marks
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
import uuid
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from common.database import Database
from generators.pdf_generator import BubbleSheetPDFGenerator
from generators.qr_generator import QRCodeGenerator
from generators.barcode_generator import BarcodeGenerator
import sqlite3

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'generated_sheets'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize generators
pdf_generator = BubbleSheetPDFGenerator()
qr_generator = QRCodeGenerator()
barcode_generator = BarcodeGenerator()

# Initialize barcode mapping database
BARCODE_DB = 'barcode_mapping.db'

def init_barcode_mapping_db():
    """Create barcode mapping table"""
    conn = sqlite3.connect(BARCODE_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS barcode_mapping (
            lecture_id TEXT PRIMARY KEY,
            barcode_hash TEXT NOT NULL,
            course_id TEXT,
            date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_barcode_mapping_db()


@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'service': 'Bubble Sheet Generator',
        'status': 'healthy',
        'port': os.getenv('PORT', 5003),
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@app.route('/health', methods=['GET'])
def health():
    """Health endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'bubble-sheet-generator'
    }), 200


@app.route('/api/generate', methods=['POST'])
def generate_bubble_sheet():
    """
    Generate bubble sheet PDF

    Request body:
    {
        "course_id": "CS101",
        "course_name": "Database Systems",
        "department": "Second Year",
        "date": "2024-12-15",
        "lecture_number": "5",
        "students": [
            {"id": "20240001", "name": "Ahmed Ali"},
            {"id": "20240002", "name": "Fatima Hassan"},
            ...
        ]
    }

    Returns:
    {
        "lecture_id": "LEC-xxx",
        "pdf_url": "/api/download/LEC-xxx",
        "total_pages": 3,
        "total_students": 90,
        "status": "success"
    }
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['course_id', 'course_name', 'date', 'students']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}',
                    'status': 'error'
                }), 400

        # Generate unique lecture ID
        lecture_id = f"LEC-{uuid.uuid4().hex[:12].upper()}"

        # Prepare course info
        course_info = {
            'course_id': data['course_id'],
            'course_name': data['course_name'],
            'department': data.get('department', ''),
            'date': data['date'],
            'lecture_number': data.get('lecture_number', '1')
        }

        # Get students
        students = data['students']

        if len(students) == 0:
            return jsonify({
                'error': 'No students provided',
                'status': 'error'
            }), 400

        # Generate PDF
        output_path = os.path.join(UPLOAD_FOLDER, f'{lecture_id}.pdf')
        result = pdf_generator.generate_bubble_sheet(
            lecture_id=lecture_id,
            course_info=course_info,
            students=students,
            output_path=output_path
        )

        # Save barcode mapping to database with course_id and date
        barcode_hash = barcode_generator.generate_barcode_data(lecture_id, 1, result['total_pages'])[:8]
        conn = sqlite3.connect(BARCODE_DB)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO barcode_mapping (lecture_id, barcode_hash, course_id, date)
            VALUES (?, ?, ?, ?)
        ''', (lecture_id, barcode_hash, course_info.get('course_id'), data.get('date')))
        conn.commit()
        conn.close()

        # Return success response
        return jsonify({
            'lecture_id': lecture_id,
            'pdf_url': f'/api/download/{lecture_id}',
            'total_pages': result['total_pages'],
            'total_students': result['total_students'],
            'status': 'success',
            'message': 'Bubble sheet generated successfully'
        }), 201

    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/api/download/<lecture_id>', methods=['GET'])
def download_bubble_sheet(lecture_id):
    """
    Download generated bubble sheet PDF

    Args:
        lecture_id: Lecture ID

    Returns:
        PDF file
    """
    try:
        pdf_path = os.path.join(UPLOAD_FOLDER, f'{lecture_id}.pdf')

        if not os.path.exists(pdf_path):
            return jsonify({
                'error': 'Bubble sheet not found',
                'status': 'error'
            }), 404

        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'attendance_sheet_{lecture_id}.pdf'
        )

    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/api/qrcode', methods=['POST'])
def generate_qr_code():
    """
    Generate standalone QR code

    Request body:
    {
        "lecture_id": "LEC-xxx",
        "course_id": "CS101",
        "date": "2024-12-15",
        "page_number": 1,
        "total_pages": 3
    }

    Returns:
        PNG image
    """
    try:
        data = request.get_json()

        # Generate QR code
        qr_bytes = qr_generator.generate_qr_bytes(
            lecture_id=data['lecture_id'],
            course_id=data['course_id'],
            date=data['date'],
            page_number=data['page_number'],
            total_pages=data['total_pages']
        )

        # Return as image
        from io import BytesIO
        return send_file(
            BytesIO(qr_bytes),
            mimetype='image/png',
            as_attachment=True,
            download_name=f'qr_{data["lecture_id"]}_p{data["page_number"]}.png'
        )

    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/api/templates/<lecture_id>', methods=['GET'])
def get_bubble_templates(lecture_id):
    """
    Get bubble coordinates for a lecture (for OMR processing)

    Args:
        lecture_id: Lecture ID

    Returns:
    {
        "lecture_id": "LEC-xxx",
        "templates": [
            {
                "page_number": 1,
                "student_id": "20240001",
                "student_name": "Ahmed Ali",
                "bubble_x": 550.0,
                "bubble_y": 650.0,
                "bubble_radius": 8.5
            },
            ...
        ]
    }
    """
    try:
        # Query database
        query = "SELECT * FROM bubble_templates WHERE lecture_id = ? ORDER BY page_number, row_number"
        templates = pdf_generator.db.fetch_all(query, (lecture_id,))

        if not templates:
            return jsonify({
                'error': 'No templates found for this lecture',
                'status': 'error'
            }), 404

        return jsonify({
            'lecture_id': lecture_id,
            'total_templates': len(templates),
            'templates': templates,
            'status': 'success'
        }), 200

    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/api/lectures', methods=['GET'])
def list_lectures():
    """
    List all generated lectures

    Returns:
    {
        "lectures": [
            {
                "lecture_id": "LEC-xxx",
                "total_pages": 3,
                "total_students": 90
            },
            ...
        ]
    }
    """
    try:
        query = """
            SELECT lecture_id,
                   MAX(page_number) as total_pages,
                   COUNT(DISTINCT student_id) as total_students
            FROM bubble_templates
            GROUP BY lecture_id
            ORDER BY created_at DESC
        """
        lectures = pdf_generator.db.fetch_all(query)

        return jsonify({
            'lectures': lectures,
            'total_lectures': len(lectures),
            'status': 'success'
        }), 200

    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/api/sheets', methods=['GET'])
def list_sheets():
    """
    List all generated bubble sheets with details

    Returns all PDFs in the generated_sheets folder
    """
    try:
        sheets = []

        # Get all PDF files from the generated_sheets folder
        if os.path.exists(UPLOAD_FOLDER):
            for filename in os.listdir(UPLOAD_FOLDER):
                if filename.endswith('.pdf'):
                    lecture_id = filename.replace('.pdf', '')
                    file_path = os.path.join(UPLOAD_FOLDER, filename)

                    # Get file info
                    file_stat = os.stat(file_path)
                    created_at = datetime.fromtimestamp(file_stat.st_ctime).isoformat()

                    # Try to get metadata from database
                    query = """
                        SELECT
                            lecture_id,
                            MAX(page_number) as total_pages,
                            COUNT(DISTINCT student_id) as total_students,
                            MIN(created_at) as created_at
                        FROM bubble_templates
                        WHERE lecture_id = ?
                        GROUP BY lecture_id
                    """
                    metadata = pdf_generator.db.fetch_one(query, (lecture_id,))

                    sheets.append({
                        'lecture_id': lecture_id,
                        'course_name': 'N/A',  # Will be enhanced later
                        'date': created_at.split('T')[0],
                        'total_students': metadata['total_students'] if metadata else 0,
                        'total_pages': metadata['total_pages'] if metadata else 0,
                        'created_at': created_at
                    })

        # Sort by created date (newest first)
        sheets.sort(key=lambda x: x['created_at'], reverse=True)

        return jsonify({
            'sheets': sheets,
            'total': len(sheets),
            'status': 'success'
        }), 200

    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get service statistics"""
    try:
        total_lectures = pdf_generator.db.fetch_one(
            "SELECT COUNT(DISTINCT lecture_id) as count FROM bubble_templates"
        )
        total_pages = pdf_generator.db.fetch_one(
            "SELECT COUNT(*) as count FROM (SELECT DISTINCT lecture_id, page_number FROM bubble_templates)"
        )
        total_students = pdf_generator.db.fetch_one(
            "SELECT COUNT(*) as count FROM bubble_templates"
        )

        return jsonify({
            'total_lectures': total_lectures['count'] if total_lectures else 0,
            'total_pages': total_pages['count'] if total_pages else 0,
            'total_bubble_coordinates': total_students['count'] if total_students else 0,
            'status': 'success'
        }), 200

    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5003))
    debug_mode = os.getenv('FLASK_ENV', 'development') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
