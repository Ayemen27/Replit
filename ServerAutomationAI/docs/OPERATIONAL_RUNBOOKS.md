# 📚 Operational Runbooks - كتيبات التشغيل

## نظرة عامة

هذه الوثيقة تحتوي على إجراءات تشغيلية خطوة بخطوة للتعامل مع السيناريوهات الشائعة في **لوحة تحكم الذكاء الاصطناعي**. استخدم هذه الأدلة للاستجابة السريعة للحوادث والصيانة اليومية.

**الأقسام:**
- [🚨 الاستجابة للحوادث](#-الاستجابة-للحوادث)
- [📧 إدارة الإشعارات](#-إدارة-الإشعارات)
- [🔄 استعادة النظام](#-استعادة-النظام)
- [🔧 إجراءات الصيانة](#-إجراءات-الصيانة)
- [📊 المراقبة والتشخيص](#-المراقبة-والتشخيص)
- [🗄️ إدارة قاعدة البيانات](#️-إدارة-قاعدة-البيانات)

---

## 🚨 الاستجابة للحوادث

### 1. وكيل واحد أو أكثر متوقف عن العمل

**الأعراض:**
- رسائل خطأ في السجلات
- تنبيهات حرجة من AI Manager
- واجهة لوحة التحكم تُظهر وكلاء غير نشطين

**الإجراءات:**

```bash
# الخطوة 1: فحص حالة الوكلاء
python main.py status

# الخطوة 2: فحص السجلات للأخطاء
tail -100 logs/ai_manager.log
tail -100 logs/performance_monitor.log
tail -100 logs/security_monitor.log

# الخطوة 3: إعادة تشغيل الوكلاء
sudo systemctl restart ai_agents.service

# الخطوة 4: التحقق من إعادة التشغيل
python main.py status

# الخطوة 5: مراقبة السجلات
tail -f logs/ai_manager.log
```

**التصعيد:**
- إذا استمرت المشكلة بعد 3 محاولات إعادة تشغيل
- إذا كانت قاعدة البيانات لا تستجيب
- إذا كان الخادم نفسه يعاني من مشاكل

**الوقاية:**
- مراقبة دورية كل 5 دقائق
- تنبيهات تلقائية عبر Telegram/Email
- فحوصات صحة منتظمة

---

### 2. استهلاك موارد عالي (CPU/RAM/Disk)

**الأعراض:**
- تنبيهات من Performance Monitor
- بطء في استجابة النظام
- رسائل `Resource Warning` في السجلات

**الإجراءات:**

```bash
# الخطوة 1: تحديد الموارد المستهلكة
python main.py monitor

# الخطوة 2: فحص العمليات
top -u $(whoami)
ps aux | grep python | grep -v grep

# الخطوة 3: فحص استخدام القرص
df -h
du -sh /srv/ai_system/*
du -sh logs/
du -sh backups/

# الخطوة 4: تنظيف الملفات القديمة
# حذف السجلات الدائرية القديمة
find logs/ -name "*.log.*" -mtime +7 -delete

# حذف النسخ الاحتياطية القديمة (>30 يوم)
find backups/ -name "*.sql" -mtime +30 -delete
find backups/ -name "*.tar.gz" -mtime +30 -delete

# الخطوة 5: إعادة تشغيل الوكلاء إذا لزم الأمر
sudo systemctl restart ai_agents.service
```

**الحدود الموصى بها:**
- CPU: تحذير عند >80%، حرج عند >90%
- RAM: تحذير عند >75%، حرج عند >85%
- Disk: تحذير عند >80%، حرج عند >90%

**الوقاية:**
- تدوير السجلات تلقائياً
- نسخ احتياطية مجدولة مع تنظيف تلقائي
- مراقبة استهلاك الموارد بشكل دوري

---

### 3. فشل الاتصال بقاعدة البيانات

**الأعراض:**
- رسائل خطأ في Database Manager logs
- تنبيهات `Database Connection Failed`
- فشل النسخ الاحتياطية

**الإجراءات:**

```bash
# الخطوة 1: فحص حالة PostgreSQL
sudo systemctl status postgresql

# الخطوة 2: فحص الاتصال
psql -h localhost -U ai_system_user -d ai_monitoring -c "SELECT 1;"

# الخطوة 3: إعادة تشغيل PostgreSQL إذا لزم الأمر
sudo systemctl restart postgresql

# الخطوة 4: فحص السجلات
sudo tail -100 /var/log/postgresql/postgresql-16-main.log

# الخطوة 5: استعادة من نسخة احتياطية إذا لزم الأمر
# (راجع قسم استعادة قاعدة البيانات)
```

**التصعيد:**
- إذا استمرت المشكلة بعد إعادة التشغيل
- إذا كانت البيانات تالفة
- إذا كانت هناك مشاكل في القرص

---

### 4. فشل نظام الإشعارات

**الأعراض:**
- لا تصل إشعارات Telegram/Email
- رسائل خطأ في `notification_system.log`
- `health_check()` يُظهر قنوات معطلة

**الإجراءات:**

```bash
# الخطوة 1: فحص صحة نظام الإشعارات
python -c "
from tools.notification_system import NotificationSystem
notifier = NotificationSystem()
health = notifier.health_check()
print('Telegram:', health['telegram'])
print('Email:', health['email'])
"

# الخطوة 2: فحص بيانات الاعتماد
python dev_platform/tools/secrets_cli.py list

# الخطوة 3: اختبار إرسال يدوي
python -c "
from tools.notification_system import NotificationSystem
notifier = NotificationSystem()
result = notifier.send_info('اختبار النظام')
print(result)
"

# الخطوة 4: تحديث بيانات الاعتماد إذا لزم الأمر
python dev_platform/tools/secrets_cli.py set TELEGRAM_BOT_TOKEN --generate
python dev_platform/tools/secrets_cli.py set TELEGRAM_CHAT_ID "YOUR_CHAT_ID"

# الخطوة 5: إعادة تشغيل الوكلاء
sudo systemctl restart ai_agents.service
```

**راجع:** `docs/NOTIFICATION_SYSTEM_GUIDE.md` للمزيد من التفاصيل

---

## 📧 إدارة الإشعارات

### 1. تكوين Telegram

```bash
# الخطوة 1: إنشاء بوت عبر @BotFather
# احصل على bot_token

# الخطوة 2: الحصول على chat_id
# أرسل رسالة للبوت، ثم:
curl "https://api.telegram.org/bot<BOT_TOKEN>/getUpdates"

# الخطوة 3: حفظ البيانات في SecretsManager
python dev_platform/tools/secrets_cli.py set TELEGRAM_BOT_TOKEN "YOUR_BOT_TOKEN"
python dev_platform/tools/secrets_cli.py set TELEGRAM_CHAT_ID "YOUR_CHAT_ID"

# الخطوة 4: التحقق من التكوين
python -c "
from tools.notification_system import NotificationSystem
notifier = NotificationSystem()
notifier.send_info('✅ تم تكوين Telegram بنجاح!')
"
```

---

### 2. تكوين Email

```bash
# الخطوة 1: الحصول على بيانات SMTP
# لـ Gmail: smtp.gmail.com:587 + App Password

# الخطوة 2: حفظ البيانات
python dev_platform/tools/secrets_cli.py set EMAIL_HOST "smtp.gmail.com"
python dev_platform/tools/secrets_cli.py set EMAIL_PORT "587"
python dev_platform/tools/secrets_cli.py set SMTP_USER "your-email@gmail.com"
python dev_platform/tools/secrets_cli.py set SMTP_PASSWORD "your-app-password"
python dev_platform/tools/secrets_cli.py set SUPPORT_EMAIL "admin@example.com"

# الخطوة 3: تفعيل Email في config.yaml
# تأكد من:
# notifications:
#   email:
#     enabled: true

# الخطوة 4: اختبار
python -c "
from tools.notification_system import NotificationSystem
notifier = NotificationSystem()
notifier._send_email('اختبار', 'رسالة اختبارية')
"
```

---

### 3. تعطيل/تفعيل الإشعارات

```bash
# تعطيل مؤقت (بدون تعديل config.yaml)
# عدّل الكود مباشرة:
python -c "
from tools.notification_system import NotificationSystem
notifier = NotificationSystem()
notifier.telegram_config['enabled'] = False
notifier.email_config['enabled'] = False
print('✓ الإشعارات معطلة مؤقتاً')
"

# تعطيل دائم: عدّل configs/config.yaml
# notifications:
#   telegram:
#     enabled: false
#   email:
#     enabled: false
```

---

## 🔄 استعادة النظام

### 1. استعادة من نسخة احتياطية كاملة

```bash
# الخطوة 1: إيقاف الوكلاء
sudo systemctl stop ai_agents.service

# الخطوة 2: اختيار النسخة الاحتياطية
ls -lh backups/database_full_backup_*.sql

# الخطوة 3: استعادة قاعدة البيانات
python src/setup/restore_database.py backups/database_full_backup_YYYYMMDD_HHMMSS.sql

# الخطوة 4: استعادة الإعدادات (إذا لزم الأمر)
tar -xzf backups/configs_backup_YYYYMMDD_HHMMSS.tar.gz -C configs/

# الخطوة 5: استعادة السجلات (اختياري)
tar -xzf backups/logs_backup_YYYYMMDD_HHMMSS.tar.gz -C logs/

# الخطوة 6: إعادة تشغيل الوكلاء
sudo systemctl start ai_agents.service

# الخطوة 7: التحقق
python main.py status
```

**ملاحظة:** راجع `backups/README.md` لمزيد من التفاصيل

---

### 2. التراجع عن نشر (Rollback Deployment)

```bash
# إذا كان النشر الجديد يسبب مشاكل

# الخطوة 1: فحص النسخ المنشورة
ls -l /srv/ai_system/

# الخطوة 2: استخدام Bridge Tool للتراجع
cd bridge_tool
python -m bridge_tool.cli rollback

# الخطوة 3: التحقق من النسخة
python main.py --version

# الخطوة 4: إعادة تشغيل
sudo systemctl restart ai_agents.service
```

**راجع:** `docs/BRIDGE_TOOL_GUIDE.md`

---

### 3. إعادة بناء النظام من الصفر

```bash
# في حالة الفشل الكارثي

# الخطوة 1: النسخ الاحتياطي للبيانات الحالية
tar -czf emergency_backup_$(date +%Y%m%d).tar.gz \
    configs/ backups/ data/ logs/

# الخطوة 2: تنفيذ سكريبت التثبيت
cd src/setup
sudo bash install.sh

# الخطوة 3: استعادة الإعدادات
cp ~/emergency_backup/configs/config.yaml configs/

# الخطوة 4: استعادة قاعدة البيانات
python src/setup/restore_database.py ~/emergency_backup/backups/latest.sql

# الخطوة 5: إعادة تشغيل
sudo systemctl enable ai_agents.service
sudo systemctl start ai_agents.service
```

---

## 🔧 إجراءات الصيانة

### 1. الصيانة اليومية

```bash
# روتين يومي - يمكن جدولته في cron

# فحص حالة النظام
python main.py status

# فحص صحة قاعدة البيانات
python main.py monitor --database

# تنظيف السجلات القديمة (>7 أيام)
find logs/ -name "*.log.*" -mtime +7 -delete

# فحص المساحة المتاحة
df -h

# مراجعة آخر 50 رسالة في Event Bus
python -c "
from tools.agent_communication import get_communication_system
comm = get_communication_system()
history = comm.get_message_history(limit=50)
for msg in history[-10:]:
    print(f\"{msg['timestamp']}: {msg['sender']} -> {msg['recipient']}\")
"
```

**جدولة في Cron:**

```bash
# تحرير crontab
crontab -e

# إضافة:
0 9 * * * cd /srv/ai_system && python main.py status > /tmp/daily_status.txt
0 2 * * * find /srv/ai_system/logs/ -name "*.log.*" -mtime +7 -delete
```

---

### 2. الصيانة الأسبوعية

```bash
# نسخة احتياطية أسبوعية كاملة
python src/setup/backup_database.py

# تنظيف النسخ الاحتياطية القديمة (>30 يوم)
find backups/ -name "*.sql" -mtime +30 -delete
find backups/ -name "*.tar.gz" -mtime +30 -delete

# فحص أداء قاعدة البيانات
psql -U ai_system_user -d ai_monitoring -c "
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;
"

# تحليل الجداول
psql -U ai_system_user -d ai_monitoring -c "ANALYZE VERBOSE;"

# مراجعة إحصائيات Event Bus
python -c "
from tools.agent_communication import get_communication_system
comm = get_communication_system()
stats = comm.get_statistics()
print('إحصائيات الأسبوع:')
print(f'  إجمالي الرسائل: {stats[\"total_messages\"]}')
print(f'  أنواع الرسائل: {stats[\"message_types\"]}')
print(f'  متوسط حجم الطوابير: {stats[\"average_queue_size\"]}')
"
```

---

### 3. الصيانة الشهرية

```bash
# مراجعة شاملة للنظام

# 1. تحديث الحزم
pip install --upgrade -r requirements.txt

# 2. فحص أمان الحزم
pip check

# 3. مراجعة حجم قاعدة البيانات
psql -U ai_system_user -d ai_monitoring -c "
SELECT pg_size_pretty(pg_database_size('ai_monitoring')) AS db_size;
"

# 4. تحسين قاعدة البيانات
psql -U ai_system_user -d ai_monitoring -c "VACUUM FULL ANALYZE;"

# 5. مراجعة السجلات للأنماط
grep -i "error" logs/*.log | wc -l
grep -i "warning" logs/*.log | wc -l
grep -i "critical" logs/*.log | wc -l

# 6. تدوير المفاتيح الأمنية (اختياري)
python dev_platform/tools/secrets_cli.py rotate dashboard

# 7. اختبار النسخ الاحتياطي
python src/setup/restore_database.py backups/latest.sql --test
```

---

## 📊 المراقبة والتشخيص

### 1. مراقبة الأداء في الوقت الفعلي

```bash
# واجهة CLI/TUI
python -m dev_platform.cli_interface

# ثم اختر:
# 1 - عرض الحالة
# 2 - مراقبة الموارد

# أو استخدم لوحة التحكم الويب:
# http://your-server:5000
```

---

### 2. فحص صحة جميع الأنظمة

```python
# احفظ هذا في check_all_health.py

from tools.agent_communication import get_communication_system
from tools.notification_system import NotificationSystem

def check_all_systems():
    print("=== فحص صحة الأنظمة ===\n")
    
    # 1. Event Bus
    print("📡 Event Bus:")
    comm = get_communication_system()
    bus_health = comm.health_check()
    print(f"  الحالة: {bus_health['status']}")
    print(f"  النقاط: {bus_health['score']}/100")
    if bus_health['warnings']:
        for w in bus_health['warnings']:
            print(f"  ⚠️  {w}")
    
    # 2. نظام الإشعارات
    print("\n📧 نظام الإشعارات:")
    notifier = NotificationSystem()
    notif_health = notifier.health_check(quick=True)
    print(f"  Telegram: {'✅' if notif_health['telegram']['available'] else '❌'}")
    print(f"  Email: {'✅' if notif_health['email']['available'] else '❌'}")
    
    # 3. قاعدة البيانات
    print("\n🗄️  قاعدة البيانات:")
    # أضف فحص قاعدة البيانات هنا
    
    print("\n=== انتهى الفحص ===")

if __name__ == "__main__":
    check_all_systems()
```

```bash
# تشغيل الفحص
python check_all_health.py
```

---

### 3. تحليل السجلات

```bash
# البحث عن الأخطاء في آخر ساعة
find logs/ -name "*.log" -mmin -60 -exec grep -i "error" {} + | tail -20

# عد الأخطاء حسب النوع
grep -h "ERROR" logs/*.log | cut -d'-' -f3 | sort | uniq -c | sort -nr

# آخر 100 رسالة حرجة
grep -h "CRITICAL" logs/*.log | tail -100

# رسائل وكيل محدد في آخر 24 ساعة
grep "ai_manager" logs/ai_manager.log | tail -100
```

---

## 🗄️ إدارة قاعدة البيانات

### 1. النسخ الاحتياطي اليدوي

```bash
# نسخة احتياطية فورية
python src/setup/backup_database.py

# التحقق من النسخة
ls -lh backups/database_full_backup_*.sql
```

---

### 2. استعادة جدول واحد

```bash
# إذا كنت تريد استعادة جدول واحد فقط

# الخطوة 1: استخراج الجدول من النسخة الاحتياطية
pg_restore -t table_name backups/database_full_backup_YYYYMMDD.sql > table_only.sql

# الخطوة 2: حذف الجدول الحالي (احذر!)
psql -U ai_system_user -d ai_monitoring -c "DROP TABLE IF EXISTS table_name CASCADE;"

# الخطوة 3: استعادة
psql -U ai_system_user -d ai_monitoring < table_only.sql
```

---

### 3. تحسين الأداء

```bash
# فحص الاستعلامات البطيئة
psql -U ai_system_user -d ai_monitoring -c "
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
"

# إعادة بناء الفهارس
psql -U ai_system_user -d ai_monitoring -c "REINDEX DATABASE ai_monitoring;"

# تحديث الإحصائيات
psql -U ai_system_user -d ai_monitoring -c "ANALYZE VERBOSE;"
```

---

## 📞 جهات الاتصال للتصعيد

### مستويات التصعيد

**المستوى 1: الوكلاء التلقائيون**
- يتعامل مع 90% من المشاكل
- استجابة فورية

**المستوى 2: المسؤول المناوب**
- للمشاكل المتوسطة
- استجابة خلال 30 دقيقة

**المستوى 3: المهندس الرئيسي**
- للحوادث الحرجة
- استجابة خلال 15 دقيقة

**المستوى 4: إدارة الأزمات**
- لتعطل النظام الكامل
- استجابة فورية

---

## 📋 قوائم التحقق

### ✅ قبل النشر (Pre-Deployment)

- [ ] نسخة احتياطية كاملة منفذة
- [ ] جميع الاختبارات ناجحة
- [ ] السجلات تمت مراجعتها
- [ ] الإشعارات تعمل
- [ ] Event Bus صحي
- [ ] قاعدة البيانات محسّنة
- [ ] خطة التراجع جاهزة

### ✅ بعد النشر (Post-Deployment)

- [ ] جميع الوكلاء تعمل
- [ ] لا أخطاء في السجلات
- [ ] الإشعارات تصل
- [ ] لوحة التحكم تعمل
- [ ] قاعدة البيانات متصلة
- [ ] استهلاك الموارد طبيعي
- [ ] فحص الصحة نجح 100%

### ✅ استعادة من كارثة

- [ ] الخادم يعمل
- [ ] PostgreSQL مثبت
- [ ] Python 3.11+ مثبت
- [ ] النسخ الاحتياطية متوفرة
- [ ] الإعدادات محفوظة
- [ ] الأسرار محفوظة
- [ ] الشبكة تعمل
- [ ] الوصول للخادم متاح

---

## 🎯 الخلاصة

هذه الكتيبات توفر إرشادات واضحة للتعامل مع السيناريوهات الشائعة. **احتفظ بهذه الوثيقة في مكان يسهل الوصول إليه** واتبع الإجراءات بدقة.

**للمساعدة الفورية:**
- السجلات: `logs/*.log`
- التوثيق: `docs/*.md`
- النسخ الاحتياطية: `backups/`
- الإعدادات: `configs/config.yaml`

---

**الإصدار:** 1.0  
**آخر تحديث:** 15 نوفمبر 2025  
**المراجع التالي:** شهرياً أو عند التغييرات الكبرى
