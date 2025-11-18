# النسخ الاحتياطي والاستعادة (Backup & Recovery)

## 1. استراتيجية النسخ الاحتياطي

### قاعدة البيانات
```yaml
frequency:
  full_backup: يومياً (2:00 AM UTC)
  incremental: كل 6 ساعات
  transaction_logs: مستمر

retention:
  daily: 7 أيام
  weekly: 4 أسابيع
  monthly: 12 شهر
  yearly: 7 سنوات

location:
  primary: S3 bucket (encrypted)
  secondary: Glacier (long-term)
  geographic: 3 regions مختلفة
```

### الملفات والتطبيقات
```yaml
application_code:
  method: Git repository
  retention: مفتوح
  
user_files:
  frequency: يومياً
  retention: 30 يوم
  
configuration:
  frequency: عند كل تغيير
  retention: 90 يوم
```

---

## 2. إجراءات الاستعادة

### استعادة قاعدة البيانات
```bash
# 1. إيقاف التطبيق
systemctl stop app

# 2. استعادة من النسخة الاحتياطية
pg_restore -d production backup_2025-11-18.dump

# 3. التحقق من السلامة
psql -c "SELECT count(*) FROM users;"

# 4. إعادة تشغيل التطبيق
systemctl start app
```

### Recovery Time Objective (RTO)
- **Critical**: < 1 ساعة
- **High**: < 4 ساعات
- **Normal**: < 24 ساعة

### Recovery Point Objective (RPO)
- **Database**: < 15 دقيقة
- **Files**: < 24 ساعة
- **Logs**: < 1 ساعة

---

**آخر تحديث**: 2025-11-18
