"""
Course and Enrollment models
"""

from typing import List, Optional, Dict
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from common.database import Database


class Course:
    """Course entity"""

    def __init__(self, id: str, name: str, code: str,
                 department: str = None, credits: int = None,
                 instructor: str = None, semester: str = None,
                 academic_year: str = None):
        self.id = id
        self.name = name
        self.code = code
        self.department = department
        self.credits = credits
        self.instructor = instructor
        self.semester = semester
        self.academic_year = academic_year

    def to_dict(self) -> Dict:
        """Convert course object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'department': self.department,
            'credits': self.credits,
            'instructor': self.instructor,
            'semester': self.semester,
            'academic_year': self.academic_year
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Course':
        """Create course object from dictionary"""
        return Course(
            id=data.get('id'),
            name=data.get('name'),
            code=data.get('code'),
            department=data.get('department'),
            credits=data.get('credits'),
            instructor=data.get('instructor'),
            semester=data.get('semester'),
            academic_year=data.get('academic_year')
        )


class Enrollment:
    """Enrollment entity"""

    def __init__(self, id: int, student_id: str, course_id: str,
                 enrollment_date: str = None, status: str = 'active'):
        self.id = id
        self.student_id = student_id
        self.course_id = course_id
        self.enrollment_date = enrollment_date or datetime.now().strftime('%Y-%m-%d')
        self.status = status

    def to_dict(self) -> Dict:
        """Convert enrollment object to dictionary"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'enrollment_date': self.enrollment_date,
            'status': self.status
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Enrollment':
        """Create enrollment object from dictionary"""
        return Enrollment(
            id=data.get('id'),
            student_id=data.get('student_id'),
            course_id=data.get('course_id'),
            enrollment_date=data.get('enrollment_date'),
            status=data.get('status', 'active')
        )


class CourseRepository:
    """Course repository for database operations"""

    def __init__(self, db: Database):
        self.db = db
        self._init_tables()

    def _init_tables(self):
        """Create courses and enrollments tables if not exist"""
        courses_schema = """
        CREATE TABLE IF NOT EXISTS courses (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            department TEXT,
            credits INTEGER,
            instructor TEXT,
            semester TEXT,
            academic_year TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        enrollments_schema = """
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            course_id TEXT NOT NULL,
            enrollment_date DATE,
            status TEXT DEFAULT 'active',
            UNIQUE(student_id, course_id)
        )
        """

        self.db.create_table(courses_schema)
        self.db.create_table(enrollments_schema)

    # Course operations
    def get_course_by_id(self, course_id: str) -> Optional[Course]:
        """Get course by ID"""
        row = self.db.fetch_one(
            "SELECT * FROM courses WHERE id = ?",
            (course_id,)
        )
        return Course.from_dict(row) if row else None

    def get_course_by_code(self, code: str) -> Optional[Course]:
        """Get course by code"""
        row = self.db.fetch_one(
            "SELECT * FROM courses WHERE code = ?",
            (code,)
        )
        return Course.from_dict(row) if row else None

    def get_all_courses(self) -> List[Course]:
        """Get all courses"""
        rows = self.db.fetch_all("SELECT * FROM courses")
        return [Course.from_dict(row) for row in rows]

    def save_course(self, course: Course) -> bool:
        """Save new course"""
        try:
            self.db.insert('courses', course.to_dict())
            return True
        except Exception as e:
            print(f"Error saving course: {e}")
            return False

    def update_course(self, course: Course) -> bool:
        """Update existing course"""
        try:
            self.db.update('courses', course.to_dict(), 'id = ?', (course.id,))
            return True
        except Exception as e:
            print(f"Error updating course: {e}")
            return False

    def delete_course(self, course_id: str) -> bool:
        """Delete course"""
        try:
            self.db.delete('courses', 'id = ?', (course_id,))
            return True
        except Exception as e:
            print(f"Error deleting course: {e}")
            return False

    def get_courses_by_department(self, department: str) -> List[Course]:
        """Get courses by department"""
        rows = self.db.fetch_all(
            "SELECT * FROM courses WHERE department = ?",
            (department,)
        )
        return [Course.from_dict(row) for row in rows]

    # Enrollment operations
    def enroll_student(self, student_id: str, course_id: str) -> bool:
        """Enroll a student in a course"""
        try:
            enrollment_data = {
                'student_id': student_id,
                'course_id': course_id,
                'enrollment_date': datetime.now().strftime('%Y-%m-%d'),
                'status': 'active'
            }
            self.db.insert('enrollments', enrollment_data)
            return True
        except Exception as e:
            print(f"Error enrolling student: {e}")
            return False

    def get_enrollment(self, student_id: str, course_id: str) -> Optional[Enrollment]:
        """Get specific enrollment"""
        row = self.db.fetch_one(
            "SELECT * FROM enrollments WHERE student_id = ? AND course_id = ?",
            (student_id, course_id)
        )
        return Enrollment.from_dict(row) if row else None

    def get_course_enrollments(self, course_id: str) -> List[Enrollment]:
        """Get all enrollments for a course"""
        rows = self.db.fetch_all(
            "SELECT * FROM enrollments WHERE course_id = ? AND status = 'active'",
            (course_id,)
        )
        return [Enrollment.from_dict(row) for row in rows]

    def get_student_enrollments(self, student_id: str) -> List[Enrollment]:
        """Get all enrollments for a student"""
        rows = self.db.fetch_all(
            "SELECT * FROM enrollments WHERE student_id = ? AND status = 'active'",
            (student_id,)
        )
        return [Enrollment.from_dict(row) for row in rows]

    def unenroll_student(self, student_id: str, course_id: str) -> bool:
        """Unenroll a student from a course"""
        try:
            self.db.update(
                'enrollments',
                {'status': 'inactive'},
                'student_id = ? AND course_id = ?',
                (student_id, course_id)
            )
            return True
        except Exception as e:
            print(f"Error unenrolling student: {e}")
            return False

    def get_enrolled_student_ids(self, course_id: str) -> List[str]:
        """Get list of student IDs enrolled in a course"""
        rows = self.db.fetch_all(
            "SELECT student_id FROM enrollments WHERE course_id = ? AND status = 'active'",
            (course_id,)
        )
        return [row['student_id'] for row in rows]
