# 🏗️ Phase 0: البنية التحتية الأساسية (Foundation)

**المدة:** 2-3 أسابيع  
**الأولوية:** 🔴 حرجة (يجب أن تكتمل قبل Phase 1)  
**الحالة:** 📋 مُخطط

---

## 🎯 الهدف

إنشاء البنية التحتية الأساسية التي يحتاجها النظام لدعم Model Pool Manager و Dashboard بشكل آمن وفعال.

---

## 📦 المكونات المطلوبة

### 1. Centralized Secret Management (إدارة الأسرار المركزية)

#### الحل المُقترح: HashiCorp Vault (مجاني + open source)

```bash
# التثبيت على السيرفر
sudo apt update
sudo apt install vault

# التكوين الأولي
vault server -dev  # للتطوير
# أو
vault server -config=/etc/vault/config.hcl  # للإنتاج
```

**الملفات المطلوبة:**
```
security/
├── __init__.py
├── vault_client.py           # عميل Vault
├── secrets_manager.py        # واجهة موحدة للأسرار
├── encryption.py             # تشفير محلي (fallback)
└── key_rotation.py           # تدوير المفاتيح
```

**Database Schema:**
```sql
-- جدول لتتبع الأسرار (metadata فقط، ليس القيم)
CREATE TABLE secrets_metadata (
    id SERIAL PRIMARY KEY,
    secret_name VARCHAR(100) UNIQUE NOT NULL,
    provider VARCHAR(50),
    storage_backend VARCHAR(50),  -- 'vault', 'aws_secrets', 'local'
    last_rotated TIMESTAMP,
    rotation_policy_days INTEGER DEFAULT 90,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_secrets_provider ON secrets_metadata(provider);
```

#### المخرجات:
- ✅ Secret store يعمل ومُختبر
- ✅ API لتخزين واسترجاع الأسرار
- ✅ تشفير end-to-end
- ✅ Audit logging للوصول

---

### 2. Shared State & Telemetry Layer (الحالة المشتركة والقياسات)

#### Redis للـ Caching & Real-time State

```bash
# التثبيت
sudo apt install redis-server

# التكوين
sudo nano /etc/redis/redis.conf
# bind 127.0.0.1
# requirepass your_strong_password
```

#### TimescaleDB للـ Time-series Metrics (اختياري)

```bash
# إضافة repository
sudo sh -c "echo 'deb https://packagecloud.io/timescale/timescaledb/ubuntu/ $(lsb_release -c -s) main' > /etc/apt/sources.list.d/timescaledb.list"

# التثبيت
sudo apt update
sudo apt install timescaledb-2-postgresql-16
```

**الملفات المطلوبة:**
```
core/
├── __init__.py
├── shared_state.py           # Redis client للحالة المشتركة
├── telemetry_collector.py    # جمع metrics
├── time_series_db.py          # TimescaleDB client
└── cache_manager.py           # إدارة cache
```

**Database Schema (PostgreSQL):**
```sql
-- جدول للـ System State
CREATE TABLE system_state (
    id SERIAL PRIMARY KEY,
    state_key VARCHAR(100) UNIQUE NOT NULL,
    state_value JSONB NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- جدول للـ Metrics (Time-series)
CREATE TABLE metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15, 4) NOT NULL,
    unit VARCHAR(20),
    tags JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- تحويل إلى hypertable (TimescaleDB)
SELECT create_hypertable('metrics', 'timestamp');

CREATE INDEX idx_metrics_name_time ON metrics(metric_name, timestamp DESC);
```

#### المخرجات:
- ✅ Redis يعمل للـ caching
- ✅ Shared state API
- ✅ Metrics collection يعمل
- ✅ Time-series storage (optional)

---

### 3. Message Queue Enhancement (تحسين نظام الرسائل)

#### Upgrade من Queue بسيط إلى RabbitMQ أو Redis Streams

**الخيار 1: Redis Streams (مُوصى به)**
```python
# core/messaging/redis_queue.py
import redis.asyncio as redis

class RedisMessageQueue:
    """
    نظام رسائل مُحسّن باستخدام Redis Streams
    
    Features:
    - Persistence
    - Consumer groups
    - Message acknowledgment
    - Dead letter queue
    """
    
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
    
    async def publish(self, stream: str, message: dict):
        """نشر رسالة"""
        await self.redis.xadd(stream, message)
    
    async def consume(self, stream: str, group: str, consumer: str):
        """استهلاك رسائل"""
        while True:
            messages = await self.redis.xreadgroup(
                group,
                consumer,
                {stream: '>'},
                count=10,
                block=5000
            )
            
            for message_id, message_data in messages:
                yield message_id, message_data
                
                # Acknowledge
                await self.redis.xack(stream, group, message_id)
```

**الخيار 2: RabbitMQ (للأنظمة الكبيرة)**
```bash
sudo apt install rabbitmq-server
```

**Database Schema:**
```sql
-- جدول لتتبع الرسائل
CREATE TABLE message_logs (
    id SERIAL PRIMARY KEY,
    message_id VARCHAR(100),
    sender VARCHAR(100),
    receiver VARCHAR(100),
    message_type VARCHAR(50),
    payload JSONB,
    status VARCHAR(20),  -- 'sent', 'delivered', 'failed'
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_sender ON message_logs(sender, created_at DESC);
CREATE INDEX idx_messages_receiver ON message_logs(receiver, created_at DESC);
```

#### المخرجات:
- ✅ Reliable messaging
- ✅ Message persistence
- ✅ Dead letter handling
- ✅ Message replay capability

---

### 4. Centralized Configuration Management

#### الحل: Configuration Server مع Hot Reload

```python
# core/config_manager.py
import yaml
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ConfigManager(FileSystemEventHandler):
    """
    مدير إعدادات مركزي مع Hot Reload
    
    Features:
    - تحميل من ملفات YAML
    - Hot reload عند التعديل
    - Validation
    - Versioning
    """
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = {}
        self.callbacks = []
        
        self._load_config()
        self._start_watching()
    
    def _load_config(self):
        """تحميل الإعدادات"""
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def _start_watching(self):
        """مراقبة التغييرات في الملف"""
        observer = Observer()
        observer.schedule(self, path=self.config_path, recursive=False)
        observer.start()
    
    def on_modified(self, event):
        """عند تعديل الملف"""
        self._load_config()
        self._notify_subscribers()
    
    def get(self, key: str, default=None):
        """الحصول على قيمة"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def subscribe(self, callback):
        """الاشتراك في تحديثات الإعدادات"""
        self.callbacks.append(callback)
    
    def _notify_subscribers(self):
        """إشعار المشتركين"""
        for callback in self.callbacks:
            callback(self.config)
```

**Database Schema:**
```sql
-- جدول لتتبع التغييرات في الإعدادات
CREATE TABLE config_history (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(200),
    old_value JSONB,
    new_value JSONB,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_config_history_key ON config_history(config_key, changed_at DESC);
```

#### المخرجات:
- ✅ Configuration management API
- ✅ Hot reload
- ✅ Version control for configs
- ✅ Audit trail

---

### 5. Agent Integration Framework

#### واجهة موحدة للوكلاء للتواصل مع البنية التحتية

```python
# core/agent_base.py
from abc import ABC, abstractmethod

class AgentBase(ABC):
    """
    Base class لجميع الوكلاء
    
    Provides:
    - Config management
    - Logging
    - Messaging
    - Secret access
    - Metrics reporting
    """
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        
        # Dependency injection
        self.config = self._get_config_manager()
        self.logger = self._get_logger()
        self.messaging = self._get_messaging()
        self.secrets = self._get_secrets_manager()
        self.telemetry = self._get_telemetry_collector()
    
    @abstractmethod
    async def start(self):
        """بدء الوكيل"""
        pass
    
    @abstractmethod
    async def stop(self):
        """إيقاف الوكيل"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """فحص صحة الوكيل"""
        pass
    
    async def get_secret(self, secret_name: str) -> str:
        """الحصول على سر بشكل آمن"""
        return await self.secrets.get_secret(secret_name)
    
    async def report_metric(self, metric_name: str, value: float, tags: dict = None):
        """إرسال metric"""
        await self.telemetry.report(
            agent=self.agent_name,
            metric=metric_name,
            value=value,
            tags=tags
        )
    
    async def send_message(self, to_agent: str, message_type: str, payload: dict):
        """إرسال رسالة لوكيل آخر"""
        await self.messaging.send(
            from_agent=self.agent_name,
            to_agent=to_agent,
            message_type=message_type,
            payload=payload
        )
```

#### Migration للوكلاء الحاليين

```python
# agents/ai_manager_v2.py
from core.agent_base import AgentBase

class AIManager(AgentBase):
    """
    AI Manager المُحدّث مع Integration Framework
    """
    
    def __init__(self):
        super().__init__("ai_manager")
        
        # باقي التهيئة...
    
    async def start(self):
        """بدء الوكيل"""
        
        # تسجيل metric
        await self.report_metric("agent_started", 1.0)
        
        # باقي الكود...
```

#### المخرجات:
- ✅ AgentBase class
- ✅ Migration guide للوكلاء الحاليين
- ✅ تحديث جميع الوكلاء الستة
- ✅ Testing framework

---

## 📊 Database Migrations

### Schema الكامل للـ Phase 0

```sql
-- migrations/phase0_001_foundation.sql

-- 1. Secrets Management
CREATE TABLE secrets_metadata (
    id SERIAL PRIMARY KEY,
    secret_name VARCHAR(100) UNIQUE NOT NULL,
    provider VARCHAR(50),
    storage_backend VARCHAR(50),
    last_rotated TIMESTAMP,
    rotation_policy_days INTEGER DEFAULT 90,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. System State
CREATE TABLE system_state (
    id SERIAL PRIMARY KEY,
    state_key VARCHAR(100) UNIQUE NOT NULL,
    state_value JSONB NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Metrics (Time-series)
CREATE TABLE metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15, 4) NOT NULL,
    unit VARCHAR(20),
    tags JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TimescaleDB (إذا مثبت)
SELECT create_hypertable('metrics', 'timestamp', if_not_exists => TRUE);

-- 4. Message Logs
CREATE TABLE message_logs (
    id SERIAL PRIMARY KEY,
    message_id VARCHAR(100),
    sender VARCHAR(100),
    receiver VARCHAR(100),
    message_type VARCHAR(50),
    payload JSONB,
    status VARCHAR(20),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Config History
CREATE TABLE config_history (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(200),
    old_value JSONB,
    new_value JSONB,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Audit Logs (من SECURITY_ARCHITECTURE)
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    actor VARCHAR(100),
    resource VARCHAR(200),
    action VARCHAR(50),
    ip_address VARCHAR(45),
    user_agent TEXT,
    success BOOLEAN,
    error_message TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_metrics_name_time ON metrics(metric_name, timestamp DESC);
CREATE INDEX idx_messages_sender ON message_logs(sender, created_at DESC);
CREATE INDEX idx_messages_receiver ON message_logs(receiver, created_at DESC);
CREATE INDEX idx_config_history_key ON config_history(config_key, changed_at DESC);
CREATE INDEX idx_audit_logs_event ON audit_logs(event_type, created_at);
CREATE INDEX idx_audit_logs_actor ON audit_logs(actor);

-- Views
CREATE VIEW suspicious_activities AS
SELECT
    actor,
    COUNT(*) as failed_attempts,
    MAX(created_at) as last_attempt
FROM audit_logs
WHERE success = FALSE
  AND created_at > NOW() - INTERVAL '1 hour'
GROUP BY actor
HAVING COUNT(*) >= 5;
```

---

## 🛠️ Dependencies الجديدة

```txt
# requirements_phase0.txt

# Secret Management
hvac==1.1.0                    # HashiCorp Vault client
cryptography==41.0.7           # Encryption

# Redis
redis[hiredis]==5.0.1          # Redis client مع hiredis للأداء

# Messaging (اختياري)
aio-pika==9.3.0                # RabbitMQ async client

# Configuration
watchdog==3.0.0                # File watching

# Time-series (اختياري)
timescaledb==0.1.1             # TimescaleDB utilities

# Async PostgreSQL
asyncpg==0.29.0                # Async PostgreSQL

# Utils
python-dotenv==1.0.0           # Environment variables
pydantic==2.5.0                # Data validation
```

---

## 📋 خطة التنفيذ (2-3 أسابيع)

### الأسبوع 1: Secrets & State Management

**أيام 1-2: Secret Management**
- [ ] تثبيت Vault على السيرفر
- [ ] إنشاء `security/vault_client.py`
- [ ] إنشاء `security/secrets_manager.py`
- [ ] Database migration للـ secrets_metadata
- [ ] اختبار التخزين والاسترجاع

**أيام 3-4: Shared State**
- [ ] تثبيت Redis
- [ ] إنشاء `core/shared_state.py`
- [ ] Database migration للـ system_state
- [ ] اختبار State management

**أيام 5-7: Telemetry**
- [ ] إنشاء `core/telemetry_collector.py`
- [ ] Database migration للـ metrics
- [ ] تثبيت TimescaleDB (optional)
- [ ] اختبار Metrics collection

### الأسبوع 2: Messaging & Configuration

**أيام 8-10: Message Queue**
- [ ] إنشاء `core/messaging/redis_queue.py`
- [ ] Database migration للـ message_logs
- [ ] Migration من Queue الحالي
- [ ] اختبار Messaging

**أيام 11-13: Configuration Management**
- [ ] إنشاء `core/config_manager.py`
- [ ] Database migration للـ config_history
- [ ] Hot reload testing
- [ ] Documentation

### الأسبوع 3: Integration & Testing

**أيام 14-16: Agent Integration Framework**
- [ ] إنشاء `core/agent_base.py`
- [ ] Migration guide للوكلاء
- [ ] تحديث وكيل واحد كـ pilot
- [ ] اختبار Integration

**أيام 17-19: Full Migration**
- [ ] تحديث جميع الوكلاء (6 وكلاء)
- [ ] End-to-end testing
- [ ] Performance testing
- [ ] Documentation

**أيام 20-21: Deployment & Validation**
- [ ] نشر على الإنتاج باستخدام Bridge Tool
- [ ] Validation tests
- [ ] Monitoring setup
- [ ] Handoff documentation

---

## ✅ معايير القبول (Definition of Done)

### Infrastructure
- [ ] Vault يعمل ويُخزن الأسرار بأمان
- [ ] Redis يعمل للـ caching & state
- [ ] Metrics يتم جمعها وتخزينها
- [ ] Message queue يعمل بشكل موثوق

### Code Quality
- [ ] جميع الكود لديه tests (coverage >80%)
- [ ] Documentation كاملة
- [ ] LSP errors = 0
- [ ] Security audit passed

### Integration
- [ ] جميع الوكلاء تستخدم AgentBase
- [ ] Secret access يعمل
- [ ] Telemetry reporting يعمل
- [ ] Inter-agent messaging يعمل

### Deployment
- [ ] منشور على الإنتاج
- [ ] systemd services تعمل
- [ ] Backups تعمل
- [ ] Monitoring active

---

## 🎯 المخرجات النهائية

بعد Phase 0، سيكون لدينا:

```
✅ Secure secret management (Vault)
✅ Shared state & caching (Redis)
✅ Metrics & telemetry (PostgreSQL + optional TimescaleDB)
✅ Reliable messaging (Redis Streams)
✅ Configuration management (Hot reload)
✅ Agent integration framework
✅ Full audit logging
✅ Security hardening

⏩ Ready for Phase 1: Model Pool Manager
```

---

**الوثيقة من إعداد:** Agent 4  
**آخر تحديث:** 2025-11-14  
**الحالة:** مُخطط 📋
