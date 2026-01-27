"""
Excel Adapter Pattern Implementation
Adapts legacy Excel student data to modern Student model
"""

from __future__ import annotations
import openpyxl
from typing import List, Optional
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from models.student import Student, IStudentDataSource
from adapters.field_mapper import FieldMapper
from adapters.value_transformer import ValueTransformer


class ExcelReader:
    """Reads Excel files and returns rows as dictionaries"""

    @staticmethod
    def read(file_path: str) -> List[dict]:
        """
        Read Excel file and return list of row dictionaries

        Args:
            file_path: Path to Excel file

        Returns:
            List of dictionaries (one per row)
        """
        try:
            workbook = openpyxl.load_workbook(file_path)
            sheet = workbook.active

            # Get headers from first row
            headers = []
            for cell in sheet[1]:
                headers.append(cell.value)

            # Read data rows
            rows = []
            for row in sheet.iter_rows(min_row=2, values_only=True):
                row_dict = {}
                for i, value in enumerate(row):
                    if i < len(headers):
                        row_dict[headers[i]] = value
                rows.append(row_dict)

            print(f"✅ Read {len(rows)} rows from Excel file")
            return rows

        except Exception as e:
            print(f"❌ Error reading Excel file: {e}")
            raise


class ExcelAdapter(IStudentDataSource):
    """
    Adapter that converts Excel data to Student objects
    Implements the Adapter Pattern to bridge legacy Excel format
    with modern Student model
    """

    def __init__(self, file_path: str, target_repository: IStudentDataSource = None):
        """
        Initialize Excel adapter

        Args:
            file_path: Path to Excel file
            target_repository: Optional repository to save imported students
        """
        self.file_path = file_path
        self.target_repository = target_repository
        self.excel_reader = ExcelReader()
        self.field_mapper = FieldMapper()
        self.value_transformer = ValueTransformer()
        self._students_cache = []

    def _load_from_excel(self):
        """Load and transform students from Excel file"""
        if self._students_cache:
            return  # Already loaded

        excel_rows = self.excel_reader.read(self.file_path)

        for excel_row in excel_rows:
            # Step 1: Map field names
            mapped_row = self.field_mapper.map_row(excel_row)

            # Step 2: Transform values
            transformed_row = self.value_transformer.transform_row(mapped_row)

            # Step 3: Create Student object
            try:
                student = Student.from_dict(transformed_row)
                self._students_cache.append(student)
            except Exception as e:
                print(f"⚠️ Warning: Skipping invalid row: {e}")
                continue

        print(f"✅ Loaded {len(self._students_cache)} students from Excel")

    def get_student_by_id(self, student_id: str) -> Optional[Student]:
        """Get student by ID from Excel data"""
        self._load_from_excel()
        for student in self._students_cache:
            if student.id == student_id:
                return student
        return None

    def get_all_students(self) -> List[Student]:
        """Get all students from Excel data"""
        self._load_from_excel()
        return self._students_cache

    def save_student(self, student: Student) -> bool:
        """
        Save student to target repository if available

        Args:
            student: Student object to save

        Returns:
            True if saved successfully
        """
        if self.target_repository:
            return self.target_repository.save_student(student)
        else:
            print("⚠️ No target repository configured")
            return False

    def update_student(self, student: Student) -> bool:
        """Update student in target repository"""
        if self.target_repository:
            return self.target_repository.update_student(student)
        return False

    def delete_student(self, student_id: str) -> bool:
        """Delete student from target repository"""
        if self.target_repository:
            return self.target_repository.delete_student(student_id)
        return False

    def import_to_repository(self):
        """
        Import all Excel students to target repository

        Returns:
            Tuple of (success_count, error_count)
        """
        if not self.target_repository:
            raise Exception("No target repository configured")

        self._load_from_excel()

        success_count = 0
        error_count = 0

        for student in self._students_cache:
            try:
                if self.target_repository.save_student(student):
                    success_count += 1
                else:
                    error_count += 1
            except Exception as e:
                print(f"❌ Error importing student {student.id}: {e}")
                error_count += 1

        print(f"✅ Import complete: {success_count} success, {error_count} errors")
        return success_count, error_count

    def get_import_preview(self, limit: int = 5) -> List[dict]:
        """
        Get preview of Excel data before importing

        Args:
            limit: Number of rows to preview

        Returns:
            List of student dictionaries
        """
        self._load_from_excel()
        preview = []
        for student in self._students_cache[:limit]:
            preview.append(student.to_dict())
        return preview
