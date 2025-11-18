# 🗄️ Database Setup Guide
# دليل إعداد قاعدة البيانات

## ⚠️ Current Issue / المشكلة الحالية

User `ai_agent` doesn't have CREATE TABLE permissions on PostgreSQL.  
المستخدم `ai_agent` ليس لديه صلاحيات إنشاء جداول في PostgreSQL.

**Error:**
```
permission denied for schema public
```

---

## ✅ Solution / الحل

You need to run SQL scripts with **superuser** (e.g., `postgres`) to grant permissions.  
تحتاج إلى تشغيل ملفات SQL باستخدام **superuser** (مثل `postgres`) لمنح الصلاحيات.

---

## 📝 Step-by-Step Instructions / الخطوات التفصيلية

### Option 1: Grant Permissions (Recommended) / الخيار الأول: منح الصلاحيات (موصى به)

**1. Connect to PostgreSQL as superuser:**  
اتصل بـ PostgreSQL كـ superuser:

```bash
psql -h 93.127.142.144 -p 5432 -U postgres -d ai_system_db
```

**2. Run the permissions script:**  
شغّل سكربت الصلاحيات:

```bash
\i dev_platform/web/setup_permissions.sql
```

Or / أو:

```bash
psql -h 93.127.142.144 -p 5432 -U postgres -d ai_system_db -f dev_platform/web/setup_permissions.sql
```

**3. Verify permissions:**  
تحقق من الصلاحيات:

```sql
SELECT schema_name, schema_owner 
FROM information_schema.schemata 
WHERE schema_name IN ('app', 'public');
```

**4. Run the admin creation script:**  
شغّل سكربت إنشاء المسؤول:

```bash
# Method 1: Interactive input (RECOMMENDED - most secure)
python -m dev_platform.web.create_admin

# Method 2: Using environment variables
ADMIN_EMAIL="your-email@example.com" ADMIN_PASSWORD="your-secure-password" python -m dev_platform.web.create_admin

# Method 3: Using SecretsManager (set these first)
python -c "from dev_platform.core.secrets_manager import get_secrets_manager; sm = get_secrets_manager(); sm.set('ADMIN_EMAIL', 'your-email@example.com', encrypt=True); sm.set('ADMIN_PASSWORD', 'your-secure-password', encrypt=True)"
python -m dev_platform.web.create_admin
```

---

### Option 2: Create Tables Manually / الخيار الثاني: إنشاء الجداول يدوياً

If you cannot grant permissions, create tables manually:  
إذا لم تستطع منح الصلاحيات، أنشئ الجداول يدوياً:

**1. Connect to PostgreSQL as superuser:**  
اتصل بـ PostgreSQL كـ superuser:

```bash
psql -h 93.127.142.144 -p 5432 -U postgres -d ai_system_db
```

**2. Run the table creation script:**  
شغّل سكربت إنشاء الجداول:

```bash
\i dev_platform/web/create_tables.sql
```

Or / أو:

```bash
psql -h 93.127.142.144 -p 5432 -U postgres -d ai_system_db -f dev_platform/web/create_tables.sql
```

**3. Create admin user manually:**  
أنشئ حساب المسؤول يدوياً:

```sql
-- Hash the password first using Python:
-- python -c "from passlib.context import CryptContext; pwd_context = CryptContext(schemes=['argon2', 'pbkdf2_sha256'], deprecated='auto'); print(pwd_context.hash('Ay**772283228'))"

INSERT INTO users (email, password_hash, role, is_active)
VALUES (
    'binarjoinanalytic@gmail.com',
    '<HASHED_PASSWORD_FROM_ABOVE>',
    'admin',
    TRUE
);
```

---

## 🔑 Admin Credentials / بيانات اعتماد المسؤول

⚠️ **SECURITY NOTE:**  
For security reasons, admin credentials are **NOT stored in this file**.  
لأسباب أمنية، بيانات اعتماد المسؤول **غير مخزنة في هذا الملف**.

**How to set admin credentials:**  
**كيفية تعيين بيانات اعتماد المسؤول:**

1. Run `python -m dev_platform.web.create_admin` and enter credentials interactively  
   شغّل `python -m dev_platform.web.create_admin` وأدخل البيانات بشكل تفاعلي

2. Or use environment variables (see above)  
   أو استخدم متغيرات البيئة (انظر أعلاه)

3. Or store in SecretsManager (see above)  
   أو احفظها في SecretsManager (انظر أعلاه)

---

## 🧪 Verify Setup / التحقق من الإعداد

**1. Check if table exists:**  
تحقق من وجود الجدول:

```sql
SELECT * FROM users;
```

**2. Test login:**  
اختبر تسجيل الدخول:

```bash
# Start web dashboard
python -m dev_platform.web.web_dashboard

# Open browser: http://localhost:5000
# Login with email and password above
```

---

## 🔒 Security Notes / ملاحظات أمنية

⚠️ **IMPORTANT:**
1. Change the admin password after first login  
   غيّر كلمة مرور المسؤول بعد أول تسجيل دخول

2. Never commit passwords to git  
   لا تحفظ كلمات المرور في git

3. Use environment variables or SecretsManager for sensitive data  
   استخدم متغيرات البيئة أو SecretsManager للبيانات الحساسة

---

## 📞 Support / الدعم

If you encounter issues, check:  
إذا واجهت مشاكل، تحقق من:

1. PostgreSQL is running  
   PostgreSQL يعمل

2. Firewall allows connection to port 5432  
   جدار الحماية يسمح بالاتصال على المنفذ 5432

3. Credentials are correct  
   بيانات الاعتماد صحيحة

4. User has necessary permissions  
   المستخدم لديه الصلاحيات اللازمة

---

**Last Updated:** 2025-11-16  
**Version:** 1.0
