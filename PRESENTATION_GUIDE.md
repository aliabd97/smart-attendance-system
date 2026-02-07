# دليل العرض التقديمي الكامل
## نظام الحضور الذكي - Smart Attendance System

---

# كيف تبدأ العرض

## قبل العرض (تحضير):
```
1. شغّل RabbitMQ: rabbitmq-server (أو من Windows Services)
2. شغّل النظام: .\START.ps1
3. تأكد من فتح: http://localhost:3000
4. سجّل الدخول: admin / admin123
5. افتح هذا الملف أمامك للقراءة
```

## المقدمة (قلها للمشرف):
> **بالعربي:** "هذا نظام حضور ذكي مبني على معمارية الخدمات المصغرة. يتكون من 8 خدمات مستقلة، وطبّقت فيه 4 أنماط تصميم هي: Circuit Breaker باستخدام State Pattern، و Strategy Pattern مع Reflection، و Choreography Pattern باستخدام RabbitMQ، و JWT Authentication."
>
> **In English:** "This is a smart attendance system built on microservices architecture. It consists of 8 independent services, and I implemented 4 design patterns: Circuit Breaker using State Pattern, Strategy Pattern with Reflection, Choreography Pattern using RabbitMQ, and JWT Authentication."

## ترتيب الشرح المقترح:
1. **JWT Authentication** (الأسهل - ابدأ به)
2. **Strategy Pattern** (واضح ومباشر)
3. **Circuit Breaker** (أكثر تعقيداً)
4. **Choreography** (الأكثر تعقيداً - اتركه للنهاية)

---

# ════════════════════════════════════════════════════════════════
# المطلب الأول: Circuit Breaker Pattern (State Pattern)
# ════════════════════════════════════════════════════════════════

## ماذا تقول للمشرف (المقدمة):
> **بالعربي:** "هذا النمط يحمي النظام من الانهيار المتتالي. مثلاً إذا خدمة الحضور تعطلت، بدل ما نضيّع وقت ننتظرها كل مرة، النظام يتذكر إنها معطلة ويرفض الطلبات فوراً لمدة معينة، ثم يعيد الاختبار."
>
> **In English:** "This pattern protects the system from cascading failures. For example, if the attendance service fails, instead of wasting time waiting for it every time, the system remembers it's down and rejects requests immediately for a certain period, then retests."

## ماذا تقول (الحالات الثلاث):
> **بالعربي:** "النمط له 3 حالات مثل State Pattern:
> - CLOSED: الحالة الطبيعية، الطلبات تمر
> - OPEN: بعد 3 أخطاء متتالية، الطلبات تُرفض فوراً
> - HALF_OPEN: بعد 15 ثانية، نجرب طلب واحد لنرى هل الخدمة رجعت"
>
> **In English:** "The pattern has 3 states like State Pattern:
> - CLOSED: Normal state, requests pass through
> - OPEN: After 3 consecutive failures, requests are rejected immediately
> - HALF_OPEN: After 15 seconds, we try one request to see if the service recovered"

---

## الملفات ومواقع الكود

### الملف الرئيسي (التطبيق اليدوي):
**المسار الكامل:** `c:\Users\HP\smart-attendance-system\common\circuit_breaker.py`

#### تعريف الحالات (سطر 19-24):
```python
# الملف: c:\Users\HP\smart-attendance-system\common\circuit_breaker.py
# الأسطر: 19-24

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"          # Normal operation
    OPEN = "open"              # Failing - reject requests
    HALF_OPEN = "half_open"    # Testing if service recovered
```

**قل للمشرف:**
> **بالعربي:** "هنا عرّفت الحالات الثلاث كـ Enum، وهذا أساس State Pattern."
>
> **In English:** "Here I defined the three states as an Enum, and this is the foundation of State Pattern."

#### الدالة الرئيسية call (سطر 77-103):
```python
# الملف: c:\Users\HP\smart-attendance-system\common\circuit_breaker.py
# الأسطر: 77-103

def call(self, func: Callable, *args, **kwargs) -> Any:
    # Check if circuit is OPEN
    if self.state == CircuitState.OPEN:
        if self._should_attempt_reset():
            self.state = CircuitState.HALF_OPEN  # انتقال للاختبار
        else:
            raise Exception("Circuit breaker is OPEN")  # رفض فوري

    # Try to execute the function
    try:
        result = func(*args, **kwargs)
        self._on_success()
        return result
    except Exception as e:
        self._on_failure()
        raise e
```

**قل للمشرف:**
> **بالعربي:** "هذه الدالة الأساسية. أولاً تتحقق من الحالة، إذا OPEN ترفض فوراً، وإلا تحاول تنفيذ الطلب."
>
> **In English:** "This is the main function. First it checks the state, if OPEN it rejects immediately, otherwise it tries to execute the request."

#### دالة معالجة الفشل (سطر 123-139):
```python
# الملف: c:\Users\HP\smart-attendance-system\common\circuit_breaker.py
# الأسطر: 123-139

def _on_failure(self):
    """Handle failed call"""
    self.failure_count += 1
    self.last_failure_time = datetime.now()

    if self.state == CircuitState.HALF_OPEN:
        self.state = CircuitState.OPEN  # فشل الاختبار

    elif self.failure_count >= self.failure_threshold:
        self.state = CircuitState.OPEN  # 3 أخطاء = فتح الدائرة
```

**قل للمشرف:**
> **بالعربي:** "عند كل فشل، نزيد العداد. إذا وصل 3، نفتح الدائرة."
>
> **In English:** "On each failure, we increment the counter. If it reaches 3, we open the circuit."

---

### الملف الثاني (التطبيق بالمكتبة):
**المسار الكامل:** `c:\Users\HP\smart-attendance-system\common\circuit_breaker_library.py`

#### استخدام مكتبة pybreaker (سطر 29-34):
```python
# الملف: c:\Users\HP\smart-attendance-system\common\circuit_breaker_library.py
# الأسطر: 29-34

self.breaker = pybreaker.CircuitBreaker(
    fail_max=failure_threshold,    # 3 أخطاء = فتح الدائرة
    reset_timeout=timeout,         # 15 ثانية ثم اختبار
    listeners=[self.listener],     # مراقب للتسجيل
    name=name
)
```

**قل للمشرف:**
> **بالعربي:** "هنا نفس المفهوم لكن باستخدام مكتبة pybreaker. أقل كود، نفس النتيجة."
>
> **In English:** "Here's the same concept but using the pybreaker library. Less code, same result."

---

### ملف الاستخدام الفعلي:
**المسار الكامل:** `c:\Users\HP\smart-attendance-system\pdf-processing-service\app.py`

#### تهيئة Circuit Breaker (سطر 27-33):
```python
# الملف: c:\Users\HP\smart-attendance-system\pdf-processing-service\app.py
# الأسطر: 27-33

circuit_breaker = CircuitBreaker(
    name="attendance-service",
    failure_threshold=3,
    timeout=15,
    success_threshold=2
)
```

**قل للمشرف:**
> **بالعربي:** "هنا أنشأت Circuit Breaker لحماية الاتصال بخدمة الحضور."
>
> **In English:** "Here I created a Circuit Breaker to protect the connection to the attendance service."

---

## كيف تُظهر للمشرف (خطوة بخطوة):

### الخطوة 1: افتح Dashboard
> **قل:** "سأفتح صفحة Design Patterns ثم Circuit Breaker"
> **Say:** "I'll open the Design Patterns page then Circuit Breaker"
```
http://localhost:3000 → Design Patterns → Circuit Breaker tab
```

### الخطوة 2: أظهر الحالة الطبيعية
> **قل:** "هنا الحالة CLOSED، يعني كل شي طبيعي"
> **Say:** "Here the state is CLOSED, meaning everything is normal"
- أشر على البطاقة الخضراء

### الخطوة 3: أوقف Attendance Service
> **قل:** "الآن سأوقف خدمة الحضور لمحاكاة عطل"
> **Say:** "Now I'll stop the attendance service to simulate a failure"
- أغلق نافذة Attendance Service

### الخطوة 4: اضغط Test 3 مرات
> **قل:** "كل ضغطة = خطأ. بعد 3 أخطاء، الدائرة تنفتح"
> **Say:** "Each click = error. After 3 errors, the circuit opens"
- اضغط "Test Attendance Service" 3 مرات
- أشر على تغيّر الحالة إلى **OPEN** (أحمر)

### الخطوة 5: أظهر الرفض الفوري
> **قل:** "الآن لاحظ: الطلبات تُرفض فوراً بدون انتظار"
> **Say:** "Now notice: requests are rejected immediately without waiting"
- اضغط Test مرة أخرى
- أشر على الرسالة: "Circuit is OPEN"

### الخطوة 6: انتظر HALF_OPEN
> **قل:** "بعد 15 ثانية، النظام يجرب مرة أخرى"
> **Say:** "After 15 seconds, the system tries again"
- انتظر حتى تتحول إلى **HALF_OPEN** (أصفر)

### الخطوة 7: أعد تشغيل الخدمة
> **قل:** "الآن أشغّل الخدمة ونختبر"
> **Say:** "Now I'll start the service and test"
- شغّل Attendance Service
- اضغط Test مرتين بنجاح
- أشر على تغيّر الحالة إلى **CLOSED** (أخضر)

---

## أسئلة متوقعة:

### س: لماذا 3 أخطاء وليس 5؟
> **بالعربي:** "رقم متوازن. لو أقل، الدائرة تفتح بخطأ عابر. لو أكثر، نتأخر في اكتشاف المشكلة."
>
> **In English:** "It's a balanced number. If less, the circuit opens on a transient error. If more, we delay detecting the problem."

### س: لماذا 15 ثانية؟
> **بالعربي:** "يعطي الخدمة وقت للتعافي. لو أقل، نضغط على خدمة مريضة. لو أكثر، ننتظر كثير."
>
> **In English:** "It gives the service time to recover. If less, we pressure a sick service. If more, we wait too long."

### س: ما الفرق بين التطبيق اليدوي والمكتبة؟
> **بالعربي:** "اليدوي: تحكم كامل وتعلم أفضل. المكتبة: أسرع وأقل أخطاء."
>
> **In English:** "Manual: full control and better learning. Library: faster and fewer bugs."

### س: هذا Client-side أم Server-side؟
> **بالعربي:** "Client-side. الخدمة المُستدعية (PDF Processing) هي التي تحمي نفسها."
>
> **In English:** "Client-side. The calling service (PDF Processing) is the one protecting itself."

---

# ════════════════════════════════════════════════════════════════
# المطلب الثاني: Strategy Pattern + Reflection
# ════════════════════════════════════════════════════════════════

## ماذا تقول للمشرف (المقدمة):
> **بالعربي:** "هذا النمط يسمح بتبديل الخوارزميات في وقت التشغيل. مثلاً المستخدم يختار صيغة التقرير (Excel أو PDF أو CSV)، والنظام ينفذ الاستراتيجية المناسبة بدون if-else طويلة."
>
> **In English:** "This pattern allows swapping algorithms at runtime. For example, the user chooses the report format (Excel, PDF, or CSV), and the system executes the appropriate strategy without long if-else chains."

## ماذا تقول (Reflection):
> **بالعربي:** "استخدمت Reflection لتحميل الـ classes ديناميكياً من أسماء نصية. يعني أكتب 'csv' كـ string، والنظام يحمّل CSVReportStrategy تلقائياً."
>
> **In English:** "I used Reflection to load classes dynamically from string names. Meaning I write 'csv' as a string, and the system loads CSVReportStrategy automatically."

---

## الملفات ومواقع الكود

### الملف الرئيسي (الواجهة المجردة):
**المسار الكامل:** `c:\Users\HP\smart-attendance-system\reporting-service\strategies\report_strategy.py`

#### تعريف Abstract Class (سطر 16-47):
```python
# الملف: c:\Users\HP\smart-attendance-system\reporting-service\strategies\report_strategy.py
# الأسطر: 16-47

class ReportFormatStrategy(ABC):
    """الفئة الأساسية المجردة لجميع استراتيجيات التقارير"""

    @abstractmethod
    def generate_student_report(self,
                               student_data: Dict[str, Any],
                               attendance_records: List[Dict[str, Any]],
                               course_data: Dict[str, Any]) -> str:
        """توليد تقرير حضور لطالب واحد"""
        pass

    @abstractmethod
    def generate_course_report(self,
                              course_data: Dict[str, Any],
                              lectures_data: List[Dict[str, Any]],
                              students_data: List[Dict[str, Any]],
                              attendance_matrix: Dict[tuple, str]) -> str:
        """توليد تقرير حضور لمقرر كامل"""
        pass
```

**قل للمشرف:**
> **بالعربي:** "هذه الواجهة المجردة. كل استراتيجية جديدة لازم تنفّذ هذه الدوال."
>
> **In English:** "This is the abstract interface. Every new strategy must implement these methods."

---

### استراتيجية PDF:
**المسار الكامل:** `c:\Users\HP\smart-attendance-system\reporting-service\strategies\pdf_strategy.py`

#### تنفيذ PDF Strategy (سطر 12-70):
```python
# الملف: c:\Users\HP\smart-attendance-system\reporting-service\strategies\pdf_strategy.py
# الأسطر: 12-42

class PDFReportStrategy(ReportFormatStrategy):
    """استراتيجية ملموسة لتوليد تقارير PDF"""

    def __init__(self):
        self.generator = PDFReportGenerator()

    def generate_student_report(self,
                               student_data: Dict[str, Any],
                               attendance_records: List[Dict[str, Any]],
                               course_data: Dict[str, Any]) -> str:
        return self.generator.generate_student_report(
            student_data,
            attendance_records,
            course_data
        )

    def get_file_extension(self) -> str:
        return ".pdf"
```

**قل للمشرف:**
> **بالعربي:** "هذه استراتيجية PDF. ترث من الواجهة المجردة وتنفّذ الدوال بطريقتها."
>
> **In English:** "This is the PDF strategy. It inherits from the abstract interface and implements the methods in its own way."

---

### المصنع مع Reflection:
**المسار الكامل:** `c:\Users\HP\smart-attendance-system\reporting-service\strategy_factory.py`

#### دالة create_strategy مع Reflection (سطر 132-203):
```python
# الملف: c:\Users\HP\smart-attendance-system\reporting-service\strategy_factory.py
# الأسطر: 156-189

def create_strategy(self, format_name: Optional[str] = None) -> ReportFormatStrategy:
    """إنشاء استراتيجية باستخدام Reflection"""

    # الخطوة 1: تحديد اسم الصيغة
    if format_name is None:
        format_name = self.get_default_format()

    # الخطوة 2: تحويل الاسم إلى اسم الفئة
    class_name = self._format_name_to_class_name(format_name)
    # "csv" -> "CSVReportStrategy"

    # الخطوة 3: Reflection - تحميل الـ module ديناميكياً
    strategies_module = importlib.import_module('strategies')

    # الخطوة 4: Reflection - الحصول على الفئة من الاسم النصي
    StrategyClass = getattr(strategies_module, class_name)

    # الخطوة 5: إنشاء instance
    return StrategyClass()
```

**قل للمشرف:**
> **بالعربي:** "هنا السحر! importlib.import_module يحمّل الـ module ديناميكياً، و getattr يجيب الـ class من اسم نصي. هذا Reflection."
>
> **In English:** "Here's the magic! importlib.import_module loads the module dynamically, and getattr gets the class from a string name. This is Reflection."

#### تحويل الاسم إلى Class Name (سطر 112-130):
```python
# الملف: c:\Users\HP\smart-attendance-system\reporting-service\strategy_factory.py
# الأسطر: 112-130

def _format_name_to_class_name(self, format_name: str) -> str:
    """
    تحويل اسم الصيغة إلى اسم الفئة.

    أمثلة:
        "excel" -> "ExcelReportStrategy"
        "pdf" -> "PDFReportStrategy"
        "csv" -> "CSVReportStrategy"
    """
    formatted = format_name.upper() if len(format_name) <= 4 else format_name.capitalize()
    return f"{formatted}ReportStrategy"
```

**قل للمشرف:**
> **بالعربي:** "هذه الدالة تحوّل الاسم النصي إلى اسم الـ class."
>
> **In English:** "This function converts the string name to the class name."

---

### ملف الإعدادات:
**المسار الكامل:** `c:\Users\HP\smart-attendance-system\reporting-service\config\report_config.yml`

```yaml
# الملف: c:\Users\HP\smart-attendance-system\reporting-service\config\report_config.yml

# الصيغة الافتراضية
default_format: excel

# الصيغ المتاحة
available_formats:
  - excel
  - pdf
  - csv
```

**قل للمشرف:**
> **بالعربي:** "الإعدادات من ملف خارجي. لو بغيت أضيف صيغة جديدة، أضيفها هنا."
>
> **In English:** "Settings are from an external file. If I want to add a new format, I add it here."

---

## كيف تُظهر للمشرف (خطوة بخطوة):

### الخطوة 1: افتح Dashboard
> **قل:** "سأفتح صفحة Design Patterns ثم Strategy Pattern"
> **Say:** "I'll open the Design Patterns page then Strategy Pattern"
```
http://localhost:3000 → Design Patterns → Strategy Pattern tab
```

### الخطوة 2: أظهر الصيغ المتاحة
> **قل:** "هنا 3 صيغ: Excel, PDF, CSV. كل واحدة استراتيجية منفصلة."
> **Say:** "Here are 3 formats: Excel, PDF, CSV. Each one is a separate strategy."

### الخطوة 3: ولّد تقرير Excel
> **قل:** "سأختار Excel وأضغط Generate"
> **Say:** "I'll choose Excel and click Generate"
- اختر Excel
- اضغط Generate Report
- أشر على الملف المحمّل

### الخطوة 4: ولّد تقرير PDF
> **قل:** "نفس الكود، بس غيّرت الاستراتيجية"
> **Say:** "Same code, just changed the strategy"
- اختر PDF
- اضغط Generate Report

### الخطوة 5: أظهر الكود في IDE (اختياري)
> **قل:** "لاحظ: كل استراتيجية في ملف منفصل"
> **Say:** "Notice: each strategy is in a separate file"
- افتح مجلد `reporting-service/strategies/`
- أشر على الملفات الثلاثة

---

## أسئلة متوقعة:

### س: ما فائدة Strategy Pattern؟
> **بالعربي:** "Open/Closed Principle. أضيف صيغة جديدة بدون تعديل الكود الموجود."
>
> **In English:** "Open/Closed Principle. I add a new format without modifying existing code."

### س: ما فائدة Reflection؟
> **بالعربي:** "لا حاجة لـ if-else. أعطيه اسم نصي، يجيب الـ class تلقائياً."
>
> **In English:** "No need for if-else. I give it a string name, it gets the class automatically."

### س: كيف أضيف صيغة JSON؟
> **بالعربي:** "3 خطوات: 1) ملف json_strategy.py 2) class JSONReportStrategy 3) أضيف 'json' في config.yml. انتهى!"
>
> **In English:** "3 steps: 1) json_strategy.py file 2) JSONReportStrategy class 3) add 'json' in config.yml. Done!"

### س: ما الـ patterns المستخدمة؟
> **بالعربي:** "Strategy للتبديل، Factory للإنشاء، Template Method في الـ abstract class."
>
> **In English:** "Strategy for swapping, Factory for creation, Template Method in the abstract class."

---

# ════════════════════════════════════════════════════════════════
# المطلب الثالث: Choreography Pattern (RabbitMQ)
# ════════════════════════════════════════════════════════════════

## ماذا تقول للمشرف (المقدمة):
> **بالعربي:** "هذا نمط تواصل بين الخدمات. بدل ما خدمة تتصل بخدمة مباشرة، تنشر حدث (Event) في message broker، والخدمات الأخرى تستهلك هذا الحدث بشكل مستقل. لا يوجد منسق مركزي."
>
> **In English:** "This is a communication pattern between services. Instead of one service calling another directly, it publishes an event to a message broker, and other services consume this event independently. There's no central coordinator."

## ماذا تقول (الفرق عن Orchestration):
> **بالعربي:** "في Orchestration، خدمة واحدة تتحكم بالكل مثل قائد الأوركسترا. في Choreography، كل خدمة ترقص لحالها عند سماع الموسيقى (Event)."
>
> **In English:** "In Orchestration, one service controls everything like an orchestra conductor. In Choreography, each service dances on its own when it hears the music (Event)."

---

## الملفات ومواقع الكود

### ملف RabbitMQ Client:
**المسار الكامل:** `c:\Users\HP\smart-attendance-system\common\rabbitmq_client.py`

#### تعريف الـ Client (سطر 20-46):
```python
# الملف: c:\Users\HP\smart-attendance-system\common\rabbitmq_client.py
# الأسطر: 20-46

class RabbitMQClient:
    """Simple RabbitMQ client for publishing and consuming messages"""

    QUEUE_NAME = 'attendance_events'

    def __init__(self, host: str = None):
        self.host = host or os.getenv('RABBITMQ_HOST', 'localhost')
        self.connection = None
        self.channel = None
        self._connect()

    def _connect(self):
        """Connect to RabbitMQ server"""
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host)
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.QUEUE_NAME, durable=True)
```

**قل للمشرف:**
> **بالعربي:** "هذا الـ client للاتصال بـ RabbitMQ. الـ queue اسمها attendance_events."
>
> **In English:** "This is the client for connecting to RabbitMQ. The queue is named attendance_events."

#### دالة النشر publish (سطر 48-79):
```python
# الملف: c:\Users\HP\smart-attendance-system\common\rabbitmq_client.py
# الأسطر: 48-65

def publish(self, message: dict):
    """نشر رسالة (Producer)"""
    self.channel.basic_publish(
        exchange='',
        routing_key=self.QUEUE_NAME,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make message persistent
            content_type='application/json'
        )
    )
```

**قل للمشرف:**
> **بالعربي:** "هذه دالة النشر. delivery_mode=2 يعني الرسالة تُحفظ على القرص."
>
> **In English:** "This is the publish function. delivery_mode=2 means the message is saved to disk."

#### دالة الاستهلاك consume (سطر 81-100):
```python
# الملف: c:\Users\HP\smart-attendance-system\common\rabbitmq_client.py
# الأسطر: 81-100

def consume(self, callback: Callable):
    """استهلاك الرسائل (Consumer)"""
    self.channel.basic_qos(prefetch_count=1)
    self.channel.basic_consume(
        queue=self.QUEUE_NAME,
        on_message_callback=callback,
        auto_ack=False
    )
    self.channel.start_consuming()
```

**قل للمشرف:**
> **بالعربي:** "هذه دالة الاستهلاك. تستدعي callback عند كل رسالة."
>
> **In English:** "This is the consume function. It calls the callback for each message."

---

### ملف Producer (Attendance Service):
**المسار الكامل:** `c:\Users\HP\smart-attendance-system\attendance-service\app.py`

#### نشر الحدث بعد تسجيل الحضور (سطر 91-105):
```python
# الملف: c:\Users\HP\smart-attendance-system\attendance-service\app.py
# الأسطر: 91-105

if success:
    # Choreography: Publish event to RabbitMQ after successful recording
    try:
        rabbitmq.publish({
            'event': 'attendance_recorded',
            'student_id': student_id,
            'course_id': course_id,
            'date': date,
            'status': status
        })
        print(f"✅ [RabbitMQ] Published attendance event for student {student_id}")
    except Exception as rmq_err:
        print(f"❌ [RabbitMQ] Failed to publish event: {rmq_err}")
        raise
```

**قل للمشرف:**
> **بالعربي:** "بعد تسجيل الحضور بنجاح، ننشر حدث إلى RabbitMQ. الخدمات الأخرى تستهلكه."
>
> **In English:** "After successfully recording attendance, we publish an event to RabbitMQ. Other services consume it."

---

### ملف Consumer (Course Service):
**المسار الكامل:** `c:\Users\HP\smart-attendance-system\course-service\app.py`

#### تخزين الأحداث (سطر 44):
```python
# الملف: c:\Users\HP\smart-attendance-system\course-service\app.py
# السطر: 44

attendance_events_log = []  # Store received events for demo
```

#### Callback عند استلام حدث (سطر 47-69):
```python
# الملف: c:\Users\HP\smart-attendance-system\course-service\app.py
# الأسطر: 47-69

def on_attendance_event(channel, method, properties, body):
    """
    Callback: يُستدعى عند استلام حدث من RabbitMQ.
    Choreography pattern - Course Service reacts independently
    """
    try:
        event = json.loads(body)
        print(f"[RabbitMQ Consumer] Received event: {event}")

        # Store event for demo
        attendance_events_log.append(event)
        if len(attendance_events_log) > 50:
            attendance_events_log.pop(0)

        # Acknowledge the message
        channel.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"[RabbitMQ Consumer] Error processing event: {e}")
        channel.basic_ack(delivery_tag=method.delivery_tag)
```

**قل للمشرف:**
> **بالعربي:** "هذا الـ callback. كل ما توصل رسالة، نخزنها ونؤكد استلامها بـ basic_ack."
>
> **In English:** "This is the callback. Every time a message arrives, we store it and acknowledge receipt with basic_ack."

#### بدء Consumer في thread منفصل (سطر 84-86):
```python
# الملف: c:\Users\HP\smart-attendance-system\course-service\app.py
# الأسطر: 84-86

# Start consumer in background thread (won't block Flask)
consumer_thread = threading.Thread(target=start_rabbitmq_consumer, daemon=True)
consumer_thread.start()
```

**قل للمشرف:**
> **بالعربي:** "الـ consumer يشتغل في thread منفصل عشان ما يعيق Flask."
>
> **In English:** "The consumer runs in a separate thread so it doesn't block Flask."

---

## كيف تُظهر للمشرف (خطوة بخطوة):

### الخطوة 1: افتح RabbitMQ Management
> **قل:** "أولاً أظهر لك RabbitMQ"
> **Say:** "First I'll show you RabbitMQ"
```
http://localhost:15672
Username: guest
Password: guest
```

### الخطوة 2: أظهر الـ Queue
> **قل:** "هذه الـ queue اللي نستخدمها: attendance_events"
> **Say:** "This is the queue we use: attendance_events"
- اذهب إلى Queues → attendance_events

### الخطوة 3: افتح Dashboard Choreography tab
> **قل:** "الآن نرجع للـ Dashboard"
> **Say:** "Now let's go back to the Dashboard"
```
http://localhost:3000 → Design Patterns → Choreography tab
```

### الخطوة 4: سجّل حضور (من OMR)
> **قل:** "سأسجّل حضور عبر OMR Processing"
> **Say:** "I'll record attendance via OMR Processing"
- اذهب إلى OMR Processing
- ارفع bubble sheet
- أو اضغط "Publish Test Event"

### الخطوة 5: أظهر الحدث في Consumed Events
> **قل:** "لاحظ: الحدث وصل Course Service تلقائياً"
> **Say:** "Notice: the event reached Course Service automatically"
- أشر على قائمة Events

### الخطوة 6: أظهر انتظار الرسائل (اختياري)
> **قل:** "لو أوقفت Course Service، الرسائل تنتظر في الـ Queue"
> **Say:** "If I stop Course Service, messages wait in the Queue"
- أوقف Course Service
- سجّل حضور
- افتح RabbitMQ → Queues → Ready = 1
- شغّل Course Service
- Ready = 0 (تم الاستهلاك)

---

## أسئلة متوقعة:

### س: ما الفرق بين Choreography و Orchestration؟
> **بالعربي:** "Orchestration: منسق مركزي يتحكم بكل شي. Choreography: كل خدمة تتصرف بشكل مستقل عند استلام Event."
>
> **In English:** "Orchestration: central coordinator controls everything. Choreography: each service acts independently when receiving an Event."

### س: لماذا RabbitMQ؟
> **بالعربي:** "Message Broker موثوق، يدعم persistence، وسهل الاستخدام مع Python."
>
> **In English:** "Reliable Message Broker, supports persistence, and easy to use with Python."

### س: ماذا لو تعطل RabbitMQ؟
> **بالعربي:** "الخدمات ستفشل في النشر/الاستهلاك. لذلك RabbitMQ مطلوب (Required) في النظام."
>
> **In English:** "Services will fail to publish/consume. That's why RabbitMQ is required in the system."

### س: ما معنى durable و delivery_mode=2؟
> **بالعربي:** "الرسائل تُحفظ على القرص. لو RabbitMQ أعاد التشغيل، الرسائل لا تضيع."
>
> **In English:** "Messages are saved to disk. If RabbitMQ restarts, messages are not lost."

### س: لماذا thread منفصل للـ consumer؟
> **بالعربي:** "لأن start_consuming تُعيق (blocking). لو وضعتها في main thread، Flask ما يشتغل."
>
> **In English:** "Because start_consuming is blocking. If I put it in the main thread, Flask won't work."

---

# ════════════════════════════════════════════════════════════════
# المطلب الرابع: JWT Authentication
# ════════════════════════════════════════════════════════════════

## ماذا تقول للمشرف (المقدمة):
> **بالعربي:** "JWT هو JSON Web Token. طريقة للـ authentication بدون session. المستخدم يسجل دخول، يحصل على token، ويرسله مع كل طلب. الـ token يحتوي معلومات المستخدم ومشفر بتوقيع."
>
> **In English:** "JWT is JSON Web Token. It's an authentication method without sessions. The user logs in, gets a token, and sends it with every request. The token contains user information and is secured with a signature."

## ماذا تقول (لماذا JWT):
> **بالعربي:** "في Microservices، الـ session صعب لأن كل خدمة منفصلة. JWT يحل المشكلة: التوكن يحمل معلومات المستخدم، وأي خدمة تقدر تتحقق منه."
>
> **In English:** "In Microservices, sessions are difficult because each service is separate. JWT solves the problem: the token carries user information, and any service can verify it."

---

## الملفات ومواقع الكود

### ملف Auth Service:
**المسار الكامل:** `c:\Users\HP\smart-attendance-system\auth-service\app.py`

#### المفتاح السري (سطر 25):
```python
# الملف: c:\Users\HP\smart-attendance-system\auth-service\app.py
# السطر: 25

SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production-2024')
```

**قل للمشرف:**
> **بالعربي:** "هذا المفتاح السري للتوقيع. لازم يكون سري ونفسه في كل الخدمات."
>
> **In English:** "This is the secret key for signing. It must be secret and the same across all services."

#### دالة تسجيل الدخول login (سطر 127-190):
```python
# الملف: c:\Users\HP\smart-attendance-system\auth-service\app.py
# الأسطر: 146-187

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # التحقق من المستخدم
    user = db.fetch_one(
        "SELECT * FROM users WHERE username = ? AND is_active = 1",
        (username,)
    )

    if not user or user['password_hash'] != hash_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401

    # إنشاء JWT Token
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    token = jwt.encode({
        'user_id': user['id'],
        'username': user['username'],
        'role': user['role'],
        'exp': expiration
    }, SECRET_KEY, algorithm='HS256')

    return jsonify({
        'token': token,
        'username': user['username'],
        'role': user['role']
    }), 200
```

**قل للمشرف:**
> **بالعربي:** "هنا نتحقق من الـ credentials، ثم ننشئ JWT token يحتوي user_id, username, role, exp."
>
> **In English:** "Here we verify the credentials, then create a JWT token containing user_id, username, role, exp."

#### الخوارزمية HS256 (سطر 175):
```python
# الملف: c:\Users\HP\smart-attendance-system\auth-service\app.py
# السطر: 175

token = jwt.encode({...}, SECRET_KEY, algorithm='HS256')
```

**قل للمشرف:**
> **بالعربي:** "HS256 هي HMAC-SHA256. خوارزمية توقيع متماثلة، نفس المفتاح للتوقيع والتحقق."
>
> **In English:** "HS256 is HMAC-SHA256. A symmetric signing algorithm, same key for signing and verification."

---

### ملف API Gateway:
**المسار الكامل:** `c:\Users\HP\smart-attendance-system\api-gateway\app.py`

#### دالة التحقق من التوكن (سطر 35-61):
```python
# الملف: c:\Users\HP\smart-attendance-system\api-gateway\app.py
# الأسطر: 35-61

def validate_token():
    """Validate JWT token from request headers"""
    token = request.headers.get('Authorization')

    if not token:
        return None, {'error': 'Token required'}, 401

    try:
        # إزالة "Bearer " من البداية
        if token.startswith('Bearer '):
            token = token[7:]

        # فك التوكن والتحقق من التوقيع
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload, None, None

    except jwt.ExpiredSignatureError:
        return None, {'error': 'Token expired'}, 401
    except jwt.InvalidTokenError:
        return None, {'error': 'Invalid token'}, 401
```

**قل للمشرف:**
> **بالعربي:** "الـ Gateway يتحقق من كل توكن. إذا صحيح، يمرر الطلب. إذا لا، يرجع 401."
>
> **In English:** "The Gateway validates every token. If valid, it forwards the request. If not, it returns 401."

#### تمرير معلومات المستخدم للخدمات (سطر 169-175):
```python
# الملف: c:\Users\HP\smart-attendance-system\api-gateway\app.py
# الأسطر: 169-175

# Add user info to headers
headers = {
    'X-User-ID': str(user.get('user_id', '')),
    'X-Username': user.get('username', ''),
    'X-Role': user.get('role', ''),
    'Content-Type': 'application/json'
}
```

**قل للمشرف:**
> **بالعربي:** "بعد التحقق، الـ Gateway يضيف معلومات المستخدم في الـ headers للخدمات الداخلية."
>
> **In English:** "After validation, the Gateway adds user information to headers for internal services."

---

### Decorator للحماية:
**المسار الكامل:** `c:\Users\HP\smart-attendance-system\auth-service\app.py`

#### require_auth decorator (سطر 88-113):
```python
# الملف: c:\Users\HP\smart-attendance-system\auth-service\app.py
# الأسطر: 88-113

def require_auth(f):
    """Decorator to protect endpoints with JWT authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'error': 'Token required'}), 401

        try:
            if token.startswith('Bearer '):
                token = token[7:]
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)
    return decorated
```

**قل للمشرف:**
> **بالعربي:** "هذا decorator. أضعه فوق أي endpoint أبغى أحميه."
>
> **In English:** "This is a decorator. I put it above any endpoint I want to protect."

#### استخدام الـ decorator (سطر 327-334):
```python
# الملف: c:\Users\HP\smart-attendance-system\auth-service\app.py
# الأسطر: 327-334

@app.route('/api/auth/users', methods=['GET'])
@require_auth
def get_users():
    """Get all users (admin only)"""
    if request.user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    # ...
```

**قل للمشرف:**
> **بالعربي:** "هنا مثال: endpoint محمي بـ @require_auth، وبداخله تحقق من الـ role."
>
> **In English:** "Here's an example: endpoint protected with @require_auth, and inside it checks the role."

---

## كيف تُظهر للمشرف (خطوة بخطوة):

### الخطوة 1: افتح Dashboard JWT tab
> **قل:** "سأفتح صفحة JWT Authentication"
> **Say:** "I'll open the JWT Authentication page"
```
http://localhost:3000 → Design Patterns → JWT Authentication tab
```

### الخطوة 2: أظهر حالة "No Token"
> **قل:** "الآن ما في توكن. لاحظ البطاقة الرمادية."
> **Say:** "Now there's no token. Notice the gray card."

### الخطوة 3: سجّل الدخول
> **قل:** "سأسجل دخول بـ admin / admin123"
> **Say:** "I'll log in with admin / admin123"
- أدخل admin / admin123
- اضغط Login
- أشر على التوكن اللي ظهر

### الخطوة 4: اشرح محتويات التوكن
> **قل:** "لاحظ: user_id, username, role, expires. كل هذا في التوكن."
> **Say:** "Notice: user_id, username, role, expires. All this is in the token."
- أشر على البطاقة الخضراء

### الخطوة 5: اختبر مع توكن
> **قل:** "الآن أختبر endpoint محمي مع التوكن"
> **Say:** "Now I'll test a protected endpoint with the token"
- اضغط "Access WITH Token"
- أشر على النجاح الأخضر

### الخطوة 6: اختبر بدون توكن
> **قل:** "الآن بدون توكن"
> **Say:** "Now without a token"
- اضغط "Access WITHOUT Token"
- أشر على الرفض: "401 Unauthorized"

### الخطوة 7: أظهر الـ Logs
> **قل:** "هنا كل العمليات مسجلة"
> **Say:** "Here all operations are logged"
- أشر على قسم Authentication Logs

---

## اختبار من PowerShell (للمشرف إذا طلب):

```powershell
# 1. تسجيل الدخول
$response = Invoke-RestMethod -Uri "http://localhost:5007/api/auth/login" -Method POST -ContentType "application/json" -Body '{"username":"admin","password":"admin123"}'

# 2. عرض التوكن
$response.token

# 3. حفظ التوكن
$token = $response.token

# 4. اختبار مع توكن (نجاح)
$headers = @{ "Authorization" = "Bearer $token" }
Invoke-RestMethod -Uri "http://localhost:5000/api/students/students" -Headers $headers

# 5. اختبار بدون توكن (فشل 401)
Invoke-RestMethod -Uri "http://localhost:5000/api/students/students"
```

---

## أسئلة متوقعة:

### س: ما الخوارزمية المستخدمة؟
> **بالعربي:** "HS256، يعني HMAC-SHA256. خوارزمية توقيع متماثلة."
>
> **In English:** "HS256, meaning HMAC-SHA256. A symmetric signing algorithm."

### س: هل JWT تشفير؟
> **بالعربي:** "لا! JWT توقيع وليس تشفير. الـ Payload مرئية لأي شخص، لكن لا يمكن تعديلها بدون المفتاح."
>
> **In English:** "No! JWT is signing, not encryption. The Payload is visible to anyone, but cannot be modified without the key."

### س: ما فائدة exp؟
> **بالعربي:** "يحدد انتهاء صلاحية التوكن. هنا 24 ساعة."
>
> **In English:** "It sets the token expiration. Here it's 24 hours."

### س: لماذا Stateless أفضل للـ Microservices؟
> **بالعربي:** "لا حاجة لمشاركة session بين الخدمات. كل خدمة تتحقق من التوكن بنفسها."
>
> **In English:** "No need to share sessions between services. Each service verifies the token itself."

### س: ما دور API Gateway؟
> **بالعربي:** "نقطة واحدة للتحقق. الخدمات الداخلية تثق بالـ headers اللي يرسلها."
>
> **In English:** "Single point for validation. Internal services trust the headers it sends."

---

# ════════════════════════════════════════════════════════════════
# ملخص سريع (للمراجعة قبل العرض)
# ════════════════════════════════════════════════════════════════

| المطلب | النمط | الملف الرئيسي | ماذا يفعل |
|--------|-------|--------------|-----------|
| **1** | Circuit Breaker | `common\circuit_breaker.py` | يحمي من الانهيار المتتالي |
| **2** | Strategy + Reflection | `reporting-service\strategy_factory.py` | يبدّل صيغ التقارير ديناميكياً |
| **3** | Choreography | `common\rabbitmq_client.py` | تواصل غير متزامن عبر Events |
| **4** | JWT Auth | `auth-service\app.py` | توثيق بدون session |

---

# الروابط السريعة

| الخدمة | الرابط |
|--------|--------|
| Dashboard | http://localhost:3000 |
| API Gateway | http://localhost:5000 |
| RabbitMQ | http://localhost:15672 (guest/guest) |
| Auth Service | http://localhost:5007 |

---

# أوامر التشغيل

```powershell
# تشغيل
.\START.ps1

# إيقاف
.\STOP.ps1

# فحص صحة النظام
Invoke-RestMethod -Uri "http://localhost:5000/api/health"
```

---

**بالتوفيق في العرض!** 🎓
