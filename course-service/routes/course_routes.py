"""
Course Service API Routes
"""

from flask import Blueprint, request, jsonify
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from models.course import Course, CourseRepository
from common.utils import validate_required_fields

course_bp = Blueprint('courses', __name__, url_prefix='/api')


def create_routes(course_repo: CourseRepository):
    """Create routes with dependency injection"""

    @course_bp.route('/courses', methods=['GET'])
    def get_all_courses():
        """Get all courses"""
        try:
            courses = course_repo.get_all_courses()
            return jsonify({
                'count': len(courses),
                'courses': [c.to_dict() for c in courses]
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @course_bp.route('/courses/<course_id>', methods=['GET'])
    def get_course(course_id):
        """Get course by ID"""
        try:
            course = course_repo.get_course_by_id(course_id)
            if course:
                return jsonify(course.to_dict()), 200
            else:
                return jsonify({'error': 'Course not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @course_bp.route('/courses', methods=['POST'])
    def create_course():
        """Create new course"""
        try:
            data = request.get_json()

            # Validate required fields
            is_valid, error_msg = validate_required_fields(data, ['id', 'name', 'code'])
            if not is_valid:
                return jsonify({'error': error_msg}), 400

            # Check if course already exists
            existing = course_repo.get_course_by_id(data['id'])
            if existing:
                return jsonify({'error': 'Course ID already exists'}), 409

            # Check if course code already exists
            existing_code = course_repo.get_course_by_code(data['code'])
            if existing_code:
                return jsonify({'error': 'Course code already exists'}), 409

            # Create course
            course = Course.from_dict(data)
            if course_repo.save_course(course):
                return jsonify({
                    'message': 'Course created successfully',
                    'course_id': course.id
                }), 201
            else:
                return jsonify({'error': 'Failed to create course'}), 500

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @course_bp.route('/courses/<course_id>', methods=['PUT'])
    def update_course(course_id):
        """Update course"""
        try:
            # Check if course exists
            existing = course_repo.get_course_by_id(course_id)
            if not existing:
                return jsonify({'error': 'Course not found'}), 404

            data = request.get_json()
            data['id'] = course_id  # Ensure ID doesn't change

            # Update course
            course = Course.from_dict(data)
            if course_repo.update_course(course):
                return jsonify({
                    'message': 'Course updated successfully',
                    'course_id': course_id
                }), 200
            else:
                return jsonify({'error': 'Failed to update course'}), 500

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @course_bp.route('/courses/<course_id>', methods=['DELETE'])
    def delete_course(course_id):
        """Delete course"""
        try:
            # Check if course exists
            existing = course_repo.get_course_by_id(course_id)
            if not existing:
                return jsonify({'error': 'Course not found'}), 404

            if course_repo.delete_course(course_id):
                return jsonify({
                    'message': 'Course deleted successfully',
                    'course_id': course_id
                }), 200
            else:
                return jsonify({'error': 'Failed to delete course'}), 500

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @course_bp.route('/courses/department/<department>', methods=['GET'])
    def get_courses_by_department(department):
        """Get courses by department"""
        try:
            courses = course_repo.get_courses_by_department(department)
            return jsonify({
                'department': department,
                'count': len(courses),
                'courses': [c.to_dict() for c in courses]
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Enrollment endpoints
    @course_bp.route('/courses/<course_id>/enroll', methods=['POST'])
    def enroll_student(course_id):
        """Enroll a student in a course"""
        try:
            # Check if course exists
            course = course_repo.get_course_by_id(course_id)
            if not course:
                return jsonify({'error': 'Course not found'}), 404

            data = request.get_json()
            is_valid, error_msg = validate_required_fields(data, ['student_id'])
            if not is_valid:
                return jsonify({'error': error_msg}), 400

            student_id = data['student_id']

            # Check if already enrolled
            existing = course_repo.get_enrollment(student_id, course_id)
            if existing and existing.status == 'active':
                return jsonify({'error': 'Student already enrolled in this course'}), 409

            # Enroll student
            if course_repo.enroll_student(student_id, course_id):
                return jsonify({
                    'message': 'Student enrolled successfully',
                    'student_id': student_id,
                    'course_id': course_id
                }), 201
            else:
                return jsonify({'error': 'Failed to enroll student'}), 500

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @course_bp.route('/courses/<course_id>/unenroll', methods=['POST'])
    def unenroll_student(course_id):
        """Unenroll a student from a course"""
        try:
            data = request.get_json()
            is_valid, error_msg = validate_required_fields(data, ['student_id'])
            if not is_valid:
                return jsonify({'error': error_msg}), 400

            student_id = data['student_id']

            # Check if enrollment exists
            enrollment = course_repo.get_enrollment(student_id, course_id)
            if not enrollment or enrollment.status != 'active':
                return jsonify({'error': 'Student not enrolled in this course'}), 404

            # Unenroll student
            if course_repo.unenroll_student(student_id, course_id):
                return jsonify({
                    'message': 'Student unenrolled successfully',
                    'student_id': student_id,
                    'course_id': course_id
                }), 200
            else:
                return jsonify({'error': 'Failed to unenroll student'}), 500

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @course_bp.route('/courses/<course_id>/students', methods=['GET'])
    def get_enrolled_students(course_id):
        """Get all students enrolled in a course"""
        try:
            # Check if course exists
            course = course_repo.get_course_by_id(course_id)
            if not course:
                return jsonify({'error': 'Course not found'}), 404

            enrollments = course_repo.get_course_enrollments(course_id)
            student_ids = [e.student_id for e in enrollments]

            return jsonify({
                'course_id': course_id,
                'course_name': course.name,
                'enrolled_count': len(student_ids),
                'student_ids': student_ids,
                'enrollments': [e.to_dict() for e in enrollments]
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @course_bp.route('/students/<student_id>/courses', methods=['GET'])
    def get_student_courses(student_id):
        """Get all courses a student is enrolled in"""
        try:
            enrollments = course_repo.get_student_enrollments(student_id)
            course_ids = [e.course_id for e in enrollments]

            # Get course details
            courses = []
            for course_id in course_ids:
                course = course_repo.get_course_by_id(course_id)
                if course:
                    courses.append(course.to_dict())

            return jsonify({
                'student_id': student_id,
                'enrolled_count': len(courses),
                'courses': courses
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return course_bp
