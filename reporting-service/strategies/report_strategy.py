"""
واجهة استراتيجية التقارير المجردة (Abstract Report Strategy Interface)

تُعرّف العقد الذي يجب أن تلتزم به جميع استراتيجيات توليد التقارير الملموسة.
هذا يتبع نمط Strategy Pattern للسماح بصيغ تقارير مختلفة بدون تعديل كود العميل.

الغرض الأكاديمي:
- يُظهر Strategy Pattern (نمط سلوكي)
- ي��بق مبدأ Open/Closed من SOLID
- يسمح باختيار الاستراتيجية ديناميكياً عبر Reflection
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any


class ReportFormatStrategy(ABC):
    """
    الفئة الأساسية المجردة لجميع استراتيجيات توليد التقارير.

    كل استراتيجية ملموسة تُنفذ صيغة تقرير مختلفة (Excel, PDF, CSV, إلخ)
    بدون تغيير كود العميل الذي يستخدمها.

    الفوائد:
    1. مبدأ Open/Closed: مفتوح للتوسع (صيغ جديدة)، مغلق للتعديل
    2. مبدأ المسؤولية الواحدة: كل استراتيجية تعالج صيغة واحدة فقط
    3. المرونة في وقت التشغيل: تبديل الاستراتيجيات عبر ملف الإعدادات
    """

    @abstractmethod
    def generate_student_report(self,
                               student_data: Dict[str, Any],
                               attendance_records: List[Dict[str, Any]],
                               course_data: Dict[str, Any]) -> str:
        """
        توليد تقرير حضور لطالب واحد.

        المعاملات:
            student_data: معلومات الطالب (id, name, department, إلخ)
            attendance_records: قائمة سجلات الحضور
            course_data: معلومات المقرر (code, name, instructor, إلخ)

        الإرجاع:
            str: مسار الملف المُولّد

        يُطلق:
            NotImplementedError: إذا لم تنفذ الفئة الفرعية هذه الدالة
        """
        pass

    @abstractmethod
    def generate_course_report(self,
                              course_data: Dict[str, Any],
                              lectures_data: List[Dict[str, Any]],
                              students_data: List[Dict[str, Any]],
                              attendance_matrix: Dict[tuple, str]) -> str:
        """
        توليد تقرير حضور لمقرر كامل.

        المعاملات:
            course_data: معلومات المقرر
            lectures_data: قائمة المحاضرات
            students_data: قائمة الطلاب المسجلين
            attendance_matrix: Dict[(student_id, lecture_id)] -> status

        الإرجاع:
            str: مسار الملف المُولّد

        يُطلق:
            NotImplementedError: إذا لم تنفذ الفئة الفرعية هذه الدالة
        """
        pass

    def get_format_name(self) -> str:
        """
        الحصول على اسم الصيغة لهذه الاستراتيجية.

        الإرجاع:
            str: اسم الصيغة (مثلاً "Excel", "PDF", "CSV")
        """
        return self.__class__.__name__.replace('ReportStrategy', '')

    def get_file_extension(self) -> str:
        """
        الحصول على امتداد الملف لهذه الصيغة.
        يجب تجاوزها في الفئات الفرعية.

        الإرجاع:
            str: امتداد الملف (مثلاً ".xlsx", ".pdf", ".csv")
        """
        return ".txt"  # قيمة افتراضية
