# دليل اختبار المشروع بـ Postman

## المحتويات
1. [Strategy Pattern + Reflection](#1-strategy-pattern--reflection)
2. [Circuit Breaker](#2-circuit-breaker)
3. [RabbitMQ Choreography](#3-rabbitmq-choreography)

---

## 1. Strategy Pattern + Reflection

### أ) تقرير طالب بصيغة Excel (الافتراضية)

**طريقة:** GET
**رابط:**
```
http://localhost:5009/api/reports/student/STU001?course_id=CS101
```

**النتيجة المتوقعة:** تحميل ملف Excel

---

### ب) تقرير طالب بصيغة PDF

**طريقة:** GET
**رابط:**
```
http://localhost:5009/api/reports/student/STU001?course_id=CS101&format=pdf
```

**النتيجة المتوقعة:** تحميل ملف PDF

---

### ج) تقرير طالب بصيغة CSV (الصيغة الجديدة - Open/Closed)

**طريقة:** GET
**رابط:**
```
http://localhost:5009/api/reports/student/STU001?course_id=CS101&format=csv
```

**النتيجة المتوقعة:** تحميل ملف CSV

---

### د) تقرير مقرر كامل بصيغة Excel

**طريقة:** GET
**رابط:**
```
http://localhost:5009/api/reports/course/CS101
```

**النتيجة المتوقعة:** تحميل ملف Excel بجميع الطلاب

---

### هـ) تقرير مقرر بصيغة CSV

**طريقة:** GET
**رابط:**
```
http://localhost:5009/api/reports/course/CS101?format=csv
```

**النتيجة المتوقعة:** تحميل ملف CSV بمصفوفة حضور

---

### و) الحصول على الصيغ المتاحة (Reflection Demo)

**طريقة:** GET
**رابط:**
```
http://localhost:5009/api/reports/formats
```

**ملاحظة:** إذا لم يوجد endpoint، يمكن رؤية القائمة في `config/report_config.yml`

---

## 2. Circuit Breaker

### أ) فحص حالة Circuit Breaker

**طريقة:** GET
**رابط:**
```
http://localhost:5004/api/pdf/cb-status
```

**النتيجة المتوقعة:**
```json
{
  "service": "PDF Processing Service",
  "circuit_breaker": {
    "state": "closed",
    "failure_count": 0,
    "threshold": 3,
    "timeout": 30
  },
  "target_service": "Attendance Service (port 5005)",
  "status": "healthy"
}
```

**الحالات الممكنة:**
- `closed` - النظام يعمل بشكل طبيعي
- `open` - Circuit Breaker مفتوح (رفض الطلبات)
- `half_open` - في وضع الاختبار

---

### ب) اختبار Circuit Breaker يدوياً

**طريقة:** POST
**رابط:**
```
http://localhost:5004/api/pdf/test-cb
```

**Body (JSON):**
```json
{
  "simulate_failure": true
}
```

**النتيجة المتوقعة:**
```json
{
  "test": "circuit_breaker",
  "result": "failure_simulated",
  "circuit_state": "open",
  "message": "Circuit breaker opened after 3 failures"
}
```

---

### ج) سيناريو كامل - فتح Circuit Breaker

**الخطوات:**

1. **إيقاف Attendance Service:**
   ```powershell
   # في نافذة PowerShell منفصلة
   Stop-Process -Name "python" -Force | Where-Object {$_.CommandLine -like "*attendance-service*"}
   ```

2. **محاولة رفع ملف PDF (سيفشل 3 مرات):**

   **طريقة:** POST
   **رابط:** `http://localhost:5004/api/pdf/process`
   **Body:** Form-data
   - Key: `file`
   - Value: اختر ملف PDF

   **كرر الطلب 3 مرات** → Circuit Breaker سيفتح

3. **فحص الحالة:**
   ```
   GET http://localhost:5004/api/pdf/cb-status
   ```

   **النتيجة:**
   ```json
   {
     "circuit_breaker": {
       "state": "open",
       "failure_count": 3
     }
   }
   ```

4. **إعادة تشغيل Attendance Service:**
   ```powershell
   cd attendance-service
   python app.py
   ```

5. **انتظر 30 ثانية** → CB سينتقل إلى `half_open` → بعد طلب ناجح سيغلق

---

## 3. RabbitMQ Choreography

### أ) تسجيل حضور (يُرسل رسالة RabbitMQ)

**طريقة:** POST
**رابط:**
```
http://localhost:5005/api/attendance
```

**Body (JSON):**
```json
{
  "student_id": "STU001",
  "course_id": "CS101",
  "lecture_id": "LEC001",
  "status": "present"
}
```

**النتيجة المتوقعة:**
```json
{
  "message": "Attendance recorded successfully",
  "attendance_id": "ATT123456",
  "event_published": true,
  "event_queue": "attendance_events"
}
```

**ماذا يحدث في الخلفية:**
1. Attendance Service يحفظ السجل في قاعدة البيانات
2. يُنشر event إلى RabbitMQ (queue: `attendance_events`)
3. Course Service يستهلك الرسالة تلقائياً
4. Course Service يُحدّث إحصائيات الحضور

---

### ب) التحقق من استهلاك الرسالة

**طريقة 1: RabbitMQ Management UI**
1. افتح: http://localhost:15672
2. تسجيل الدخول: `guest` / `guest`
3. اذهب إلى **Queues** → `attendance_events`
4. سترى:
   - **Ready:** 0 (لا توجد رسائل معلقة)
   - **Total Messages Published:** عدد الرسائل المُرسلة
   - **Total Messages Consumed:** عدد الرسائل المستهلكة

**طريقة 2: Course Service Logs**
```powershell
# اذهب إلى نافذة Course Service PowerShell
# سترى:
[Course Service] تم استلام event من RabbitMQ
[Course Service] Event Type: attendance_recorded
[Course Service] Student: STU001, Course: CS101
```

---

### ج) الحصول على سجل Events (من Course Service)

**طريقة:** GET
**رابط:**
```
http://localhost:5002/api/courses/attendance-events
```

**النتيجة المتوقعة:**
```json
{
  "service": "Course Service",
  "events_received": [
    {
      "event_type": "attendance_recorded",
      "student_id": "STU001",
      "course_id": "CS101",
      "timestamp": "2026-02-04T10:30:00Z"
    }
  ],
  "total_events": 1
}
```

---

## 4. نصائح مهمة

### تنظيم Postman

1. أنشئ **Collection** اسمها: "Smart Attendance System"
2. أنشئ **Folders:**
   - Strategy Pattern (Reports)
   - Circuit Breaker (Testing)
   - RabbitMQ (Choreography)
   - Other Services (CRUD operations)

### Variables مفيدة

أضف **Environment Variables** في Postman:
- `base_url` = `http://localhost:5000`
- `reporting_url` = `http://localhost:5009`
- `pdf_url` = `http://localhost:5004`
- `attendance_url` = `http://localhost:5005`
- `course_url` = `http://localhost:5002`

ثم استخدم: `{{reporting_url}}/api/reports/course/CS101`

---

## 5. سيناريو العرض التقديمي الكامل

### للمشرف (7 فبراير):

**1. Strategy Pattern (دقيقة 1-2)**
- افتح Postman
- اعرض تقرير Excel: `GET /api/reports/course/CS101`
- اعرض تقرير CSV: `GET /api/reports/course/CS101?format=csv`
- **النقطة الأكاديمية:** "أضفنا CSV بدون تعديل endpoints - Open/Closed Principle"

**2. Reflection (دقيقة 3)**
- افتح `config/report_config.yml`
- غيّر `default_format` من `excel` إلى `csv`
- أعد تشغيل Reporting Service
- جرب: `GET /api/reports/course/CS101` (بدون `format` parameter)
- **النتيجة:** سيُرجع CSV (التحميل الديناميكي عبر Reflection)

**3. Circuit Breaker (دقيقة 4-6)**
- اعرض حالة CB: `GET /api/pdf/cb-status` → `closed`
- أوقف Attendance Service
- حاول رفع PDF 3 مرات → فشل
- اعرض الحالة: `GET /api/pdf/cb-status` → `open`
- **النقطة الأكاديمية:** "State Pattern: CLOSED → OPEN بعد 3 فشلات"

**4. RabbitMQ Choreography (دقيقة 7-9)**
- افتح RabbitMQ UI: http://localhost:15672
- سجل حضور: `POST /api/attendance`
- **أعرض مباشرة:** queue في RabbitMQ → Message consumed
- **أعرض:** Course Service logs → event استلام
- **النقطة الأكاديمية:** "Choreography: لا يوجد orchestrator - كل خدمة تعرف دورها"

**5. الخاتمة (دقيقة 10)**
- "كل شيء حقيقي، ليس simulation"
- "كل pattern متصل بوظائف حقيقية في النظام"
- "Open/Closed, State Pattern, Event-Driven Architecture"

---

## 6. إجابات متوقعة لأسئلة المشرف

### س: "أين Circuit Breaker؟"
**ج:** في PDF Processing Service (client-side) عند الاتصال بـ Attendance Service. موقع واقعي لأن PDF Processing يحتاج لحفظ الحضور.

### س: "لماذا Strategy Pattern في Reports؟"
**ج:** لأن التقارير لها صيغ متعددة (Excel, PDF, CSV). Strategy Pattern + Reflection يسمح بإضافة صيغة جديدة بدون تعديل كود endpoints.

### س: "ما فائدة Reflection؟"
**ج:** يمكن تغيير الصيغة الافتراضية من config.yml بدون إعادة برمجة. الاستراتيجية تُحمّل ديناميكياً بـ importlib + getattr.

### س: "كيف RabbitMQ choreography؟"
**ج:** Attendance Service يُنشر event → Course Service يستهلك ويُحدّث إحصائيات. لا يوجد orchestrator مركزي - كل خدمة مستقلة.

### س: "هل هذا simulation؟"
**ج:** لا، كل شيء حقيقي. يمكنك رؤية:
- RabbitMQ Management UI (messages حقيقية)
- Circuit Breaker state changes (حالات حقيقية)
- Reports downloaded (ملفات حقيقية)

---

## 7. Troubleshooting

### المشكلة: "Connection refused"
**الحل:** تأكد من تشغيل جميع الخدمات بـ `.\START.ps1`

### المشكلة: "RabbitMQ queue not found"
**الحل:**
```powershell
# إعادة تشغيل RabbitMQ
rabbitmq-service stop
rabbitmq-service start
```

### المشكلة: "Circuit Breaker لا يفتح"
**الحل:** تأكد من:
1. Attendance Service متوقف فعلاً
2. كررت الطلب 3 مرات على الأقل
3. انتظر بين الطلبات (لا تكررها بسرعة شديدة)

---

## انتهى الدليل

**الملخص:**
- تشغيل: `.\START.ps1`
- إيقاف: `.\STOP.ps1`
- Dashboard: http://localhost:5000
- RabbitMQ UI: http://localhost:15672
- جميع الطلبات موثقة أعلاه

**للمشرف:** كل شيء حقيقي، قابل للاختبار، ومتصل بوظائف النظام الفعلية.
