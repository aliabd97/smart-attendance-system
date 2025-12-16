# 📚 دليل تسجيل الطلاب في المواد

## ⚠️ مهم جداً: يجب تسجيل الطلاب في المادة قبل إنشاء Bubble Sheet!

---

## الخطوات المطلوبة:

### 1. ✅ إضافة طلاب
1. اذهب إلى **Dashboard → Students**
2. اضغط **Add Student**
3. أدخل البيانات:
   - Student ID: مثل `S001`
   - Name: مثل `أحمد علي`
   - Email: مثل `ahmed@university.edu`
   - Department: مثل `Computer Science`
4. اضغط **Add Student**

**كرر العملية** لإضافة 5-10 طلاب على الأقل.

### 2. ✅ إضافة مادة
1. اذهب إلى **Dashboard → Courses**
2. اضغط **Add Course**
3. أدخل البيانات:
   - Course Code: مثل `CS101`
   - Course Name: مثل `Introduction to Programming`
   - Instructor: مثل `د. محمد أحمد`
   - Department: مثل `Computer Science`
4. اضغط **Add Course**

### 3. ⚠️ تسجيل الطلاب في المادة (مطلوب!)

**حالياً، يجب تسجيل الطلاب عبر API مباشرة:**

افتح Terminal/PowerShell وقم بتنفيذ:

```powershell
# احصل على الـ Token أولاً (من localStorage في المتصفح)
# افتح Developer Tools → Console → اكتب:
# localStorage.getItem('token')

# ثم استخدمه في الطلب:
$token = "YOUR_TOKEN_HERE"

# تسجيل طالب في مادة
Invoke-RestMethod -Method POST `
  -Uri "http://localhost:5000/api/courses/CS101/students/S001" `
  -Headers @{"Authorization"="Bearer $token"}

# كرر لكل طالب:
Invoke-RestMethod -Method POST `
  -Uri "http://localhost:5000/api/courses/CS101/students/S002" `
  -Headers @{"Authorization"="Bearer $token"}

Invoke-RestMethod -Method POST `
  -Uri "http://localhost:5000/api/courses/CS101/students/S003" `
  -Headers @{"Authorization"="Bearer $token"}
```

**أو باستخدام cURL:**

```bash
# احصل على الـ Token
TOKEN="YOUR_TOKEN_HERE"

# تسجيل الطلاب
curl -X POST http://localhost:5000/api/courses/CS101/students/S001 \
  -H "Authorization: Bearer $TOKEN"

curl -X POST http://localhost:5000/api/courses/CS101/students/S002 \
  -H "Authorization: Bearer $TOKEN"

curl -X POST http://localhost:5000/api/courses/CS101/students/S003 \
  -H "Authorization: Bearer $TOKEN"
```

### 4. ✅ إنشاء Bubble Sheet

الآن يمكنك:
1. اذهب إلى **Dashboard → Bubble Sheets**
2. أدخل Course ID: `CS101`
3. أدخل Lecture ID: `L001`
4. اختر التاريخ
5. اضغط **Generate PDF**

✅ **سيعمل الآن بنجاح!**

---

## 🔧 حل سريع: تسجيل جماعي

إذا كان لديك عدة طلاب، استخدم هذا السكريبت:

```powershell
# احصل على الـ Token من المتصفح
$token = "YOUR_TOKEN_HERE"

# قائمة الطلاب
$students = @("S001", "S002", "S003", "S004", "S005")

# تسجيل كل الطلاب في CS101
foreach ($studentId in $students) {
    Write-Host "Enrolling $studentId..."
    Invoke-RestMethod -Method POST `
      -Uri "http://localhost:5000/api/courses/CS101/students/$studentId" `
      -Headers @{"Authorization"="Bearer $token"} `
      -ErrorAction SilentlyContinue
}

Write-Host "Done! All students enrolled."
```

---

## 📝 ملاحظة مهمة:

**في النسخة المستقبلية**، سنضيف واجهة UI لتسجيل الطلاب في المواد مباشرة من Dashboard.

حالياً، استخدم الطريقة أعلاه عبر API.

---

## ✅ كيف أتحقق من نجاح التسجيل؟

افتح المتصفح على:
```
http://localhost:5000/api/courses/CS101/students
```

يجب أن ترى قائمة بالطلاب المسجلين.

---

**بعد إتمام هذه الخطوات، يمكنك توليد Bubble Sheets بنجاح! 🎉**
