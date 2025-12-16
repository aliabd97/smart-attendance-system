# دليل التشغيل المحلي - Smart Attendance System

## المتطلبات الأساسية

### 1. تثبيت Python
- Python 3.11 أو أحدث
- تحقق من التثبيت:
```bash
python --version
```

### 2. تثبيت Node.js
- Node.js 18 أو أحدث
- تحقق من التثبيت:
```bash
node --version
npm --version
```

---

## خطوات التشغيل الكامل

### الخطوة 1: تثبيت مكتبات Python لجميع الخدمات

افتح PowerShell في مجلد المشروع ونفذ:

```powershell
# Student Service
cd student-service
pip install -r requirements.txt
cd ..

# Course Service
cd course-service
pip install -r requirements.txt
cd ..

# Attendance Service
cd attendance-service
pip install -r requirements.txt
cd ..

# Auth Service
cd auth-service
pip install -r requirements.txt
cd ..

# Service Registry
cd service-registry
pip install -r requirements.txt
cd ..

# Bubble Sheet Generator
cd bubble-sheet-generator
pip install -r requirements.txt
cd ..

# PDF Processing Service
cd pdf-processing-service
pip install -r requirements.txt
cd ..

# Reporting Service
cd reporting-service
pip install -r requirements.txt
cd ..

# API Gateway
cd api-gateway
pip install -r requirements.txt
cd ..
```

**أو استخدم سكريبت واحد (سأنشئه لك)**

### الخطوة 2: إنشاء ملفات .env للخدمات

```powershell
# في مجلد المشروع الرئيسي
# الملفات .env موجودة كـ .env.example، انسخها

# أو سأنشئ لك سكريبت لهذا
```

### الخطوة 3: تشغيل جميع الخدمات Backend

**يجب فتح 9 نوافذ PowerShell منفصلة:**

**نافذة 1 - Student Service:**
```powershell
cd "c:\Users\HP\smart-attendance-system\student-service"
python app.py
```

**نافذة 2 - Course Service:**
```powershell
cd "c:\Users\HP\smart-attendance-system\course-service"
python app.py
```

**نافذة 3 - Attendance Service:**
```powershell
cd "c:\Users\HP\smart-attendance-system\attendance-service"
python app.py
```

**نافذة 4 - Auth Service:**
```powershell
cd "c:\Users\HP\smart-attendance-system\auth-service"
python app.py
```

**نافذة 5 - Service Registry:**
```powershell
cd "c:\Users\HP\smart-attendance-system\service-registry"
python app.py
```

**نافذة 6 - Bubble Sheet Generator:**
```powershell
cd "c:\Users\HP\smart-attendance-system\bubble-sheet-generator"
python app.py
```

**نافذة 7 - PDF Processing Service:**
```powershell
cd "c:\Users\HP\smart-attendance-system\pdf-processing-service"
python app.py
```

**نافذة 8 - Reporting Service:**
```powershell
cd "c:\Users\HP\smart-attendance-system\reporting-service"
python app.py
```

**نافذة 9 - API Gateway:**
```powershell
cd "c:\Users\HP\smart-attendance-system\api-gateway"
python app.py
```

### الخطوة 4: تشغيل Frontend Dashboard

**نافذة 10 - Frontend:**
```powershell
cd "c:\Users\HP\smart-attendance-system\admin-dashboard"
npm install
npm run dev
```

---

## التحقق من التشغيل

### Backend Services
افتح المتصفح واذهب إلى:

- Student Service: http://localhost:5001/health
- Course Service: http://localhost:5002/health
- Attendance Service: http://localhost:5006/health
- Auth Service: http://localhost:5007/health
- Service Registry: http://localhost:5008/health
- Bubble Sheet Generator: http://localhost:5003/health
- PDF Processing: http://localhost:5004/health
- Reporting Service: http://localhost:5007/health
- API Gateway: http://localhost:5000/health

### Frontend Dashboard
- Dashboard: http://localhost:3000

---

## تسجيل الدخول

افتح المتصفح واذهب إلى: http://localhost:3000

**معلومات تسجيل الدخول:**
- Username: `admin`
- Password: `admin123`

---

## الترتيب الصحيح للتشغيل

**مهم جداً: شغل الخدمات بهذا الترتيب:**

1. ✅ Service Registry (أولاً)
2. ✅ Auth Service
3. ✅ Student Service
4. ✅ Course Service
5. ✅ Attendance Service
6. ✅ Bubble Sheet Generator
7. ✅ PDF Processing Service
8. ✅ Reporting Service
9. ✅ API Gateway (آخر خدمة backend)
10. ✅ Frontend Dashboard

---

## استكشاف الأخطاء

### مشكلة: "Port already in use"
**الحل:**
```powershell
# اقتل العملية على البورت
netstat -ano | findstr :5001
taskkill /PID [PID_NUMBER] /F
```

### مشكلة: "Module not found"
**الحل:**
```powershell
# تأكد من تثبيت المكتبات
pip install -r requirements.txt
```

### مشكلة: "Connection refused"
**الحل:**
- تأكد من تشغيل الخدمة المطلوبة
- تحقق من رقم البورت الصحيح

### مشكلة: "CORS error" في Frontend
**الحل:**
- تأكد من تشغيل API Gateway على البورت 5000
- تحقق من ملف `.env` في admin-dashboard

---

## إيقاف التشغيل

اضغط `Ctrl + C` في كل نافذة PowerShell لإيقاف الخدمات.

---

## سكريبتات مساعدة (سأنشئها لك)

### 1. install-all.ps1
يثبت جميع المكتبات تلقائياً

### 2. start-all-services.ps1
يشغل جميع الخدمات في نوافذ منفصلة

### 3. stop-all-services.ps1
يوقف جميع الخدمات

### 4. check-services.ps1
يتحقق من حالة جميع الخدمات

---

## ملاحظات مهمة

1. **قواعد البيانات**: تُنشأ تلقائياً عند أول تشغيل لكل خدمة
2. **البيانات التجريبية**: غير موجودة، يجب إضافتها من الـ Dashboard
3. **الملفات المُنشأة**:
   - PDFs في `bubble-sheet-generator/sheets/`
   - Reports في `reporting-service/reports/`
   - Uploaded PDFs في `pdf-processing-service/uploads/`

---

## الخطوات السريعة (بعد التثبيت الأول)

بعد أول مرة، فقط:

1. افتح 10 نوافذ PowerShell
2. شغل الأوامر في كل نافذة حسب الترتيب أعلاه
3. انتظر حتى تظهر "Running on http://..." لكل خدمة
4. افتح http://localhost:3000 في المتصفح
5. ابدأ الاستخدام!

---

## التكامل الكامل - اختبار الـ Workflow

### 1. إضافة طلاب
- اذهب إلى Students → Upload Excel
- أو أضف يدوياً

### 2. إضافة مقررات
- اذهب إلى Courses → Add Course
- سجل الطلاب في المقرر

### 3. إنشاء ورقة حضور
- اذهب إلى Bubble Sheets → Generate
- أدخل بيانات المحاضرة
- حمّل الـ PDF
- اطبعها

### 4. رفع ورقة ممسوحة
- امسح الورقة ضوئياً (PDF)
- اذهب إلى Bubble Sheets → Upload
- ارفع الـ PDF
- شاهد النتائج التلقائية

### 5. إنشاء تقارير
- اذهب إلى Reports
- اختر نوع التقرير
- حمّل Excel أو PDF

---

الآن كل شيء جاهز! 🚀
