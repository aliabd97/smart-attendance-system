"""
Reporting Service
Generates attendance reports in Excel and PDF formats
"""
import os
import sys
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests

# Add common directory to path for shared utilities
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'common')))

from circuit_breaker import CircuitBreaker
from timeouts import TimeoutManager
from bulkhead import ServiceBulkheads

from generators.excel_generator import ExcelReportGenerator
from generators.pdf_generator import PDFReportGenerator

app = Flask(__name__)
CORS(app)

# Configuration
STUDENT_SERVICE_URL = os.getenv('STUDENT_SERVICE_URL', 'http://localhost:5001')
COURSE_SERVICE_URL = os.getenv('COURSE_SERVICE_URL', 'http://localhost:5002')
ATTENDANCE_SERVICE_URL = os.getenv('ATTENDANCE_SERVICE_URL', 'http://localhost:5006')

# Initialize generators
excel_generator = ExcelReportGenerator()
pdf_generator = PDFReportGenerator()

# Circuit breakers for external services
student_service_breaker = CircuitBreaker(failure_threshold=3, timeout=30)
course_service_breaker = CircuitBreaker(failure_threshold=3, timeout=30)
attendance_service_breaker = CircuitBreaker(failure_threshold=3, timeout=30)


# Helper functions to fetch data from other services

def fetch_student_data(student_id):
    """Fetch student data from Student Service"""
    try:
        response = requests.get(f'{STUDENT_SERVICE_URL}/api/students/{student_id}', timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {'error': str(e)}


def fetch_course_data(course_id):
    """Fetch course data from Course Service"""
    try:
        response = requests.get(f'{COURSE_SERVICE_URL}/api/courses/{course_id}', timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {'error': str(e)}


def fetch_students_by_course(course_id):
    """Fetch all students in a course"""
    try:
        response = requests.get(f'{COURSE_SERVICE_URL}/api/courses/{course_id}/students', timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {'error': str(e)}


def fetch_attendance_records(student_id=None, course_id=None, lecture_id=None):
    """Fetch attendance records from Attendance Service"""
    try:
        params = {}
        if student_id:
            params['student_id'] = student_id
        if course_id:
            params['course_id'] = course_id
        if lecture_id:
            params['lecture_id'] = lecture_id

        response = requests.get(f'{ATTENDANCE_SERVICE_URL}/api/attendance', params=params, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return []


def fetch_lectures_by_course(course_id):
    """Fetch all lectures for a course"""
    try:
        response = requests.get(f'{ATTENDANCE_SERVICE_URL}/api/lectures/course/{course_id}', timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return []


# API Endpoints

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'reporting-service',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/reports/student/<student_id>', methods=['GET'])
def generate_student_report(student_id):
    """
    Generate attendance report for a single student

    Query parameters:
    - course_id (required): Course ID
    - format (optional): 'excel' or 'pdf' (default: excel)
    """
    try:
        course_id = request.args.get('course_id')
        if not course_id:
            return jsonify({'error': 'course_id is required'}), 400

        report_format = request.args.get('format', 'excel').lower()
        if report_format not in ['excel', 'pdf']:
            return jsonify({'error': 'format must be excel or pdf'}), 400

        # Fetch data from services
        student_data = fetch_student_data(student_id)
        if 'error' in student_data:
            return jsonify({'error': f"Student not found: {student_data['error']}"}), 404

        course_data = fetch_course_data(course_id)
        if 'error' in course_data:
            return jsonify({'error': f"Course not found: {course_data['error']}"}), 404

        attendance_records = fetch_attendance_records(student_id=student_id, course_id=course_id)

        # Generate report
        if report_format == 'excel':
            filepath = excel_generator.generate_student_report(student_data, attendance_records, course_data)
        else:
            filepath = pdf_generator.generate_student_report(student_data, attendance_records, course_data)

        # Return file
        return send_file(
            filepath,
            as_attachment=True,
            download_name=os.path.basename(filepath)
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reports/course/<course_id>', methods=['GET'])
def generate_course_report(course_id):
    """
    Generate attendance report for entire course

    Query parameters:
    - format (optional): 'excel' or 'pdf' (default: excel)
    """
    try:
        report_format = request.args.get('format', 'excel').lower()
        if report_format not in ['excel', 'pdf']:
            return jsonify({'error': 'format must be excel or pdf'}), 400

        # Fetch data from services
        course_data = fetch_course_data(course_id)
        if 'error' in course_data:
            return jsonify({'error': f"Course not found: {course_data['error']}"}), 404

        students_data = fetch_students_by_course(course_id)
        lectures_data = fetch_lectures_by_course(course_id)
        attendance_records = fetch_attendance_records(course_id=course_id)

        # Build attendance matrix
        attendance_matrix = {}
        for record in attendance_records:
            key = (record['student_id'], record['lecture_id'])
            attendance_matrix[key] = record['status']

        # Generate report
        if report_format == 'excel':
            filepath = excel_generator.generate_course_report(
                course_data, lectures_data, students_data, attendance_matrix
            )
        else:
            filepath = pdf_generator.generate_course_report(
                course_data, lectures_data, students_data, attendance_matrix
            )

        # Return file
        return send_file(
            filepath,
            as_attachment=True,
            download_name=os.path.basename(filepath)
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reports/department/<department>', methods=['GET'])
def generate_department_report(department):
    """
    Generate department-wide attendance summary

    Query parameters:
    - format (optional): 'excel' or 'pdf' (default: excel)
    """
    try:
        report_format = request.args.get('format', 'excel').lower()
        if report_format not in ['excel', 'pdf']:
            return jsonify({'error': 'format must be excel or pdf'}), 400

        # Get all courses for department from Course Service
        response = requests.get(f'{COURSE_SERVICE_URL}/api/courses', params={'department': department})
        response.raise_for_status()
        courses = response.json()

        if not courses:
            return jsonify({'error': f'No courses found for department: {department}'}), 404

        # Calculate statistics for each course
        courses_stats = []
        for course in courses:
            course_id = course['course_id']

            # Fetch students and attendance
            students = fetch_students_by_course(course_id)
            lectures = fetch_lectures_by_course(course_id)
            attendance_records = fetch_attendance_records(course_id=course_id)

            if not lectures:
                continue

            # Calculate average attendance
            total_possible = len(students) * len(lectures)
            if total_possible == 0:
                continue

            present_count = sum(1 for r in attendance_records if r['status'] == 'present')
            avg_attendance = (present_count / total_possible * 100)

            # Count at-risk students (below 75%)
            at_risk = 0
            for student in students:
                student_id = student['student_id']
                student_present = sum(1 for r in attendance_records
                                    if r['student_id'] == student_id and r['status'] == 'present')
                student_percentage = (student_present / len(lectures) * 100) if len(lectures) > 0 else 0
                if student_percentage < 75:
                    at_risk += 1

            courses_stats.append({
                'course_code': course['course_code'],
                'course_name': course['name'],
                'total_students': len(students),
                'avg_attendance': avg_attendance,
                'at_risk_students': at_risk
            })

        # Generate report (Excel only for department summary)
        filepath = excel_generator.generate_department_report(department, courses_stats)

        # Return file
        return send_file(
            filepath,
            as_attachment=True,
            download_name=os.path.basename(filepath)
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reports/alerts', methods=['GET'])
def generate_absence_alerts():
    """
    Generate absence alert report for at-risk students

    Query parameters:
    - course_id (optional): Filter by course
    - threshold (optional): Attendance percentage threshold (default: 75)
    """
    try:
        course_id = request.args.get('course_id')
        threshold = int(request.args.get('threshold', 75))

        at_risk_students = []

        if course_id:
            # Single course
            course_data = fetch_course_data(course_id)
            students = fetch_students_by_course(course_id)
            lectures = fetch_lectures_by_course(course_id)
            attendance_records = fetch_attendance_records(course_id=course_id)

            for student in students:
                student_id = student['student_id']
                present_count = sum(1 for r in attendance_records
                                  if r['student_id'] == student_id and r['status'] == 'present')
                absent_count = len(lectures) - present_count
                percentage = (present_count / len(lectures) * 100) if len(lectures) > 0 else 0

                if percentage < threshold:
                    at_risk_students.append({
                        'student_id': student_id,
                        'name': student['name'],
                        'course_name': course_data['name'],
                        'present_count': present_count,
                        'absent_count': absent_count,
                        'attendance_percentage': percentage
                    })
        else:
            # All courses - would need to iterate through all
            return jsonify({'error': 'Please specify course_id for alerts'}), 400

        # Generate PDF alert
        filepath = pdf_generator.generate_absence_alert(at_risk_students, threshold)

        # Return file
        return send_file(
            filepath,
            as_attachment=True,
            download_name=os.path.basename(filepath)
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reports/statistics/<course_id>', methods=['GET'])
def get_course_statistics(course_id):
    """
    Get course attendance statistics (JSON response, not file)
    """
    try:
        # Fetch data
        course_data = fetch_course_data(course_id)
        if 'error' in course_data:
            return jsonify({'error': f"Course not found: {course_data['error']}"}), 404

        students = fetch_students_by_course(course_id)
        lectures = fetch_lectures_by_course(course_id)
        attendance_records = fetch_attendance_records(course_id=course_id)

        # Calculate statistics
        total_students = len(students)
        total_lectures = len(lectures)
        total_possible = total_students * total_lectures

        if total_possible == 0:
            return jsonify({
                'course': course_data,
                'total_students': 0,
                'total_lectures': 0,
                'statistics': {}
            })

        present_count = sum(1 for r in attendance_records if r['status'] == 'present')
        absent_count = total_possible - present_count
        avg_attendance = (present_count / total_possible * 100)

        # Student-level statistics
        student_stats = []
        at_risk_count = 0

        for student in students:
            student_id = student['student_id']
            student_present = sum(1 for r in attendance_records
                                if r['student_id'] == student_id and r['status'] == 'present')
            student_absent = total_lectures - student_present
            student_percentage = (student_present / total_lectures * 100) if total_lectures > 0 else 0

            if student_percentage < 75:
                at_risk_count += 1

            student_stats.append({
                'student_id': student_id,
                'name': student['name'],
                'present': student_present,
                'absent': student_absent,
                'percentage': round(student_percentage, 2),
                'at_risk': student_percentage < 75
            })

        return jsonify({
            'course': course_data,
            'total_students': total_students,
            'total_lectures': total_lectures,
            'statistics': {
                'total_possible_attendance': total_possible,
                'total_present': present_count,
                'total_absent': absent_count,
                'average_attendance_percentage': round(avg_attendance, 2),
                'students_at_risk': at_risk_count
            },
            'students': student_stats
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5009))
    app.run(host='0.0.0.0', port=port, debug=True)
