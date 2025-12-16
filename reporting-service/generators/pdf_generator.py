"""
PDF Report Generator
Generates attendance reports in PDF format
"""
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class PDFReportGenerator:
    """Generates attendance reports in PDF format"""

    def __init__(self, output_dir='reports/pdf'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()

        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=20,
            alignment=TA_CENTER
        )

        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2e5fa3'),
            spaceAfter=12
        )

    def generate_student_report(self, student_data, attendance_records, course_data):
        """
        Generate attendance report for a single student

        Args:
            student_data: Student information
            attendance_records: List of attendance records
            course_data: Course information

        Returns:
            str: Path to generated PDF file
        """
        filename = f"student_{student_data.get('student_id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []

        # Title
        title = Paragraph('Student Attendance Report', self.title_style)
        story.append(title)
        story.append(Spacer(1, 12))

        # Student information table
        info_data = [
            ['Student ID:', student_data.get('student_id', 'N/A')],
            ['Student Name:', student_data.get('name', 'N/A')],
            ['Department:', student_data.get('department', 'N/A')],
            ['Course:', course_data.get('name', 'N/A')]
        ]

        info_table = Table(info_data, colWidths=[100, 300])
        info_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))

        story.append(info_table)
        story.append(Spacer(1, 20))

        # Statistics
        total_lectures = len(attendance_records)
        present_count = sum(1 for r in attendance_records if r.get('status') == 'present')
        absent_count = total_lectures - present_count
        attendance_percentage = (present_count / total_lectures * 100) if total_lectures > 0 else 0

        stats_data = [
            ['Total Lectures', 'Present', 'Absent', 'Attendance %'],
            [str(total_lectures), str(present_count), str(absent_count), f'{attendance_percentage:.2f}%']
        ]

        stats_table = Table(stats_data, colWidths=[100, 100, 100, 100])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (1, 1), (1, 1), colors.HexColor('#C6EFCE')),
            ('BACKGROUND', (2, 1), (2, 1), colors.HexColor('#FFC7CE')),
        ]))

        story.append(stats_table)
        story.append(Spacer(1, 20))

        # Attendance records
        heading = Paragraph('Attendance Records', self.heading_style)
        story.append(heading)

        records_data = [['Date', 'Lecture ID', 'Status', 'Marked At']]
        for record in attendance_records:
            records_data.append([
                record.get('date', ''),
                record.get('lecture_id', ''),
                record.get('status', '').upper(),
                record.get('marked_at', '')
            ])

        records_table = Table(records_data, colWidths=[80, 100, 60, 140])

        # Build table style
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]

        # Color code status column
        for idx, record in enumerate(attendance_records, start=1):
            if record.get('status') == 'present':
                table_style.append(('BACKGROUND', (2, idx), (2, idx), colors.HexColor('#C6EFCE')))
            else:
                table_style.append(('BACKGROUND', (2, idx), (2, idx), colors.HexColor('#FFC7CE')))

        records_table.setStyle(TableStyle(table_style))
        story.append(records_table)

        # Build PDF
        doc.build(story)
        return filepath

    def generate_course_report(self, course_data, lectures_data, students_data, attendance_matrix):
        """
        Generate attendance report for a course

        Args:
            course_data: Course information
            lectures_data: List of lectures
            students_data: List of students
            attendance_matrix: Dict mapping (student_id, lecture_id) -> status

        Returns:
            str: Path to generated PDF file
        """
        filename = f"course_{course_data.get('course_code', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(filepath, pagesize=landscape(A4))
        story = []

        # Title
        title = Paragraph(f"Attendance Report - {course_data.get('name', 'Course')}", self.title_style)
        story.append(title)
        story.append(Spacer(1, 12))

        # Course information
        info_data = [
            ['Course Code:', course_data.get('course_code', 'N/A')],
            ['Instructor:', course_data.get('instructor', 'N/A')],
            ['Total Students:', str(len(students_data))],
            ['Total Lectures:', str(len(lectures_data))]
        ]

        info_table = Table(info_data, colWidths=[100, 200])
        info_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 9),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 9),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))

        story.append(info_table)
        story.append(Spacer(1, 15))

        # Attendance matrix (compact view - only stats)
        heading = Paragraph('Student Attendance Summary', self.heading_style)
        story.append(heading)

        summary_data = [['Student ID', 'Student Name', 'Present', 'Absent', 'Total', 'Attendance %']]

        for student in students_data:
            student_id = student.get('student_id', '')
            present_count = 0
            absent_count = 0

            for lecture in lectures_data:
                lecture_id = lecture.get('lecture_id', '')
                status = attendance_matrix.get((student_id, lecture_id), 'absent')
                if status == 'present':
                    present_count += 1
                else:
                    absent_count += 1

            total = len(lectures_data)
            percentage = (present_count / total * 100) if total > 0 else 0

            summary_data.append([
                student_id,
                student.get('name', ''),
                str(present_count),
                str(absent_count),
                str(total),
                f'{percentage:.1f}%'
            ])

        summary_table = Table(summary_data, colWidths=[70, 150, 50, 50, 40, 70])

        # Build table style
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]

        # Color code percentage column
        for idx, student in enumerate(students_data, start=1):
            student_id = student.get('student_id', '')
            present_count = sum(1 for lecture in lectures_data
                              if attendance_matrix.get((student_id, lecture.get('lecture_id', '')), 'absent') == 'present')
            total = len(lectures_data)
            percentage = (present_count / total * 100) if total > 0 else 0

            if percentage < 50:
                table_style.append(('BACKGROUND', (5, idx), (5, idx), colors.HexColor('#FFC7CE')))
            elif percentage < 75:
                table_style.append(('BACKGROUND', (5, idx), (5, idx), colors.HexColor('#FFEB9C')))
            else:
                table_style.append(('BACKGROUND', (5, idx), (5, idx), colors.HexColor('#C6EFCE')))

        summary_table.setStyle(TableStyle(table_style))
        story.append(summary_table)

        # Build PDF
        doc.build(story)
        return filepath

    def generate_absence_alert(self, at_risk_students, threshold=75):
        """
        Generate absence alert report for at-risk students

        Args:
            at_risk_students: List of students below threshold
            threshold: Attendance percentage threshold

        Returns:
            str: Path to generated PDF file
        """
        filename = f"absence_alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []

        # Title
        title = Paragraph(f'Absence Alert Report - Below {threshold}%', self.title_style)
        story.append(title)
        story.append(Spacer(1, 12))

        # Alert message
        alert_text = f"The following students have attendance below {threshold}% and require immediate attention:"
        alert = Paragraph(alert_text, self.styles['Normal'])
        story.append(alert)
        story.append(Spacer(1, 15))

        # At-risk students table
        alert_data = [['Student ID', 'Student Name', 'Course', 'Present', 'Absent', 'Attendance %', 'Risk Level']]

        for student in at_risk_students:
            percentage = student.get('attendance_percentage', 0)

            if percentage < 50:
                risk_level = 'CRITICAL'
            elif percentage < 60:
                risk_level = 'HIGH'
            else:
                risk_level = 'MODERATE'

            alert_data.append([
                student.get('student_id', ''),
                student.get('name', ''),
                student.get('course_name', ''),
                str(student.get('present_count', 0)),
                str(student.get('absent_count', 0)),
                f"{percentage:.1f}%",
                risk_level
            ])

        alert_table = Table(alert_data, colWidths=[60, 120, 100, 45, 45, 60, 70])

        # Build table style
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C00000')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]

        # Color code risk level
        for idx, student in enumerate(at_risk_students, start=1):
            percentage = student.get('attendance_percentage', 0)

            if percentage < 50:
                table_style.append(('BACKGROUND', (6, idx), (6, idx), colors.HexColor('#C00000')))
                table_style.append(('TEXTCOLOR', (6, idx), (6, idx), colors.whitesmoke))
            elif percentage < 60:
                table_style.append(('BACKGROUND', (6, idx), (6, idx), colors.HexColor('#FF6B6B')))
            else:
                table_style.append(('BACKGROUND', (6, idx), (6, idx), colors.HexColor('#FFEB9C')))

        alert_table.setStyle(TableStyle(table_style))
        story.append(alert_table)

        # Build PDF
        doc.build(story)
        return filepath
