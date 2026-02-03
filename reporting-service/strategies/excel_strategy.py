"""
استراتيجية توليد تقارير Excel

استراتيجية ملموسة تُولّد التقارير بصيغة Excel (.xlsx) باستخدام openpyxl.
"""

from typing import Dict, List, Any
from .report_strategy import ReportFormatStrategy
from generators.excel_generator import ExcelReportGenerator


class ExcelReportStrategy(ReportFormatStrategy):
    """
    استراتيجية ملموسة لتوليد تقارير Excel.

    تستخدم ExcelReportGenerator الموجود حالياً لتوليد ملفات .xlsx.
    """

    def __init__(self):
        """تهيئة ExcelReportGenerator"""
        self.generator = ExcelReportGenerator()

    def generate_student_report(self,
                               student_data: Dict[str, Any],
                               attendance_records: List[Dict[str, Any]],
                               course_data: Dict[str, Any]) -> str:
        """
        توليد تقرير حضور طالب بصيغة Excel.

        المعاملات:
            student_data: معلومات الطالب
            attendance_records: سجلات الحضور
            course_data: معلومات المقرر

        الإرجاع:
            str: مسار ملف Excel المُولّد
        """
        return self.generator.generate_student_report(
            student_data,
            attendance_records,
            course_data
        )

    def generate_course_report(self,
                              course_data: Dict[str, Any],
                              lectures_data: List[Dict[str, Any]],
                              students_data: List[Dict[str, Any]],
                              attendance_matrix: Dict[tuple, str]) -> str:
        """
        توليد تقرير مقرر بصيغة Excel.

        المعاملات:
            course_data: معلومات المقرر
            lectures_data: قائمة المحاضرات
            students_data: قائمة الطلاب
            attendance_matrix: مصفوفة الحضور

        الإرجاع:
            str: مسار ملف Excel المُولّد
        """
        return self.generator.generate_course_report(
            course_data,
            lectures_data,
            students_data,
            attendance_matrix
        )

    def get_file_extension(self) -> str:
        """الإرجاع: ".xlsx" """
        return ".xlsx"
