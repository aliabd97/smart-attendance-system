"""
مصنع الاستراتيجيات مع Reflection
Strategy Factory with Reflection Programming

هذا الملف يُظهر Reflection Programming في Python:
- تحميل الفئات ديناميكياً من أسماء نصية
- إنشاء instances بدون ذكر أسماء الفئات مباشرة
- قراءة الإعدادات من ملف خارجي (YAML)

الغرض الأكاديمي:
- Reflection Programming: تحميل ديناميكي للفئات
- Factory Pattern: إنشاء الكائنات بطريقة موحدة
- Strategy Pattern: اختيار الاستراتيجية في وقت التشغيل
- SOLID Principles: Open/Closed, Single Responsibility
"""

import os
import yaml
import importlib
from typing import Optional
from strategies.report_strategy import ReportFormatStrategy


class StrategyFactory:
    """
    مصنع لإنشاء استراتيجيات التقارير ديناميكياً باستخدام Reflection.

    كيفية العمل:
    1. قراءة ملف الإعدادات (config/report_config.yml)
    2. استخراج اسم الاستراتيجية المطلوبة (مثلاً "csv")
    3. تحويل الاسم إلى اسم Class (مثلاً "CSVReportStrategy")
    4. استخدام Reflection لتحميل الفئة ديناميكياً
    5. إنشاء instance وإرجاعه
    """

    def __init__(self, config_path: str = 'config/report_config.yml'):
        """
        تهيئة المصنع.

        المعاملات:
            config_path: مسار ملف الإعدادات (YAML)
        """
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """
        قراءة ملف الإعدادات YAML.

        الإرجاع:
            dict: قاموس الإعدادات

        يُطلق:
            FileNotFoundError: إذا لم يُعثر على ملف الإعدادات
            yaml.YAMLError: إذا كان الملف غير صالح
        """
        config_file = os.path.join(
            os.path.dirname(__file__),
            self.config_path
        )

        if not os.path.exists(config_file):
            print(f"[Strategy Factory] تحذير: لم يُعثر على {config_file}")
            print(f"[Strategy Factory] سيتم استخدام الإعدادات الافتراضية")
            return {
                'default_format': 'excel',
                'available_formats': ['excel', 'pdf', 'csv']
            }

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                print(f"[Strategy Factory] تم تحميل الإعدادات من: {config_file}")
                print(f"[Strategy Factory] الصيغة الافتراضية: {config.get('default_format', 'excel')}")
                return config
        except yaml.YAMLError as e:
            print(f"[Strategy Factory] خطأ في قراءة YAML: {e}")
            return {
                'default_format': 'excel',
                'available_formats': ['excel', 'pdf', 'csv']
            }

    def get_default_format(self) -> str:
        """
        الحصول على الصيغة الافتراضية من الإعدادات.

        الإرجاع:
            str: اسم الصيغة الافتراضية (مثلاً "excel")
        """
        return self.config.get('default_format', 'excel')

    def get_available_formats(self) -> list:
        """
        الحصول على قائمة الصيغ المتاحة.

        الإرجاع:
            list: قائمة أسماء الصيغ المتاحة
        """
        return self.config.get('available_formats', ['excel', 'pdf', 'csv'])

    def is_format_available(self, format_name: str) -> bool:
        """
        التحقق من توفر صيغة معينة.

        المعاملات:
            format_name: اسم الصيغة (مثلاً "csv")

        الإرجاع:
            bool: True إذا كانت الصيغة متاحة
        """
        return format_name.lower() in self.get_available_formats()

    def _format_name_to_class_name(self, format_name: str) -> str:
        """
        تحويل اسم الصيغة إلى اسم الفئة.

        أمثلة:
            "excel" -> "ExcelReportStrategy"
            "pdf" -> "PDFReportStrategy"
            "csv" -> "CSVReportStrategy"
            "json" -> "JSONReportStrategy"

        المعاملات:
            format_name: اسم الصيغة (حروف صغيرة)

        الإرجاع:
            str: اسم الفئة (PascalCase + "ReportStrategy")
        """
        # تحويل "csv" -> "CSV", "excel" -> "Excel"
        formatted = format_name.upper() if len(format_name) <= 4 else format_name.capitalize()
        return f"{formatted}ReportStrategy"

    def create_strategy(self, format_name: Optional[str] = None) -> ReportFormatStrategy:
        """
        إنشاء استراتيجية باستخدام Reflection.

        هذه هي الدالة الأساسية التي تُظهر Reflection Programming:

        خطوات Reflection:
        1. تحديد اسم الصيغة (من المعامل أو من الإعدادات)
        2. تحويل الاسم إلى اسم الفئة (مثلاً "csv" -> "CSVReportStrategy")
        3. استيراد module الاستراتيجيات (importlib)
        4. الحصول على الفئة من Module (getattr)
        5. إنشاء instance من الفئة
        6. إرجاع الـ instance

        المعاملات:
            format_name: اسم الصيغة (اختياري، إذا لم يُحدد يُستخدم default_format)

        الإرجاع:
            ReportFormatStrategy: instance من الاستراتيجية المطلوبة

        يُطلق:
            ValueError: إذا كانت الصيغة غير متاحة
            AttributeError: إذا لم تُعثر على الفئة المطلوبة
        """
        # الخطوة 1: تحديد اسم الصيغة
        if format_name is None:
            format_name = self.get_default_format()

        format_name = format_name.lower()

        # التحقق من توفر الصيغة
        if not self.is_format_available(format_name):
            raise ValueError(
                f"الصيغة '{format_name}' غير متاحة. "
                f"الصيغ المتاحة: {self.get_available_formats()}"
            )

        # الخطوة 2: تحويل الاسم إلى اسم الفئة
        class_name = self._format_name_to_class_name(format_name)

        print(f"[Reflection] تحميل الاستراتيجية: {format_name} -> {class_name}")

        try:
            # الخطوة 3: استيراد module الاستراتيجيات
            # importlib.import_module يحمّل الـ module ديناميكياً
            strategies_module = importlib.import_module('strategies')

            # الخطوة 4: الحصول على الفئة من الـ module
            # getattr يبحث عن الفئة بالاسم (string) في الـ module
            StrategyClass = getattr(strategies_module, class_name)

            # الخطوة 5: إنشاء instance
            strategy_instance = StrategyClass()

            print(f"[Reflection] تم إنشاء: {strategy_instance.__class__.__name__}")

            # الخطوة 6: إرجاع الـ instance
            return strategy_instance

        except AttributeError as e:
            # الفئة غير موجودة
            raise AttributeError(
                f"لم يتم العثور على الفئة '{class_name}' في module strategies. "
                f"تأكد من وجود ملف strategies/{format_name}_strategy.py "
                f"وأن الفئة {class_name} معرّفة فيه."
            ) from e

        except Exception as e:
            # خطأ آخر
            raise RuntimeError(
                f"خطأ في إنشاء الاستراتيجية '{format_name}': {str(e)}"
            ) from e

    def reload_config(self):
        """
        إعادة تحميل ملف الإعدادات.

        مفيدة إذا تم تعديل ملف الإعدادات أثناء تشغيل الخدمة.
        """
        print(f"[Strategy Factory] إعادة تحميل الإعدادات...")
        self.config = self._load_config()


# ===========================================
# مثال على الاستخدام (للاختبار)
# ===========================================

def example_usage():
    """
    مثال على استخدام Reflection لإنشاء الاستراتيجيات.
    """
    print("\n" + "=" * 60)
    print("مثال على Reflection Programming")
    print("=" * 60 + "\n")

    # إنشاء المصنع
    factory = StrategyFactory()

    # الحالة 1: استخدام الصيغة الافتراضية (من config.yml)
    print("[مثال 1] استخدام الصيغة الافتراضية:")
    default_strategy = factory.create_strategy()
    print(f"    الاستراتيجية: {default_strategy.get_format_name()}")
    print(f"    الامتداد: {default_strategy.get_file_extension()}\n")

    # الحالة 2: تحديد صيغة معينة (Excel)
    print("[مثال 2] تحديد صيغة Excel:")
    excel_strategy = factory.create_strategy('excel')
    print(f"    الاستراتيجية: {excel_strategy.get_format_name()}")
    print(f"    الامتداد: {excel_strategy.get_file_extension()}\n")

    # الحالة 3: استخدام الصيغة الجديدة (CSV)
    print("[مثال 3] استخدام الصيغة الجديدة CSV:")
    csv_strategy = factory.create_strategy('csv')
    print(f"    الاستراتيجية: {csv_strategy.get_format_name()}")
    print(f"    الامتداد: {csv_strategy.get_file_extension()}\n")

    # الحالة 4: صيغة غير متاحة (سيُطلق Exception)
    print("[مثال 4] محاولة استخدام صيغة غير متاحة:")
    try:
        factory.create_strategy('json')
    except ValueError as e:
        print(f"    خطأ متوقع: {e}\n")

    print("=" * 60)
    print("الفوائد الأكاديمية:")
    print("  1. Reflection: تحميل الفئات ديناميكياً من أسماء نصية")
    print("  2. Open/Closed: إضافة صيغة جديدة = ملف جديد فقط")
    print("  3. Strategy Pattern: اختيار الاستراتيجية في وقت التشغيل")
    print("  4. Configuration-driven: السلوك يُحدد من ملف خارجي")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    # تشغيل المثال عند تنفيذ هذا الملف مباشرة
    example_usage()
