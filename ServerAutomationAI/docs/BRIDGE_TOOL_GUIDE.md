# Bridge Tool - دليل الاستخدام الكامل

## 📚 نظرة عامة

**Bridge Tool** هي أداة CLI متكاملة تربط بين بيئة التطوير على Replit والسيرفر الإنتاجي الخارجي. توفر الأداة:
- نشر آلي للكود
- مزامنة ثنائية الاتجاه
- اختبار عن بُعد
- نظام Rollback ذكي
- مراقبة الحالة

---

## 🚀 البداية السريعة

### 1. التثبيت والإعداد

```bash
# تثبيت المكتبات المطلوبة
pip install paramiko pyyaml

# إنشاء ملف الإعداد
python3 bridge_tool/cli.py init

# تحرير الإعدادات
nano bridge.config.yaml
```

### 2. إعداد bridge.config.yaml

```yaml
server:
  host: "your-server-ip"
  port: 22
  username: "your-username"
  auth_method: "key"  # أو "password"
  key_path: "~/.ssh/id_rsa"

paths:
  remote:
    base: "/srv/ai_system"
    releases: "/srv/ai_system/releases"
    current: "/srv/ai_system/current"
```

### 3. اختبار الاتصال

```bash
python3 bridge_tool/cli.py test
```

---

## 📋 الأوامر المتاحة

### `init` - التهيئة الأولية

إنشاء ملف الإعداد من النموذج.

```bash
python3 bridge_tool/cli.py init
```

---

### `push` - النشر

نشر الكود إلى سيرفر الإنتاج.

```bash
# اختبار بدون تغييرات فعلية (Dry Run)
python3 bridge_tool/cli.py push --dry-run

# نشر فعلي
python3 bridge_tool/cli.py push

# نشر بدون نسخ احتياطي
python3 bridge_tool/cli.py push --skip-backup

# نشر بدون تحقق
python3 bridge_tool/cli.py push --skip-verify
```

**ما يحدث أثناء النشر:**
1. إنشاء مجلد إصدار جديد (`release_YYYYMMDD_HHMMSS`)
2. نسخ احتياطي قبل النشر (إذا لم يتم تعطيله)
3. نقل الملفات إلى السيرفر
4. تشغيل سكريبتات ما بعد النشر
5. تحديث symlink `current` للإشارة إلى الإصدار الجديد
6. حذف الإصدارات القديمة (الاحتفاظ بآخر 5)
7. التحقق من نجاح النشر

---

### `pull` - جلب البيانات

جلب السجلات أو النسخ الاحتياطية أو الإعدادات من السيرفر.

```bash
# جلب السجلات
python3 bridge_tool/cli.py pull logs

# جلب النسخ الاحتياطية
python3 bridge_tool/cli.py pull backups

# جلب ملفات الإعداد
python3 bridge_tool/cli.py pull configs

# تحديد مجلد الوجهة
python3 bridge_tool/cli.py pull logs --output ./my_logs
```

---

### `status` - فحص الحالة

فحص حالة النظام على السيرفر.

```bash
# حالة أساسية
python3 bridge_tool/cli.py status

# حالة مفصلة
python3 bridge_tool/cli.py status --detailed
```

**ما يتم فحصه:**
- حالة الخدمة (systemd)
- حالة الوكلاء الستة
- مساحة القرص
- السجلات الأخيرة
- اتصال قاعدة البيانات
- معلومات النظام (في الوضع المفصل)

---

### `exec` - تنفيذ أوامر

تشغيل أمر على السيرفر مباشرة.

```bash
# تنفيذ أمر
python3 bridge_tool/cli.py exec "python3 main.py status"

# تنفيذ مع timeout مخصص (بالثواني)
python3 bridge_tool/cli.py exec "python3 agents/backup_recovery.py" --timeout 300
```

**أمثلة مفيدة:**
```bash
# إعادة تشغيل الخدمة
python3 bridge_tool/cli.py exec "systemctl restart ai_agents"

# فحص الوكلاء
python3 bridge_tool/cli.py exec "python3 main.py status"

# عرض استخدام الموارد
python3 bridge_tool/cli.py exec "top -bn1 | head -20"
```

---

### `rollback` - التراجع

التراجع إلى إصدار سابق.

```bash
# عرض الإصدارات المتاحة
python3 bridge_tool/cli.py rollback --list

# التراجع إلى الإصدار السابق مباشرة
python3 bridge_tool/cli.py rollback

# التراجع إلى إصدار محدد
python3 bridge_tool/cli.py rollback --release release_20231115_143022
```

**آلية Rollback:**
1. إيقاف الخدمة
2. تحديث symlink `current` للإشارة إلى الإصدار المطلوب
3. إعادة تشغيل الخدمة
4. التحقق من نجاح العملية

---

### `test` - اختبار الاتصال

اختبار شامل للاتصال والإعدادات.

```bash
python3 bridge_tool/cli.py test
```

**ما يتم اختباره:**
- صحة ملف الإعداد
- اتصال SSH
- صلاحيات الوصول
- وجود المجلدات المطلوبة
- صلاحيات الكتابة
- توفر الأدوات المطلوبة (git, pip3, systemctl)

---

## 🔧 الإعدادات المتقدمة

### مثال إعداد كامل

```yaml
# Server Configuration
server:
  host: "192.168.1.100"
  port: 22
  username: "deployer"
  auth_method: "key"
  key_path: "~/.ssh/deploy_key"

# Deployment Paths
paths:
  remote:
    base: "/srv/ai_system"
    releases: "/srv/ai_system/releases"
    current: "/srv/ai_system/current"
    shared: "/srv/ai_system/shared"
    backups: "/srv/ai_system/backups"
  
  local:
    root: "."
    exclude_file: ".bridgeignore"

# Deployment Settings
deployment:
  service_name: "ai_agents"
  keep_releases: 5
  timeout:
    connect: 30
    transfer: 600
    command: 120
  
  verify:
    enabled: true
    checks:
      - "service_status"
      - "log_check"
      - "health_endpoint"

# Pre/Post Deployment Scripts
scripts:
  pre_deploy:
    - name: "Validate Config"
      command: "python3 -c 'import yaml; yaml.safe_load(open(\"configs/config.yaml\"))'"
  
  post_deploy:
    - name: "Install Dependencies"
      command: "pip3 install -r requirements.txt"
    
    - name: "Restart Service"
      command: "systemctl restart ai_agents"
```

---

## 📂 ملف .bridgeignore

استبعاد ملفات من النشر (مثل .gitignore):

```
# Development environment
.replit
.pythonlibs/
bridge_tool/
bridge.config.yaml

# Python cache
__pycache__/
*.pyc

# Logs (will be synced separately)
logs/*.log

# Version control
.git/

# Tests
tests/
*_test.py
```

---

## 🔐 الأمان

### استخدام SSH Keys (موصى به)

```bash
# إنشاء SSH key
ssh-keygen -t rsa -b 4096 -C "deploy@ai-system"

# نسخ المفتاح إلى السيرفر
ssh-copy-id -i ~/.ssh/id_rsa.pub user@server

# استخدام في bridge.config.yaml
server:
  auth_method: "key"
  key_path: "~/.ssh/id_rsa"
```

### استخدام Replit Secrets

```yaml
# في bridge.config.yaml
server:
  password: "${SSH_PASSWORD}"

notifications:
  telegram:
    bot_token: "${TELEGRAM_BOT_TOKEN}"
```

ثم أضف المتغيرات في Replit Secrets:
- `SSH_PASSWORD`
- `TELEGRAM_BOT_TOKEN`

---

## 🔄 سير العمل المقترح

### 1. التطوير على Replit

```bash
# تعديل الكود...
nano agents/ai_manager.py

# اختبار محلي
python3 agents/ai_manager.py

# التحقق من التغييرات
git status
```

### 2. الاختبار قبل النشر

```bash
# اختبار الاتصال
python3 bridge_tool/cli.py test

# تجربة نشر وهمي
python3 bridge_tool/cli.py push --dry-run
```

### 3. النشر الفعلي

```bash
# النشر
python3 bridge_tool/cli.py push

# التحقق من الحالة
python3 bridge_tool/cli.py status
```

### 4. المراقبة والصيانة

```bash
# فحص السجلات
python3 bridge_tool/cli.py pull logs

# فحص الحالة
python3 bridge_tool/cli.py status --detailed
```

### 5. التراجع عند الحاجة

```bash
# عرض الإصدارات
python3 bridge_tool/cli.py rollback --list

# التراجع
python3 bridge_tool/cli.py rollback
```

---

## 🐛 حل المشاكل

### مشكلة: فشل الاتصال SSH

```bash
# اختبار الاتصال يدوياً
ssh user@server

# فحص المفتاح
ssh-keygen -y -f ~/.ssh/id_rsa

# التحقق من الصلاحيات
chmod 600 ~/.ssh/id_rsa
chmod 700 ~/.ssh
```

### مشكلة: فشل نقل الملفات

```bash
# فحص المساحة على السيرفر
python3 bridge_tool/cli.py exec "df -h"

# فحص الصلاحيات
python3 bridge_tool/cli.py exec "ls -la /srv/ai_system"
```

### مشكلة: فشل الخدمة بعد النشر

```bash
# فحص حالة الخدمة
python3 bridge_tool/cli.py exec "systemctl status ai_agents"

# فحص السجلات
python3 bridge_tool/cli.py exec "journalctl -u ai_agents -n 50"

# التراجع للإصدار السابق
python3 bridge_tool/cli.py rollback
```

---

## 📊 أمثلة عملية

### مثال 1: نشر تحديث جديد

```bash
# 1. اختبار النشر
python3 bridge_tool/cli.py push --dry-run

# 2. النشر الفعلي
python3 bridge_tool/cli.py push

# 3. التحقق
python3 bridge_tool/cli.py status

# 4. جلب السجلات للمراجعة
python3 bridge_tool/cli.py pull logs
```

### مثال 2: صيانة دورية

```bash
# فحص الحالة
python3 bridge_tool/cli.py status --detailed

# جلب السجلات
python3 bridge_tool/cli.py pull logs --output ./logs_$(date +%Y%m%d)

# جلب النسخ الاحتياطية
python3 bridge_tool/cli.py pull backups
```

### مثال 3: طوارئ - التراجع السريع

```bash
# التراجع فوراً
python3 bridge_tool/cli.py rollback

# التحقق من الحالة
python3 bridge_tool/cli.py status

# إعادة تشغيل الخدمة
python3 bridge_tool/cli.py exec "systemctl restart ai_agents"
```

---

## 🎯 أفضل الممارسات

1. **اختبر دائماً قبل النشر:**
   ```bash
   python3 bridge_tool/cli.py push --dry-run
   ```

2. **راقب الحالة بعد النشر:**
   ```bash
   python3 bridge_tool/cli.py status --detailed
   ```

3. **احتفظ بنسخ احتياطية:**
   - لا تستخدم `--skip-backup` إلا للضرورة
   - اجلب النسخ الاحتياطية دورياً

4. **استخدم SSH Keys بدلاً من كلمات المرور**

5. **راجع `.bridgeignore` بانتظام:**
   - تأكد من استبعاد الملفات غير الضرورية
   - قلل حجم النقل

6. **حدد timeout مناسب للأوامر الطويلة**

7. **استخدم Rollback عند الحاجة:**
   - لا تخف من التراجع إذا ظهرت مشاكل
   - الإصدارات القديمة محفوظة

---

## 📞 الدعم

للمساعدة أو الإبلاغ عن مشاكل:
1. راجع قسم حل المشاكل أعلاه
2. فحص السجلات في `bridge_reports/bridge.log`
3. راجع PROGRESS.md للتوثيق الكامل

---

**تم إنشاؤه بواسطة:** AI Multi-Agent Team  
**الإصدار:** 1.0.0  
**آخر تحديث:** 2025-11-14
