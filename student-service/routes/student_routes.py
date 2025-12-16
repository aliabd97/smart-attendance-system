"""
Student Service API Routes
"""

from flask import Blueprint, request, jsonify
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from models.student import Student, StudentRepository
from adapters.excel_adapter import ExcelAdapter
from common.utils import validate_required_fields

student_bp = Blueprint('students', __name__, url_prefix='/api')


def create_routes(student_repo: StudentRepository):
    """Create routes with dependency injection"""

    @student_bp.route('/students', methods=['GET'])
    def get_all_students():
        """Get all students"""
        try:
            students = student_repo.get_all_students()
            return jsonify({
                'count': len(students),
                'students': [s.to_dict() for s in students]
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @student_bp.route('/students/<student_id>', methods=['GET'])
    def get_student(student_id):
        """Get student by ID"""
        try:
            student = student_repo.get_student_by_id(student_id)
            if student:
                return jsonify(student.to_dict()), 200
            else:
                return jsonify({'error': 'Student not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @student_bp.route('/students', methods=['POST'])
    def create_student():
        """Create new student"""
        try:
            data = request.get_json()

            # Validate required fields
            is_valid, error_msg = validate_required_fields(data, ['id', 'name'])
            if not is_valid:
                return jsonify({'error': error_msg}), 400

            # Check if student already exists
            existing = student_repo.get_student_by_id(data['id'])
            if existing:
                return jsonify({'error': 'Student already exists'}), 409

            # Create student
            student = Student.from_dict(data)
            if student_repo.save_student(student):
                return jsonify({
                    'message': 'Student created successfully',
                    'student_id': student.id
                }), 201
            else:
                return jsonify({'error': 'Failed to create student'}), 500

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @student_bp.route('/students/<student_id>', methods=['PUT'])
    def update_student(student_id):
        """Update student"""
        try:
            # Check if student exists
            existing = student_repo.get_student_by_id(student_id)
            if not existing:
                return jsonify({'error': 'Student not found'}), 404

            data = request.get_json()
            data['id'] = student_id  # Ensure ID doesn't change

            # Update student
            student = Student.from_dict(data)
            if student_repo.update_student(student):
                return jsonify({
                    'message': 'Student updated successfully',
                    'student_id': student_id
                }), 200
            else:
                return jsonify({'error': 'Failed to update student'}), 500

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @student_bp.route('/students/<student_id>', methods=['DELETE'])
    def delete_student(student_id):
        """Delete student"""
        try:
            # Check if student exists
            existing = student_repo.get_student_by_id(student_id)
            if not existing:
                return jsonify({'error': 'Student not found'}), 404

            if student_repo.delete_student(student_id):
                return jsonify({
                    'message': 'Student deleted successfully',
                    'student_id': student_id
                }), 200
            else:
                return jsonify({'error': 'Failed to delete student'}), 500

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @student_bp.route('/students/search', methods=['GET'])
    def search_students():
        """Search students by name or ID"""
        try:
            query = request.args.get('q', '')
            if not query:
                return jsonify({'error': 'Query parameter "q" is required'}), 400

            students = student_repo.search_students(query)
            return jsonify({
                'count': len(students),
                'students': [s.to_dict() for s in students]
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @student_bp.route('/students/department/<department>', methods=['GET'])
    def get_students_by_department(department):
        """Get students by department"""
        try:
            students = student_repo.get_students_by_department(department)
            return jsonify({
                'department': department,
                'count': len(students),
                'students': [s.to_dict() for s in students]
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @student_bp.route('/students/import-excel', methods=['POST'])
    def import_excel():
        """
        Import students from Excel file
        Uses Adapter Pattern to convert legacy Excel format
        """
        try:
            # Check if file was uploaded
            if 'file' not in request.files:
                return jsonify({'error': 'No file uploaded'}), 400

            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400

            # Save uploaded file temporarily
            upload_path = os.path.join('uploads', file.filename)
            os.makedirs('uploads', exist_ok=True)
            file.save(upload_path)

            # Use Excel Adapter to import
            adapter = ExcelAdapter(upload_path, target_repository=student_repo)

            # Get preview first (optional)
            preview = adapter.get_import_preview(limit=3)

            # Import to database
            success_count, error_count = adapter.import_to_repository()

            # Clean up temp file
            os.remove(upload_path)

            return jsonify({
                'message': 'Import completed',
                'success_count': success_count,
                'error_count': error_count,
                'preview': preview
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @student_bp.route('/students/import-excel/preview', methods=['POST'])
    def preview_excel():
        """Preview Excel file before importing"""
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file uploaded'}), 400

            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400

            # Save uploaded file temporarily
            upload_path = os.path.join('uploads', file.filename)
            os.makedirs('uploads', exist_ok=True)
            file.save(upload_path)

            # Get preview
            adapter = ExcelAdapter(upload_path)
            preview = adapter.get_import_preview(limit=10)

            # Clean up temp file
            os.remove(upload_path)

            return jsonify({
                'preview': preview,
                'count': len(preview)
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return student_bp
