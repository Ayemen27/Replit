# 🔐 معمارية الأمان - AI Multi-Agent System

**الهدف:** تأمين شامل للنظام مع التركيز على إدارة API Keys والبيانات الحساسة

---

## 🎯 المتطلبات الأمنية

### 1. API Keys & Secrets Management
- ✅ تخزين مُشفر لجميع المفاتيح
- ✅ Rotation تلقائي للمفاتيح
- ✅ Access control (من يستطيع الوصول)
- ✅ Audit logging (تتبع كل الوصول)
- ✅ Secrets in transit encryption

### 2. Data Protection
- ✅ تشفير البيانات في قاعدة البيانات (at rest)
- ✅ تشفير البيانات أثناء النقل (in transit)
- ✅ حماية معلومات المستخدمين
- ✅ Secure backups

### 3. Access Control
- ✅ Authentication للـ Dashboard
- ✅ Authorization (RBAC)
- ✅ API rate limiting
- ✅ IP whitelisting

---

## 🏗️ البنية المعمارية الأمنية

```
┌─────────────────────────────────────────────────────────────┐
│                     SECURITY LAYER                          │
│                                                             │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │  Authentication  │  │  Authorization   │               │
│  │  (JWT/OAuth)     │  │  (RBAC)          │               │
│  └──────────────────┘  └──────────────────┘               │
└─────────────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────────────┐
│               SECRETS MANAGEMENT LAYER                      │
│                                                             │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │  Vault/KMS       │  │  Key Rotation    │               │
│  │  (HashiCorp)     │  │  Service         │               │
│  └──────────────────┘  └──────────────────┘               │
│                                                             │
│  ┌──────────────────────────────────────┐                 │
│  │       Encrypted Storage              │                 │
│  │  (PostgreSQL with encryption)        │                 │
│  └──────────────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────────────┐
│                   AUDIT & MONITORING                        │
│                                                             │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │  Audit Logs      │  │  Alert System    │               │
│  │  (Who/What/When) │  │  (Anomalies)     │               │
│  └──────────────────┘  └──────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔑 Secret Storage Solutions

### الخيار 1: HashiCorp Vault (مُوصى به للإنتاج)

```yaml
# vault-config.hcl
storage "postgresql" {
  connection_url = "postgres://vault:password@localhost:5432/vault"
}

listener "tcp" {
  address     = "127.0.0.1:8200"
  tls_disable = 1  # Enable TLS in production
}

api_addr = "http://127.0.0.1:8200"
```

```python
# security/vault_client.py
import hvac

class VaultClient:
    """
    عميل HashiCorp Vault
    """
    
    def __init__(self, url: str = "http://127.0.0.1:8200", token: str = None):
        self.client = hvac.Client(url=url, token=token)
        
    def store_secret(self, path: str, data: dict):
        """تخزين سر"""
        self.client.secrets.kv.v2.create_or_update_secret(
            path=path,
            secret=data
        )
    
    def get_secret(self, path: str) -> dict:
        """استرجاع سر"""
        response = self.client.secrets.kv.v2.read_secret_version(
            path=path
        )
        return response['data']['data']
    
    def rotate_secret(self, path: str, new_data: dict):
        """تدوير سر (إنشاء version جديدة)"""
        self.client.secrets.kv.v2.create_or_update_secret(
            path=path,
            secret=new_data
        )
```

### الخيار 2: AWS Secrets Manager (للـ AWS)

```python
# security/aws_secrets.py
import boto3
import json

class AWSSecretsManager:
    """
    عميل AWS Secrets Manager
    """
    
    def __init__(self, region: str = "us-east-1"):
        self.client = boto3.client('secretsmanager', region_name=region)
    
    def store_secret(self, name: str, value: dict):
        """تخزين سر"""
        self.client.create_secret(
            Name=name,
            SecretString=json.dumps(value)
        )
    
    def get_secret(self, name: str) -> dict:
        """استرجاع سر"""
        response = self.client.get_secret_value(SecretId=name)
        return json.loads(response['SecretString'])
    
    def rotate_secret(self, name: str):
        """تدوير سر تلقائياً"""
        self.client.rotate_secret(SecretId=name)
```

### الخيار 3: Local Encrypted Storage (للتطوير)

```python
# security/encrypted_storage.py
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64
import os
import json

class EncryptedStorage:
    """
    تخزين محلي مُشفر (للتطوير فقط)
    """
    
    def __init__(self, master_password: str = None):
        self.master_password = master_password or os.getenv("MASTER_PASSWORD")
        if not self.master_password:
            raise ValueError("MASTER_PASSWORD must be set")
        
        self.cipher = self._get_cipher()
    
    def _get_cipher(self) -> Fernet:
        """إنشاء مفتاح التشفير من كلمة المرور الرئيسية"""
        
        salt = b'ai_multi_agent_salt'  # في الإنتاج: استخدم salt عشوائي محفوظ
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(self.master_password.encode()))
        return Fernet(key)
    
    def encrypt(self, data: str) -> bytes:
        """تشفير بيانات"""
        return self.cipher.encrypt(data.encode())
    
    def decrypt(self, encrypted_data: bytes) -> str:
        """فك تشفير بيانات"""
        return self.cipher.decrypt(encrypted_data).decode()
    
    def store_secret(self, name: str, value: dict, file_path: str = ".secrets.enc"):
        """تخزين سر في ملف مُشفر"""
        
        # تحميل الأسرار الحالية
        secrets = {}
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                encrypted = f.read()
                if encrypted:
                    decrypted = self.decrypt(encrypted)
                    secrets = json.loads(decrypted)
        
        # إضافة السر الجديد
        secrets[name] = value
        
        # حفظ مع تشفير
        encrypted = self.encrypt(json.dumps(secrets))
        with open(file_path, 'wb') as f:
            f.write(encrypted)
        
        # صلاحيات 600 (read/write للمالك فقط)
        os.chmod(file_path, 0o600)
    
    def get_secret(self, name: str, file_path: str = ".secrets.enc") -> dict:
        """استرجاع سر"""
        
        if not os.path.exists(file_path):
            raise FileNotFoundError("Secrets file not found")
        
        with open(file_path, 'rb') as f:
            encrypted = f.read()
        
        decrypted = self.decrypt(encrypted)
        secrets = json.loads(decrypted)
        
        if name not in secrets:
            raise KeyError(f"Secret '{name}' not found")
        
        return secrets[name]
```

---

## 🔄 Key Rotation Strategy

```python
# security/key_rotation.py
from datetime import datetime, timedelta
from typing import Dict

class KeyRotationManager:
    """
    إدارة تدوير المفاتيح التلقائي
    """
    
    def __init__(self, storage_backend):
        self.storage = storage_backend
        self.rotation_policy = {
            'openai': 90,      # كل 90 يوم
            'anthropic': 90,
            'google': 180,     # كل 180 يوم
            'groq': 365,       # سنوياً (مجاني)
        }
    
    async def check_rotation_needed(self, provider: str) -> bool:
        """فحص إذا كان المفتاح يحتاج تدوير"""
        
        metadata = await self._get_key_metadata(provider)
        
        if not metadata:
            return False
        
        last_rotated = datetime.fromisoformat(metadata.get('last_rotated'))
        days_since = (datetime.now() - last_rotated).days
        
        rotation_days = self.rotation_policy.get(provider, 90)
        
        return days_since >= rotation_days
    
    async def rotate_key(self, provider: str, new_key: str):
        """
        تدوير مفتاح
        
        Steps:
        1. تخزين المفتاح الجديد
        2. تحديث metadata
        3. تسجيل في Audit Log
        4. إشعار المسؤول
        """
        
        # 1. تخزين المفتاح الجديد مع الاحتفاظ بالقديم (grace period)
        await self.storage.store_secret(
            f"{provider}_new",
            {"key": new_key, "created_at": datetime.now().isoformat()}
        )
        
        # 2. اختبار المفتاح الجديد
        if not await self._test_key(provider, new_key):
            raise ValueError(f"New key for {provider} failed validation")
        
        # 3. نقل القديم إلى backup
        old_key = await self.storage.get_secret(provider)
        await self.storage.store_secret(
            f"{provider}_old",
            old_key
        )
        
        # 4. ترقية المفتاح الجديد إلى الرئيسي
        await self.storage.store_secret(
            provider,
            {
                "key": new_key,
                "last_rotated": datetime.now().isoformat(),
                "rotated_by": "auto"
            }
        )
        
        # 5. Audit log
        await self._log_rotation(provider, "success")
        
        # 6. إشعار
        await self._notify_rotation(provider)
    
    async def _test_key(self, provider: str, key: str) -> bool:
        """اختبار صلاحية المفتاح"""
        
        # محاكاة اختبار (في الواقع: استدعاء API حقيقي)
        return len(key) > 10
    
    async def _log_rotation(self, provider: str, status: str):
        """تسجيل عملية التدوير في Audit Log"""
        
        # سيتم التنفيذ في قاعدة البيانات
        pass
    
    async def _notify_rotation(self, provider: str):
        """إشعار المسؤول بالتدوير"""
        
        # إرسال عبر Telegram/Email
        pass
```

---

## 📊 Audit Logging

```sql
-- Schema للـ Audit Logs

CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,  -- 'key_access', 'key_rotation', 'secret_read', etc.
    actor VARCHAR(100),                -- من قام بالعملية
    resource VARCHAR(200),             -- المورد المُستهدف (provider name, secret path)
    action VARCHAR(50),                -- 'read', 'write', 'delete', 'rotate'
    ip_address VARCHAR(45),
    user_agent TEXT,
    success BOOLEAN,
    error_message TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_event ON audit_logs(event_type, created_at);
CREATE INDEX idx_audit_logs_actor ON audit_logs(actor);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource);

-- Anomaly Detection View
CREATE VIEW suspicious_activities AS
SELECT
    actor,
    COUNT(*) as failed_attempts,
    MAX(created_at) as last_attempt
FROM audit_logs
WHERE success = FALSE
  AND created_at > NOW() - INTERVAL '1 hour'
GROUP BY actor
HAVING COUNT(*) >= 5;  -- 5+ failed attempts in 1 hour
```

```python
# security/audit_logger.py
import asyncpg
from datetime import datetime

class AuditLogger:
    """
    تسجيل جميع العمليات الأمنية
    """
    
    def __init__(self, db_pool):
        self.db = db_pool
    
    async def log_event(
        self,
        event_type: str,
        actor: str,
        resource: str,
        action: str,
        success: bool,
        ip_address: str = None,
        error_message: str = None,
        metadata: dict = None
    ):
        """تسجيل حدث أمني"""
        
        async with self.db.acquire() as conn:
            await conn.execute("""
                INSERT INTO audit_logs
                (event_type, actor, resource, action, ip_address, success, error_message, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
            event_type, actor, resource, action, ip_address, success, error_message, metadata
            )
    
    async def get_suspicious_activities(self) -> list:
        """الحصول على أنشطة مشبوهة"""
        
        async with self.db.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM suspicious_activities")
            return [dict(row) for row in rows]
```

---

## 🛡️ Authentication & Authorization

### JWT-based Authentication

```python
# security/auth.py
import jwt
from datetime import datetime, timedelta
from typing import Optional

class AuthManager:
    """
    إدارة المصادقة والتخويل
    """
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.algorithm = "HS256"
        self.access_token_expire = timedelta(hours=24)
    
    def create_token(self, user_id: str, roles: list) -> str:
        """إنشاء JWT token"""
        
        payload = {
            "sub": user_id,
            "roles": roles,
            "exp": datetime.utcnow() + self.access_token_expire,
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_token(self, token: str) -> Optional[dict]:
        """التحقق من token"""
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def has_permission(self, token: str, required_role: str) -> bool:
        """فحص الصلاحيات"""
        
        payload = self.verify_token(token)
        
        if not payload:
            return False
        
        roles = payload.get('roles', [])
        return required_role in roles or 'admin' in roles
```

### RBAC (Role-Based Access Control)

```python
# security/rbac.py
from enum import Enum

class Role(Enum):
    ADMIN = "admin"              # كل الصلاحيات
    DEVELOPER = "developer"      # تعديل الكود، الوكلاء
    OPERATOR = "operator"        # مراقبة، إعادة تشغيل
    VIEWER = "viewer"            # مشاهدة فقط

class Permission(Enum):
    VIEW_DASHBOARD = "view_dashboard"
    MANAGE_AGENTS = "manage_agents"
    MANAGE_KEYS = "manage_keys"
    VIEW_LOGS = "view_logs"
    EXECUTE_COMMANDS = "execute_commands"
    MANAGE_USERS = "manage_users"

ROLE_PERMISSIONS = {
    Role.ADMIN: [p for p in Permission],  # كل الصلاحيات
    Role.DEVELOPER: [
        Permission.VIEW_DASHBOARD,
        Permission.MANAGE_AGENTS,
        Permission.VIEW_LOGS,
        Permission.EXECUTE_COMMANDS
    ],
    Role.OPERATOR: [
        Permission.VIEW_DASHBOARD,
        Permission.MANAGE_AGENTS,
        Permission.VIEW_LOGS
    ],
    Role.VIEWER: [
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_LOGS
    ]
}

def can_perform(role: Role, permission: Permission) -> bool:
    """فحص إذا كان الدور يملك الصلاحية"""
    return permission in ROLE_PERMISSIONS.get(role, [])
```

---

## 🔒 Data Encryption

### Database Encryption (at rest)

```sql
-- تفعيل التشفير في PostgreSQL
-- 1. تشفير على مستوى الأعمدة (column-level)

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- جدول مُشفر للمفاتيح
CREATE TABLE encrypted_keys (
    id SERIAL PRIMARY KEY,
    provider VARCHAR(50) NOT NULL,
    encrypted_key BYTEA NOT NULL,  -- مُشفر
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- دوال للتشفير/فك التشفير
CREATE OR REPLACE FUNCTION encrypt_key(key_text TEXT, passphrase TEXT)
RETURNS BYTEA AS $$
BEGIN
    RETURN pgp_sym_encrypt(key_text, passphrase);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION decrypt_key(encrypted_data BYTEA, passphrase TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN pgp_sym_decrypt(encrypted_data, passphrase);
END;
$$ LANGUAGE plpgsql;
```

### Application-level Encryption

```python
# security/encryption.py
from cryptography.fernet import Fernet

class FieldEncryption:
    """
    تشفير حقول محددة في قاعدة البيانات
    """
    
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)
    
    def encrypt_field(self, value: str) -> bytes:
        """تشفير حقل"""
        return self.cipher.encrypt(value.encode())
    
    def decrypt_field(self, encrypted: bytes) -> str:
        """فك تشفير حقل"""
        return self.cipher.decrypt(encrypted).decode()
```

---

## 🌐 Network Security

### TLS/SSL Configuration

```nginx
# nginx.conf للـ Dashboard
server {
    listen 443 ssl http2;
    server_name dashboard.ai-system.com;
    
    ssl_certificate /etc/ssl/certs/ai-system.crt;
    ssl_certificate_key /etc/ssl/private/ai-system.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Headers أمنية
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Rate Limiting

```python
# api/middleware/rate_limit.py
from fastapi import Request, HTTPException
from datetime import datetime, timedelta
import redis

class RateLimiter:
    """
    تحديد معدل الطلبات
    """
    
    def __init__(self, redis_client, max_requests: int = 100, window_seconds: int = 60):
        self.redis = redis_client
        self.max_requests = max_requests
        self.window = window_seconds
    
    async def check_limit(self, identifier: str) -> bool:
        """
        فحص إذا تجاوز المستخدم الحد
        
        Args:
            identifier: IP أو user_id
        """
        
        key = f"rate_limit:{identifier}"
        
        current = await self.redis.get(key)
        
        if current is None:
            await self.redis.setex(key, self.window, 1)
            return True
        
        if int(current) >= self.max_requests:
            return False
        
        await self.redis.incr(key)
        return True
```

---

## 📋 Security Checklist

### قبل النشر في الإنتاج

- [ ] جميع API Keys مُشفرة ومُخزنة في Vault
- [ ] HTTPS مُفعّل على جميع endpoints
- [ ] Authentication & Authorization مُطبّقة
- [ ] Audit logging يعمل لجميع العمليات الحساسة
- [ ] Rate limiting مُفعّل
- [ ] Database encryption مُفعّل
- [ ] Key rotation مُجدول
- [ ] Backups مُشفرة
- [ ] Firewall rules مُطبّقة
- [ ] Security monitoring نشط

---

## 🚨 Incident Response Plan

### في حالة اختراق محتمل

1. **عزل فوري:**
   - إيقاف جميع الوكلاء
   - قطع الاتصال بالإنترنت
   - حفظ السجلات

2. **التحقيق:**
   - فحص Audit logs
   - تحديد نقطة الاختراق
   - تقييم الضرر

3. **الإصلاح:**
   - تدوير جميع API Keys
   - تحديث كلمات المرور
   - patch الثغرات

4. **الاستعادة:**
   - استعادة من backup آمن
   - التحقق من السلامة
   - إعادة التشغيل التدريجي

5. **التقرير:**
   - توثيق الحادثة
   - تحديث إجراءات الأمان
   - تدريب الفريق

---

**الوثيقة من إعداد:** Agent 4  
**آخر تحديث:** 2025-11-14  
**الحالة:** للمراجعة ✅
