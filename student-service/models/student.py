"""
Student model and data operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from datetime import datetime
import sys
import os

# Add parent directory to path to import common modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from common.database import Database


class Student:
    """Student entity"""

    def __init__(self, id: str, name: str, email: str = None,
                 department: str = None, level: int = None,
                 phone: str = None, is_active: bool = True,
                 registration_date: str = None):
        self.id = id
        self.name = name
        self.email = email
        self.department = department
        self.level = level
        self.phone = phone
        self.is_active = is_active
        self.registration_date = registration_date or datetime.now().strftime('%Y-%m-%d')

    def to_dict(self) -> Dict:
        """Convert student object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'department': self.department,
            'level': self.level,
            'phone': self.phone,
            'is_active': self.is_active,
            'registration_date': self.registration_date
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Student':
        """Create student object from dictionary"""
        return Student(
            id=data.get('id'),
            name=data.get('name'),
            email=data.get('email'),
            department=data.get('department'),
            level=data.get('level'),
            phone=data.get('phone'),
            is_active=data.get('is_active', True),
            registration_date=data.get('registration_date')
        )


class IStudentDataSource(ABC):
    """Interface for student data sources"""

    @abstractmethod
    def get_student_by_id(self, student_id: str) -> Optional[Student]:
        """Get student by ID"""
        pass

    @abstractmethod
    def get_all_students(self) -> List[Student]:
        """Get all students"""
        pass

    @abstractmethod
    def save_student(self, student: Student) -> bool:
        """Save student"""
        pass

    @abstractmethod
    def update_student(self, student: Student) -> bool:
        """Update student"""
        pass

    @abstractmethod
    def delete_student(self, student_id: str) -> bool:
        """Delete student"""
        pass


class StudentRepository(IStudentDataSource):
    """Student repository for database operations"""

    def __init__(self, db: Database):
        self.db = db
        self._init_table()

    def _init_table(self):
        """Create students table if not exists"""
        schema = """
        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            department TEXT,
            level INTEGER,
            phone TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            registration_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.db.create_table(schema)

    def get_student_by_id(self, student_id: str) -> Optional[Student]:
        """Get student by ID"""
        row = self.db.fetch_one(
            "SELECT * FROM students WHERE id = ?",
            (student_id,)
        )
        return Student.from_dict(row) if row else None

    def get_all_students(self) -> List[Student]:
        """Get all students"""
        rows = self.db.fetch_all("SELECT * FROM students")
        return [Student.from_dict(row) for row in rows]

    def save_student(self, student: Student) -> bool:
        """Save new student"""
        try:
            self.db.insert('students', student.to_dict())
            return True
        except Exception as e:
            print(f"Error saving student: {e}")
            return False

    def update_student(self, student: Student) -> bool:
        """Update existing student"""
        try:
            data = student.to_dict()
            data['updated_at'] = datetime.now().isoformat()
            self.db.update('students', data, 'id = ?', (student.id,))
            return True
        except Exception as e:
            print(f"Error updating student: {e}")
            return False

    def delete_student(self, student_id: str) -> bool:
        """Delete student"""
        try:
            self.db.delete('students', 'id = ?', (student_id,))
            return True
        except Exception as e:
            print(f"Error deleting student: {e}")
            return False

    def search_students(self, query: str) -> List[Student]:
        """Search students by name or ID"""
        rows = self.db.fetch_all(
            "SELECT * FROM students WHERE id LIKE ? OR name LIKE ?",
            (f'%{query}%', f'%{query}%')
        )
        return [Student.from_dict(row) for row in rows]

    def get_students_by_department(self, department: str) -> List[Student]:
        """Get students by department"""
        rows = self.db.fetch_all(
            "SELECT * FROM students WHERE department = ?",
            (department,)
        )
        return [Student.from_dict(row) for row in rows]
