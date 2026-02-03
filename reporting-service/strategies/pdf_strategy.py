"""
استراتيجية توليد تقارير PDF

استراتيجية ملموسة تُولّد التقارير بصيغة PDF باستخدام ReportLab.
"""

from typing import Dict, List, Any
from .report_strategy import ReportFormatStrategy
from generators.pdf_generator import PDFReportGenerator


class PDFReportStrategy(ReportFormatStrategy):
    """
    استراتيجية ملموسة لتوليد تقارير PDF.

    تستخدم PDFReportGenerator الموجود حالياً لتوليد ملفات .pdf.
    """

    def __init__(self):
        """تهيئة PDFReportGenerator"""
        self.generator = PDFReportGenerator()

    def generate_student_report(self,
                               student_data: Dict[str, Any],
                               attendance_records: List[Dict[str, Any]],
                               course_data: Dict[str, Any]) -> str:
        """
        توليد تقرير حضور طالب بصيغة PDF.

        المعاملات:
            student_data: معلومات الطالب
            attendance_records: سجلات الحضور
            course_data: معلومات المقرر

        الإرجاع:
            str: مسار ملف PDF المُولّد
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
        توليد تقرير مقرر بصيغة PDF.

        المعاملات:
            course_data: معلومات المقرر
            lectures_data: قائمة المحاضرات
            students_data: قائمة الطلاب
            attendance_matrix: مصفوفة الحضور

        الإرجاع:
            str: مسار ملف PDF المُولّد
        """
        return self.generator.generate_course_report(
            course_data,
            lectures_data,
            students_data,
            attendance_matrix
        )

    def get_file_extension(self) -> str:
        """الإرجاع: ".pdf" """
        return ".pdf"
