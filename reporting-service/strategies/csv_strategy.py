"""
استراتيجية توليد تقارير CSV (جديدة)

استراتيجية ملموسة تُولّد التقارير بصيغة CSV (Comma-Separated Values).
هذه صيغة بسيطة يمكن فتحها في Excel أو أي محرر نصوص.

الميزة الأكاديمية:
- يُظهر Open/Closed Principle: أضفنا صيغة جديدة بدون تعديل كود موجود
- استراتيجية جديدة = ملف جديد فقط
"""

import os
import csv
from datetime import datetime
from typing import Dict, List, Any
from .report_strategy import ReportFormatStrategy


class CSVReportStrategy(ReportFormatStrategy):
    """
    استراتيجية ملموسة لتوليد تقارير CSV.

    CSV (Comma-Separated Values) هي صيغة نصية بسيطة:
    - سهلة القراءة والتحرير
    - يمكن فتحها في Excel
    - مناسبة للتحليل البرمجي (Python pandas, R, إلخ)
    - حجم ملف أصغر من Excel/PDF
    """

    def __init__(self, output_dir: str = 'reports/csv'):
        """
        تهيئة CSV Strategy.

        المعاملات:
            output_dir: المجلد لحفظ ملفات CSV (افتراضياً: reports/csv)
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_student_report(self,
                               student_data: Dict[str, Any],
                               attendance_records: List[Dict[str, Any]],
                               course_data: Dict[str, Any]) -> str:
        """
        توليد تقرير حضور طالب بصيغة CSV.

        البنية:
        Date,Lecture ID,Status,Marked At
        2026-01-15,LEC001,present,2026-01-15 10:30:00
        2026-01-17,LEC002,absent,2026-01-17 10:30:00
        ...

        المعاملات:
            student_data: معلومات الطالب
            attendance_records: سجلات الحضور
            course_data: معلومات المقرر

        الإرجاع:
            str: مسار ملف CSV المُولّد
        """
        # اسم الملف
        student_id = student_data.get('student_id', 'unknown')
        course_code = course_data.get('course_code', 'unknown')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"student_{student_id}_{course_code}_{timestamp}.csv"
        filepath = os.path.join(self.output_dir, filename)

        # كتابة CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            # رأس الملف (metadata)
            f.write(f"# تقرير حضور الطالب\n")
            f.write(f"# Student: {student_data.get('name', 'N/A')} ({student_id})\n")
            f.write(f"# Course: {course_data.get('name', 'N/A')} ({course_code})\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"#\n")

            # رأس الجدول
            fieldnames = ['date', 'lecture_id', 'status', 'marked_at']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            # البيانات
            for record in attendance_records:
                writer.writerow({
                    'date': record.get('date', ''),
                    'lecture_id': record.get('lecture_id', ''),
                    'status': record.get('status', ''),
                    'marked_at': record.get('marked_at', '')
                })

            # إحصائيات
            total_records = len(attendance_records)
            present_count = sum(1 for r in attendance_records if r.get('status') == 'present')
            absent_count = total_records - present_count
            percentage = (present_count / total_records * 100) if total_records > 0 else 0

            f.write(f"\n")
            f.write(f"# Summary\n")
            f.write(f"# Total Lectures: {total_records}\n")
            f.write(f"# Present: {present_count}\n")
            f.write(f"# Absent: {absent_count}\n")
            f.write(f"# Attendance %: {percentage:.2f}%\n")

        print(f"[CSV Strategy] تقرير الطالب تم توليده: {filepath}")
        return filepath

    def generate_course_report(self,
                              course_data: Dict[str, Any],
                              lectures_data: List[Dict[str, Any]],
                              students_data: List[Dict[str, Any]],
                              attendance_matrix: Dict[tuple, str]) -> str:
        """
        توليد تقرير مقرر بصيغة CSV.

        البنية:
        Student ID,Student Name,2026-01-15,2026-01-17,...,Present,Absent,%
        STU001,Ahmad Ali,P,A,...,5,2,71.43
        STU002,Sara Mohammed,P,P,...,7,0,100.0
        ...

        حيث P = Present, A = Absent, L = Late, E = Excused

        المعاملات:
            course_data: معلومات المقرر
            lectures_data: قائمة المحاضرات
            students_data: قائمة الطلاب
            attendance_matrix: مصفوفة الحضور

        الإرجاع:
            str: مسار ملف CSV المُولّد
        """
        # اسم الملف
        course_code = course_data.get('course_code', 'unknown')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"course_{course_code}_{timestamp}.csv"
        filepath = os.path.join(self.output_dir, filename)

        # كتابة CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            # رأس الملف (metadata)
            f.write(f"# تقرير حضور المقرر\n")
            f.write(f"# Course: {course_data.get('name', 'N/A')} ({course_code})\n")
            f.write(f"# Instructor: {course_data.get('instructor', 'N/A')}\n")
            f.write(f"# Total Students: {len(students_data)}\n")
            f.write(f"# Total Lectures: {len(lectures_data)}\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"#\n")

            writer = csv.writer(f)

            # رأس الجدول
            headers = ['Student ID', 'Student Name']
            headers.extend([lecture.get('date', f"Lec{i+1}") for i, lecture in enumerate(lectures_data)])
            headers.extend(['Present', 'Absent', 'Attendance %'])
            writer.writerow(headers)

            # صف لكل طالب
            for student in students_data:
                student_id = student.get('student_id', '')
                student_name = student.get('name', 'N/A')

                row = [student_id, student_name]

                # حالة الحضور لكل محاضرة
                present_count = 0
                for lecture in lectures_data:
                    lecture_id = lecture.get('lecture_id', '')
                    status = attendance_matrix.get((student_id, lecture_id), 'absent')

                    # رمز مختصر: P=Present, A=Absent, L=Late, E=Excused
                    status_symbol = {
                        'present': 'P',
                        'absent': 'A',
                        'late': 'L',
                        'excused': 'E'
                    }.get(status, 'A')

                    row.append(status_symbol)

                    if status == 'present':
                        present_count += 1

                # الإحصائيات
                total_lectures = len(lectures_data)
                absent_count = total_lectures - present_count
                percentage = (present_count / total_lectures * 100) if total_lectures > 0 else 0

                row.extend([present_count, absent_count, f"{percentage:.2f}"])

                writer.writerow(row)

            # إحصائيات عامة
            f.write(f"\n")
            f.write(f"# Legend: P=Present, A=Absent, L=Late, E=Excused\n")

        print(f"[CSV Strategy] تقرير المقرر تم توليده: {filepath}")
        return filepath

    def get_file_extension(self) -> str:
        """الإرجاع: ".csv" """
        return ".csv"
