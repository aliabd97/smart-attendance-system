"""
Attendance model and data operations
"""

from typing import List, Optional, Dict
from datetime import datetime
import hashlib
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from common.database import Database


class AttendanceRecord:
    """Attendance record entity"""

    def __init__(self, id: int, student_id: str, course_id: str,
                 date: str, status: str, session_name: str = None,
                 idempotency_key: str = None):
        self.id = id
        self.student_id = student_id
        self.course_id = course_id
        self.date = date
        self.status = status  # present, absent, late, excused
        self.session_name = session_name
        self.idempotency_key = idempotency_key or self._generate_key()

    def _generate_key(self):
        """Generate idempotency key"""
        data = f"{self.student_id}:{self.course_id}:{self.date}:{self.session_name or ''}"
        return hashlib.sha256(data.encode()).hexdigest()

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'date': self.date,
            'status': self.status,
            'session_name': self.session_name,
            'idempotency_key': self.idempotency_key
        }

    @staticmethod
    def from_dict(data: Dict) -> 'AttendanceRecord':
        """Create from dictionary"""
        return AttendanceRecord(
            id=data.get('id'),
            student_id=data.get('student_id'),
            course_id=data.get('course_id'),
            date=data.get('date'),
            status=data.get('status'),
            session_name=data.get('session_name'),
            idempotency_key=data.get('idempotency_key')
        )


class AttendanceRepository:
    """Attendance repository for database operations"""

    def __init__(self, db: Database):
        self.db = db
        self._init_table()

    def _init_table(self):
        """Create attendance_records table if not exists"""
        schema = """
        CREATE TABLE IF NOT EXISTS attendance_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            course_id TEXT NOT NULL,
            date DATE NOT NULL,
            status TEXT NOT NULL,
            session_name TEXT,
            idempotency_key TEXT UNIQUE,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, course_id, date, session_name)
        )
        """
        self.db.create_table(schema)

    def record_attendance(self, student_id: str, course_id: str,
                         date: str, status: str, session_name: str = None) -> tuple[bool, str, int]:
        """
        Record attendance (idempotent operation)

        Args:
            student_id: Student ID
            course_id: Course ID
            date: Date in YYYY-MM-DD format
            status: Attendance status
            session_name: Optional session name

        Returns:
            Tuple of (success, message, record_id)
        """
        try:
            # Generate idempotency key
            temp_record = AttendanceRecord(
                id=None,
                student_id=student_id,
                course_id=course_id,
                date=date,
                status=status,
                session_name=session_name
            )
            key = temp_record._generate_key()

            # Check if already exists
            existing = self.db.fetch_one(
                "SELECT id FROM attendance_records WHERE idempotency_key = ?",
                (key,)
            )

            if existing:
                return True, 'Already recorded', existing['id']

            # Insert new record
            record_id = self.db.insert('attendance_records', {
                'student_id': student_id,
                'course_id': course_id,
                'date': date,
                'status': status,
                'session_name': session_name,
                'idempotency_key': key
            })

            return True, 'Recorded successfully', record_id

        except Exception as e:
            print(f"Error recording attendance: {e}")
            return False, str(e), None

    def get_attendance_records(self, **filters) -> List[AttendanceRecord]:
        """
        Get attendance records with optional filters

        Args:
            **filters: student_id, course_id, date, session_name
        """
        query = "SELECT * FROM attendance_records WHERE 1=1"
        params = []

        if filters.get('student_id'):
            query += " AND student_id = ?"
            params.append(filters['student_id'])

        if filters.get('course_id'):
            query += " AND course_id = ?"
            params.append(filters['course_id'])

        if filters.get('date'):
            query += " AND date = ?"
            params.append(filters['date'])

        if filters.get('session_name'):
            query += " AND session_name = ?"
            params.append(filters['session_name'])

        query += " ORDER BY date DESC, recorded_at DESC"

        rows = self.db.fetch_all(query, tuple(params))
        return [AttendanceRecord.from_dict(row) for row in rows]

    def get_student_attendance_summary(self, student_id: str, course_id: str = None) -> Dict:
        """
        Get attendance summary for a student

        Args:
            student_id: Student ID
            course_id: Optional course ID filter

        Returns:
            Summary dictionary
        """
        query = """
            SELECT
                status,
                COUNT(*) as count
            FROM attendance_records
            WHERE student_id = ?
        """
        params = [student_id]

        if course_id:
            query += " AND course_id = ?"
            params.append(course_id)

        query += " GROUP BY status"

        rows = self.db.fetch_all(query, tuple(params))

        summary = {
            'student_id': student_id,
            'course_id': course_id,
            'total': 0,
            'present': 0,
            'absent': 0,
            'late': 0,
            'excused': 0
        }

        for row in rows:
            status = row['status']
            count = row['count']
            summary[status] = count
            summary['total'] += count

        # Calculate attendance percentage
        if summary['total'] > 0:
            summary['attendance_percentage'] = round(
                (summary['present'] + summary['late']) / summary['total'] * 100, 2
            )
        else:
            summary['attendance_percentage'] = 0.0

        return summary

    def get_course_attendance_summary(self, course_id: str, date: str = None) -> Dict:
        """
        Get attendance summary for a course

        Args:
            course_id: Course ID
            date: Optional date filter

        Returns:
            Summary dictionary
        """
        query = """
            SELECT
                status,
                COUNT(*) as count
            FROM attendance_records
            WHERE course_id = ?
        """
        params = [course_id]

        if date:
            query += " AND date = ?"
            params.append(date)

        query += " GROUP BY status"

        rows = self.db.fetch_all(query, tuple(params))

        summary = {
            'course_id': course_id,
            'date': date,
            'total': 0,
            'present': 0,
            'absent': 0,
            'late': 0,
            'excused': 0
        }

        for row in rows:
            status = row['status']
            count = row['count']
            summary[status] = count
            summary['total'] += count

        return summary

    def bulk_record_attendance(self, records: List[Dict]) -> tuple[int, int]:
        """
        Bulk record attendance

        Args:
            records: List of attendance record dictionaries

        Returns:
            Tuple of (success_count, error_count)
        """
        success_count = 0
        error_count = 0

        for record in records:
            success, _, _ = self.record_attendance(
                student_id=record['student_id'],
                course_id=record['course_id'],
                date=record['date'],
                status=record['status'],
                session_name=record.get('session_name')
            )

            if success:
                success_count += 1
            else:
                error_count += 1

        return success_count, error_count
