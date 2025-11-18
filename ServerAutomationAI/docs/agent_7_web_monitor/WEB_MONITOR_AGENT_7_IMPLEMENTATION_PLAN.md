# 📋 خطة تنفيذ شاملة: الوكيل رقم 7 - وكيل مراقبة تطبيق الويب

**تاريخ الإنشاء:** 15 نوفمبر 2025  
**الحالة:** جاهز للتنفيذ  
**المدة المقدرة:** 22 يوم عمل  
**الميزانية التقديرية:** 33 مهمة × 200,000 توكن = 6,600,000 توكن

---

## 🎯 نظرة عامة على المشروع

### التطبيق المراد مراقبته

**الاسم:** منصة توليد إشارات التداول - Binar Join Analytic  
**النوع:** تطبيق ويب لتوليد إشارات التداول (Express + React + PostgreSQL)  
**المسار على السيرفر:** `/home/administrator/Bot.v4`  
**السيرفر:** `93.127.142.144` (Ubuntu 24.04 LTS)  
**التقنيات:**
- **Backend:** Express.js + TypeScript
- **Frontend:** React + Vite + TypeScript
- **قاعدة البيانات:** PostgreSQL (Neon)
- **الترجمة:** Tolgee (العربية، الإنجليزية، الهندية) مع RTL
- **الاختبار:** Playwright (مُثبت مسبقاً)

---

## ⚠️ معلومات حرجة: بيئة التشغيل

### 🔴 الوكيل رقم 7 يعمل على سيرفر خارجي وليس على Replit

**مهم جداً:**
1. **الوكيل رقم 7 سيتم نشره وتشغيله على السيرفر الخارجي** `93.127.142.144`
2. **منصة Replit تُستخدم فقط** لتطوير الكود ثم النشر عبر Bridge Tool
3. **التطبيق المراد مراقبته** موجود على نفس السيرفر في `/home/administrator/Bot.v4`
4. **جميع الوكلاء (1-7) تعمل على السيرفر الخارجي** في `/srv/ai_system/`

### طريقة الاتصال والعمل

```
┌──────────────────────────────────────────────────────────┐
│              منصة Replit (بيئة التطوير فقط)              │
│  - تطوير الكود                                           │
│  - اختبار محلي                                          │
│  - Git version control                                  │
└──────────────┬───────────────────────────────────────────┘
               │
               │ Bridge Tool (SFTP/SSH)
               │ python3 bridge_tool/cli.py push
               ↓
┌──────────────────────────────────────────────────────────┐
│          السيرفر الخارجي 93.127.142.144                  │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  /srv/ai_system/  (نظام الوكلاء)                  │ │
│  │  ├── agents/                                       │ │
│  │  │   ├── ai_manager.py       (الوكيل الأب)        │ │
│  │  │   ├── performance_monitor.py                   │ │
│  │  │   ├── log_analyzer.py                          │ │
│  │  │   ├── security_monitor.py                      │ │
│  │  │   ├── database_manager.py                      │ │
│  │  │   ├── backup_recovery.py                       │ │
│  │  │   └── web_monitor_agent.py  ← الوكيل رقم 7    │ │
│  │  ├── tools/                                        │ │
│  │  │   ├── communication.py (queue system)          │ │
│  │  │   ├── logger.py                                │ │
│  │  │   └── notification_system.py                   │ │
│  │  └── configs/config.yaml                          │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  /home/administrator/Bot.v4  (التطبيق المراقَب)   │ │
│  │  ├── server/                                       │ │
│  │  ├── client/                                       │ │
│  │  ├── package.json                                  │ │
│  │  └── ...                                           │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ✓ الوكيل 7 يعمل 24/7 عبر systemd                       │
│  ✓ يراقب التطبيق محلياً (localhost)                     │
│  ✓ يتواصل مع الوكلاء الأخرى عبر queue                   │
│  ✓ يرسل التقارير للوكيل الأب (AI Manager)               │
└──────────────────────────────────────────────────────────┘
```

### دورة العمل الكاملة

```
1. التطوير (Replit)
   ↓
2. الاختبار المحلي (Replit)
   ↓
3. النشر (Bridge Tool → السيرفر)
   ↓
4. التشغيل 24/7 (systemd على السيرفر)
   ↓
5. المراقبة والتقارير (على السيرفر)
   ↓
6. التحديثات (Replit → Bridge Tool → السيرفر)
```

---

## 📚 المعرفة المطلوبة قبل البدء

### ملفات يجب قراءتها أولاً

**في منصة Replit:**
1. `replit.md` - نظرة عامة على النظام بأكمله
2. `README.md` - تفاصيل الوكلاء 1-6
3. `PROGRESS.md` - حالة المشروع والإنجازات
4. `agents/ai_manager.py` - الوكيل الأب (للفهم)
5. `tools/communication.py` - نظام queue للتواصل
6. `configs/config.yaml` - الإعدادات المركزية

**على السيرفر (عبر Bridge Tool):**
```bash
python3 bridge_tool/cli.py exec "cat /home/administrator/Bot.v4/README.md"
python3 bridge_tool/cli.py exec "cat /home/administrator/Bot.v4/package.json"
```

---

## 🛠️ الأدوات المستخدمة (100% مجانية)

### أدوات إلزامية (مجانية تماماً)

| الأداة | الاستخدام | المصدر | السعر |
|--------|-----------|--------|-------|
| **Playwright** | Synthetic monitoring, headless browser | `npm install playwright` | مجاني 100% |
| **Python requests/httpx** | HTTP checks, API testing | `pip install requests httpx` | مجاني 100% |
| **SQLite** | تخزين النتائج محلياً | Built-in Python | مجاني 100% |
| **asyncio** | Async operations, queues | Built-in Python | مجاني 100% |
| **psutil** | System metrics (موجود) | `pip install psutil` | مجاني 100% |
| **BeautifulSoup4** | HTML parsing, link checking | `pip install beautifulsoup4` | مجاني 100% |
| **axe-core-python** | WCAG accessibility | `pip install axe-selenium-python` | مجاني 100% |

### أدوات محظورة (ممنوع استخدامها)

❌ **خدمات مدفوعة:**
- Apify Web Scanner (مدفوع)
- Screaming Frog SEO (نسخة كاملة مدفوعة)
- SigNoz Cloud (نسخة السحابة مدفوعة)
- New Relic, DataDog (مدفوعة)

✅ **البديل المسموح:**
- استخدام النسخ المفتوحة المصدر والمجانية فقط
- تطوير custom scanners باستخدام Playwright + Python

---

## 🔒 القيود الصارمة للتطوير

### قواعد إلزامية (MUST FOLLOW)

```python
# ❌ ممنوع: إنشاء ملفات مكررة
# إذا كان هناك logger.py موجود، استخدمه

# ✅ صحيح: استخدام البنية الموجودة
from tools.logger import get_logger
logger = get_logger('web_monitor')

# ❌ ممنوع: إنشاء نظام queue جديد
# النظام الموجود في tools/communication.py

# ✅ صحيح: استخدام النظام الموجود
from tools.agent_communication import get_communication_system
comm = get_communication_system()
```

### 1. لا تكرار في الكود

**قبل كتابة أي كود:**
```bash
# ابحث في الملفات الموجودة
grep -r "def send_message" tools/
grep -r "class.*Monitor" agents/
```

**استخدم البنية الموجودة:**
- `tools/logger.py` → للسجلات
- `tools/communication.py` → للتواصل بين الوكلاء
- `tools/notification_system.py` → للتنبيهات

### 2. تنظيف الملفات غير المستخدمة

**قبل إضافة ملفات جديدة:**
```bash
# على السيرفر - نظف الملفات القديمة
python3 bridge_tool/cli.py exec "cd /srv/ai_system && find . -name '*.pyc' -delete"
python3 bridge_tool/cli.py exec "cd /srv/ai_system && find . -name '__pycache__' -type d -exec rm -rf {} +"
```

### 3. النسخ الاحتياطي الإلزامي

**قبل أي تعديل:**
```bash
# 1. طلب نسخة احتياطية من الوكلاء الآخرين
python3 bridge_tool/cli.py exec "python /srv/ai_system/agents/backup_recovery.py"

# 2. نسخة احتياطية من التطبيق المراقَب
python3 bridge_tool/cli.py exec "cd /home/administrator/Bot.v4 && tar -czf ../Bot.v4_backup_$(date +%Y%m%d_%H%M%S).tar.gz ."

# 3. التحقق من النسخة
python3 bridge_tool/cli.py exec "ls -lh /home/administrator/Bot.v4_backup_*"
```

### 4. تحديث حالة التقدم

**بعد كل مهمة:**
```bash
# تحديث PROGRESS.md
echo "✅ [$(date)] Task X completed" >> PROGRESS.md
git add PROGRESS.md
git commit -m "Update: Completed Task X"
```

---

## 📊 تصنيف الوظائف (40 وظيفة)

### الفئة A: يطلبها من الوكلاء الموجودين (7 وظائف)

| # | الوظيفة | الوكيل المسؤول | طريقة الطلب |
|---|---------|----------------|-------------|
| 2 | CPU/RAM | Performance Monitor | `comm.send_message("performance_monitor", {"type": "data_request", "metric": "cpu"})` |
| 3 | قواعد البيانات | Database Manager | `comm.send_message("database_manager", {"type": "data_request"})` |
| 4 | نشاط السيرفر | Security Monitor | `comm.send_message("security_monitor", {"type": "data_request"})` |
| 8 | SSL Certificates | Security Monitor | `comm.send_message("security_monitor", {"type": "cert_status"})` |
| 9 | سجلات الأخطاء | Log Analyzer | `comm.subscribe("log_alerts")` |
| 13 | تغييرات الملفات | Security Monitor | `comm.subscribe("file_integrity_feed")` |
| 37 | حرارة السيرفر | Performance Monitor | `comm.send_message("performance_monitor", {"type": "sensors"})` |

### الفئة B: يبنيها بنفسه (20 وظيفة)

| # | الوظيفة | الوحدة | الأولوية |
|---|---------|--------|----------|
| 1 | مراقبة الجلسات | `session_inspector.py` | High |
| 5 | ملفات Assets | `asset_checker.py` | High |
| 6 | سجل المتصفح | `console_collector.py` | Critical |
| 7 | محتوى غير آمن | `mixed_content_scan.py` | High |
| 11 | SEO | `seo_audit.py` | Medium |
| 12 | APIs غير مستخدمة | `api_usage_diff.py` | High |
| 15 | رفع الملفات | `upload_guard.py` | Critical |
| 16 | جودة الصور | `image_optimizer.py` | Medium |
| 17 | توافق الجوال | `mobile_tester.py` | High |
| 19 | WebSockets | `websocket_probe.py` | Medium |
| 20 | أداء JavaScript | `js_profiler.py` | High |
| 21 | ذاكرة المتصفح | `browser_memory.py` | Medium |
| 22 | أخطاء React | `framework_log_capture.py` | High |
| 23 | النصوص غير المترجمة | `i18n_scanner.py` | Critical |
| 24 | معلومات المتصفحات | `browser_matrix.py` | Low |
| 27 | robots/sitemap | `robots_sitemap_check.py` | Medium |
| 28 | صور الخلفية | `bg_image_audit.py` | Low |
| 30 | تحليل UX | `ux_evaluator.py` | Medium |
| 31 | تذكير المشاكل | `issue_reminder.py` | Low |
| 32 | تحسينات السلوك | `behaviour_insights.py` | Low |

### الفئة C: تعاون مشترك (13 وظيفة)

| # | الوظيفة | الوكيل المشارك | الجزء الخاص بالوكيل 7 |
|---|---------|----------------|----------------------|
| 10 | أوقات الاستجابة | Performance Monitor | `synthetic_latency.py` |
| 14 | Cron Jobs | Log Analyzer | `cron_log_rules.py` |
| 18 | تعديلات الواجهة | Security Monitor | `frontend_diff.py` |
| 25 | جودة CDN | Performance Monitor | `cdn_probe.py` |
| 26 | SQL Injection/XSS | Security Monitor | `threat_context.py` |
| 29 | TTFB | Performance Monitor | `ttfb_probe.py` |
| 33 | تغييرات CSS | Security Monitor | `css_diff.py` |
| 34 | إدارة المخاطر | AI Manager | `risk_playbooks.py` |
| 35 | طرف ثالث | Security Monitor | `third_party_watch.py` |
| 36 | مستوى خطورة | AI Manager | `severity_alignment.py` |
| 38 | تقارير دورية | AI Manager | `report_scheduler.py` |
| 39 | AI للمقارنة | Performance+Log | `ai_trend.py` |
| 40 | توقع الأعطال ML | Performance+Log | `failure_predictor.py` |

---

## 📅 خطة التنفيذ المرحلية (33 مهمة)

### المرحلة 0: الإعداد والبحث (5 مهام - 1,000,000 توكن)

#### المهمة 0.1: فحص البيئة والتطبيق المراقَب
**المدة:** يوم واحد  
**الميزانية:** 200,000 توكن  
**الوصف:** فحص شامل للتطبيق المراد مراقبته وفهم بنيته.

**الخطوات التفصيلية:**
```bash
# 1. الاتصال بالسيرفر
python3 bridge_tool/cli.py test

# 2. فحص التطبيق
python3 bridge_tool/cli.py exec "cd /home/administrator/Bot.v4 && ls -la"
python3 bridge_tool/cli.py exec "cd /home/administrator/Bot.v4 && cat package.json"
python3 bridge_tool/cli.py exec "cd /home/administrator/Bot.v4 && cat .env.example"

# 3. فحص السيرفر والخدمات
python3 bridge_tool/cli.py exec "ps aux | grep node"
python3 bridge_tool/cli.py exec "netstat -tulpn | grep LISTEN"
python3 bridge_tool/cli.py exec "systemctl status"

# 4. فحص البنية الحالية للوكلاء
python3 bridge_tool/cli.py exec "ls -la /srv/ai_system/agents/"
python3 bridge_tool/cli.py exec "cat /srv/ai_system/configs/config.yaml"
```

**الناتج المطلوب:**
- [ ] ملف `docs/bot_v4_analysis.md` يحتوي على:
  - هيكل التطبيق الكامل
  - المنافذ المستخدمة
  - قواعد البيانات
  - الخدمات النشطة
  - نقاط النهاية (Endpoints)

**معايير القبول:**
- ✅ جدول كامل بجميع endpoints
- ✅ قائمة بجميع صفحات الواجهة
- ✅ فهم نظام الترجمة (Tolgee)
- ✅ معرفة منافذ التشغيل

---

#### المهمة 0.2: إنشاء قاعدة البيانات للوكيل 7
**المدة:** نصف يوم  
**الميزانية:** 200,000 توكن  

**الخطوات:**
```sql
-- على السيرفر: إنشاء جداول الوكيل 7
-- الملف: agents/web_monitor/schema.sql

CREATE TABLE IF NOT EXISTS web_monitor_runs (
    run_id TEXT PRIMARY KEY,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT CHECK(status IN ('running', 'completed', 'failed')),
    total_checks INTEGER DEFAULT 0,
    passed_checks INTEGER DEFAULT 0,
    failed_checks INTEGER DEFAULT 0,
    summary JSON
);

CREATE TABLE IF NOT EXISTS web_monitor_findings (
    finding_id TEXT PRIMARY KEY,
    run_id TEXT REFERENCES web_monitor_runs(run_id),
    severity TEXT CHECK(severity IN ('Critical', 'High', 'Medium', 'Low')),
    component TEXT NOT NULL,
    description TEXT NOT NULL,
    remediation_hint TEXT,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    status TEXT DEFAULT 'open' CHECK(status IN ('open', 'in_progress', 'resolved', 'ignored'))
);

CREATE TABLE IF NOT EXISTS synthetic_transactions (
    transaction_id TEXT PRIMARY KEY,
    run_id TEXT REFERENCES web_monitor_runs(run_id),
    flow_type TEXT NOT NULL,  -- 'payment', 'login', 'signup', 'upload'
    status TEXT CHECK(status IN ('success', 'failure', 'timeout')),
    duration_ms INTEGER,
    error_details TEXT,
    screenshot_path TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS api_usage_stats (
    endpoint TEXT PRIMARY KEY,
    last_accessed TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    avg_response_ms INTEGER,
    error_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'stale', 'dead'))
);

CREATE TABLE IF NOT EXISTS localization_gaps (
    gap_id TEXT PRIMARY KEY,
    component TEXT NOT NULL,
    missing_key TEXT NOT NULL,
    language TEXT NOT NULL,
    page_url TEXT,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fixed_at TIMESTAMP
);

-- Indexes للأداء
CREATE INDEX idx_findings_severity ON web_monitor_findings(severity);
CREATE INDEX idx_findings_component ON web_monitor_findings(component);
CREATE INDEX idx_findings_status ON web_monitor_findings(status);
CREATE INDEX idx_findings_timestamp ON web_monitor_findings(detected_at);
CREATE INDEX idx_transactions_flow ON synthetic_transactions(flow_type);
CREATE INDEX idx_transactions_status ON synthetic_transactions(status);
CREATE INDEX idx_api_status ON api_usage_stats(status);
```

**تنفيذ على السيرفر:**
```bash
# إنشاء الجداول
python3 bridge_tool/cli.py exec "cd /srv/ai_system && python -c \"
from tools.logger import get_logger
import sqlite3

# استخدام قاعدة البيانات الموجودة
conn = sqlite3.connect('cache/workflow_cache.db')
cursor = conn.cursor()

# تنفيذ SQL من ملف schema.sql
with open('agents/web_monitor/schema.sql', 'r') as f:
    cursor.executescript(f.read())

conn.commit()
conn.close()
print('✅ Database schema created successfully')
\""
```

**الناتج:**
- [ ] ملف `agents/web_monitor/schema.sql`
- [ ] الجداول منشأة على السيرفر
- [ ] اختبار الاتصال بقاعدة البيانات

---

#### المهمة 0.3: إعداد بروتوكول التكامل مع الوكلاء
**المدة:** يوم واحد  
**الميزانية:** 200,000 توكن  

**الخطوات:**
```python
# الملف: agents/web_monitor/integration_bridge.py

import asyncio
from typing import Dict, Any, Optional
from tools.agent_communication import get_communication_system

class IntegrationBridge:
    """طبقة التكامل مع الوكلاء الموجودين (1-6)"""
    
    def __init__(self, agent_name: str = "web_monitor"):
        self.agent_name = agent_name
        self.comm = get_communication_system()
        self.subscriptions = []
        
    async def request_cpu_metrics(self) -> Dict[str, Any]:
        """طلب بيانات CPU من Performance Monitor"""
        message = {
            "type": "data_request",
            "from": self.agent_name,
            "to": "performance_monitor",
            "payload": {
                "metric": "cpu",
                "scope": "last_5m"
            }
        }
        
        # إرسال الطلب
        await self.comm.send_message("performance_monitor", message)
        
        # انتظار الرد (مع timeout)
        response = await self.comm.receive_message(
            self.agent_name, 
            timeout=10
        )
        
        return response.get("payload", {})
    
    async def request_db_health(self) -> Dict[str, Any]:
        """طلب حالة قاعدة البيانات من Database Manager"""
        message = {
            "type": "data_request",
            "from": self.agent_name,
            "to": "database_manager",
            "payload": {
                "check": "health"
            }
        }
        
        await self.comm.send_message("database_manager", message)
        response = await self.comm.receive_message(self.agent_name, timeout=10)
        return response.get("payload", {})
    
    async def subscribe_to_log_alerts(self):
        """الاشتراك في تنبيهات السجلات من Log Analyzer"""
        message = {
            "type": "subscribe",
            "from": self.agent_name,
            "to": "log_analyzer",
            "topics": ["log_alerts", "error_events"]
        }
        
        await self.comm.send_message("log_analyzer", message)
        
        # انتظار التأكيد
        ack = await self.comm.receive_message(self.agent_name, timeout=5)
        if ack.get("subscribed"):
            self.subscriptions.append("log_alerts")
            return True
        return False
    
    async def send_alert_to_ai_manager(
        self, 
        severity: str, 
        component: str, 
        description: str
    ):
        """إرسال تنبيه للوكيل الأب (AI Manager)"""
        message = {
            "type": "alert",
            "from": self.agent_name,
            "to": "ai_manager",
            "payload": {
                "severity": severity,
                "component": component,
                "description": description,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        await self.comm.send_message("ai_manager", message)

# مثال للاستخدام
async def test_integration():
    bridge = IntegrationBridge()
    
    # طلب بيانات
    cpu_data = await bridge.request_cpu_metrics()
    print(f"CPU Usage: {cpu_data}")
    
    # الاشتراك في التنبيهات
    subscribed = await bridge.subscribe_to_log_alerts()
    print(f"Subscribed to alerts: {subscribed}")
    
    # إرسال تنبيه
    await bridge.send_alert_to_ai_manager(
        severity="High",
        component="Payment Page",
        description="Payment page load time exceeded 3 seconds"
    )

if __name__ == "__main__":
    asyncio.run(test_integration())
```

**معايير القبول:**
- [ ] ملف `integration_bridge.py` يعمل
- [ ] اختبار الاتصال مع كل وكيل
- [ ] توثيق كامل لكل دالة

---

#### المهمة 0.4: تحديث config.yaml
**المدة:** نصف يوم  
**الميزانية:** 200,000 توكن  

```yaml
# إضافة إعدادات الوكيل 7 إلى configs/config.yaml

agents:
  web_monitor:
    enabled: true
    check_interval: 300  # كل 5 دقائق
    
    # التطبيق المراقَب
    target_app:
      path: "/home/administrator/Bot.v4"
      url: "http://localhost:3000"  # أو المنفذ الفعلي
      name: "Binar Join Analytic"
    
    # إعدادات Playwright
    playwright:
      headless: true
      timeout: 30000  # 30 ثانية
      browsers:
        - chromium
      
    # الفحوصات المفعّلة
    checks:
      session_monitoring: true
      asset_integrity: true
      console_errors: true
      mixed_content: true
      seo_audit: false  # سيتم تفعيله لاحقاً
      api_usage: true
      upload_security: true
      image_optimization: false
      mobile_compatibility: true
      websocket_health: true
      javascript_performance: true
      browser_memory: false
      framework_errors: true
      i18n_completeness: true  # حرج جداً
      browser_compatibility: false
      robots_sitemap: true
      
    # عتبات التنبيهات
    thresholds:
      page_load_time_ms: 3000
      api_response_time_ms: 1000
      memory_leak_threshold_mb: 100
      missing_translations_critical: 5
      console_errors_critical: 10
      
    # التقارير
    reports:
      daily: true
      weekly: true
      monthly: true
      send_to_ai_manager: true
```

---

#### المهمة 0.5: إنشاء البنية الأساسية للوكيل
**المدة:** يوم واحد  
**الميزانية:** 200,000 توكن  

```python
# الملف: agents/web_monitor_agent.py

import asyncio
import sys
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# إضافة المسارات
sys.path.append(str(Path(__file__).parent.parent))

from tools.logger import get_logger
from tools.agent_communication import get_communication_system
from agents.web_monitor.integration_bridge import IntegrationBridge

class WebAppMonitorAgent:
    """
    وكيل مراقبة تطبيق الويب الشامل (الوكيل رقم 7)
    
    المسؤوليات:
    - مراقبة تطبيق الويب 24/7
    - فحص شامل لجميع جوانب التطبيق
    - التكامل مع الوكلاء 1-6
    - إرسال تقارير للوكيل الأب
    """
    
    def __init__(self, config: Dict):
        self.agent_name = "web_monitor"
        self.config = config
        self.logger = get_logger(self.agent_name)
        self.comm = get_communication_system()
        self.bridge = IntegrationBridge(self.agent_name)
        self.running = False
        
        self.logger.info(f"✓ {self.agent_name} initialized")
    
    async def start(self):
        """بدء تشغيل الوكيل"""
        self.running = True
        self.logger.info("Starting Web Application Monitor Agent...")
        
        # الاشتراك في التنبيهات من الوكلاء الأخرى
        await self._subscribe_to_agents()
        
        # بدء دورة المراقبة
        await self._monitoring_loop()
    
    async def _subscribe_to_agents(self):
        """الاشتراك في بيانات الوكلاء الأخرى"""
        self.logger.info("Subscribing to other agents...")
        
        # الاشتراك في تنبيهات السجلات
        await self.bridge.subscribe_to_log_alerts()
        
        self.logger.info("✓ Subscriptions completed")
    
    async def _monitoring_loop(self):
        """دورة المراقبة الرئيسية"""
        check_interval = self.config.get('check_interval', 300)
        
        while self.running:
            try:
                self.logger.info("Starting monitoring cycle...")
                
                # 1. تحميل الإعدادات
                # 2. تسجيل السيناريوهات
                # 3. تنفيذ الفحوصات
                # 4. جمع المقاييس
                # 5. تقييم الشذوذ
                # 6. حفظ النتائج
                # 7. نشر التقارير
                
                await self._run_checks()
                
                self.logger.info(f"Cycle completed. Sleeping for {check_interval}s")
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(60)  # انتظار دقيقة في حالة الخطأ
    
    async def _run_checks(self):
        """تنفيذ جميع الفحوصات"""
        # سيتم تنفيذها في المراحل القادمة
        pass
    
    async def stop(self):
        """إيقاف الوكيل"""
        self.logger.info("Stopping Web Monitor Agent...")
        self.running = False

async def main():
    # تحميل الإعدادات (سيتم تحسينه لاحقاً)
    config = {
        'check_interval': 300,
        'target_app': {
            'url': 'http://localhost:3000'
        }
    }
    
    agent = WebAppMonitorAgent(config)
    
    try:
        await agent.start()
    except KeyboardInterrupt:
        await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

**معايير القبول:**
- [ ] الملف `web_monitor_agent.py` يعمل
- [ ] يتصل بالوكلاء الأخرى
- [ ] يظهر في سجلات AI Manager

---

### المرحلة 1: البنية الأساسية (3 مهام - 600,000 توكن)

#### المهمة 1.1: إنشاء Task Registry
**المدة:** نصف يوم  
**الميزانية:** 200,000 توكن  

```python
# الملف: agents/web_monitor/shared/task_registry.py

from dataclasses import dataclass, field
from typing import List, Callable, Dict, Any
from datetime import datetime
from enum import Enum

class TaskPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class MonitoringTask:
    """مهمة مراقبة واحدة"""
    task_id: str
    name: str
    check_func: Callable
    priority: TaskPriority
    enabled: bool = True
    status: TaskStatus = TaskStatus.PENDING
    last_run: datetime = None
    last_result: Dict[str, Any] = field(default_factory=dict)
    error_count: int = 0
    success_count: int = 0

class TaskRegistry:
    """سجل المهام - إدارة جميع مهام المراقبة"""
    
    def __init__(self):
        self.tasks: Dict[str, MonitoringTask] = {}
    
    def register(
        self, 
        task_id: str, 
        name: str, 
        check_func: Callable,
        priority: TaskPriority = TaskPriority.NORMAL
    ):
        """تسجيل مهمة جديدة"""
        task = MonitoringTask(
            task_id=task_id,
            name=name,
            check_func=check_func,
            priority=priority
        )
        self.tasks[task_id] = task
        return task
    
    def get_enabled_tasks(self) -> List[MonitoringTask]:
        """الحصول على المهام المفعّلة مرتبة حسب الأولوية"""
        enabled = [t for t in self.tasks.values() if t.enabled]
        return sorted(enabled, key=lambda t: t.priority.value)
    
    def mark_completed(self, task_id: str, result: Dict[str, Any]):
        """تحديد مهمة كمكتملة"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = TaskStatus.COMPLETED
            task.last_run = datetime.now()
            task.last_result = result
            task.success_count += 1
    
    def mark_failed(self, task_id: str, error: str):
        """تحديد مهمة كفاشلة"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = TaskStatus.FAILED
            task.last_run = datetime.now()
            task.last_result = {"error": error}
            task.error_count += 1
```

---

#### المهمة 1.2: إنشاء Concurrency Manager
**المدة:** نصف يوم  
**الميزانية:** 200,000 توكن  

```python
# الملف: agents/web_monitor/shared/concurrency_manager.py

import asyncio
from typing import List, Callable, Dict, Any
from dataclasses import dataclass

@dataclass
class TaskResult:
    task_id: str
    success: bool
    result: Any = None
    error: str = None
    duration_ms: float = 0

class ConcurrencyManager:
    """إدارة تنفيذ المهام المتزامنة"""
    
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def run_task_with_semaphore(
        self, 
        task_id: str, 
        task_func: Callable
    ) -> TaskResult:
        """تنفيذ مهمة واحدة مع التحكم في التزامن"""
        async with self.semaphore:
            import time
            start = time.time()
            
            try:
                result = await task_func()
                duration_ms = (time.time() - start) * 1000
                
                return TaskResult(
                    task_id=task_id,
                    success=True,
                    result=result,
                    duration_ms=duration_ms
                )
            except Exception as e:
                duration_ms = (time.time() - start) * 1000
                
                return TaskResult(
                    task_id=task_id,
                    success=False,
                    error=str(e),
                    duration_ms=duration_ms
                )
    
    async def run_tasks_parallel(
        self, 
        tasks: Dict[str, Callable]
    ) -> List[TaskResult]:
        """تنفيذ عدة مهام بالتزامن"""
        task_coroutines = [
            self.run_task_with_semaphore(task_id, task_func)
            for task_id, task_func in tasks.items()
        ]
        
        results = await asyncio.gather(*task_coroutines)
        return results
```

---

(يتبع في الملف التالي بسبب حد الطول...)

