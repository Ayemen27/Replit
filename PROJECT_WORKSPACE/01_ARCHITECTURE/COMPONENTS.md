# مكونات النظام (System Components)

## 1. نظرة عامة

هذا المستند يوثق جميع المكونات الرئيسية للمنصة وكيفية تفاعلها.

---

## 2. المكونات الرئيسية

### Frontend (الواجهة الأمامية)

#### Dashboard Web App
```yaml
technology: Next.js 14 + React 18
hosting: Vercel / Cloudflare Pages
features:
  - مشاريع المستخدم
  - إدارة الوكلاء (Agents)
  - مراقبة الأداء (Monitoring)
  - إدارة السيرفرات
  
routes:
  - /dashboard - لوحة التحكم الرئيسية
  - /projects - إدارة المشاريع
  - /agents - إدارة الوكلاء
  - /servers - السيرفرات المربوطة
  - /settings - الإعدادات
```

#### Component Architecture
```
src/
├── components/       # مكونات React قابلة لإعادة الاستخدام
├── pages/           # صفحات Next.js
├── lib/             # أدوات ومكتبات
├── hooks/           # Custom React hooks
├── contexts/        # React contexts للحالة العامة
└── styles/          # CSS/Tailwind styles
```

---

### Backend (الخادم الخلفي)

#### API Server
```yaml
technology: FastAPI (Python 3.11)
database: PostgreSQL 15
cache: Redis 7
authentication: JWT + OAuth2

endpoints:
  auth:
    - POST /auth/login
    - POST /auth/register
    - POST /auth/refresh
    - POST /auth/logout
    
  projects:
    - GET    /projects
    - POST   /projects
    - GET    /projects/{id}
    - PUT    /projects/{id}
    - DELETE /projects/{id}
    
  agents:
    - GET    /agents
    - POST   /agents
    - GET    /agents/{id}/status
    - POST   /agents/{id}/execute
    - DELETE /agents/{id}/jobs/{job_id}
    
  servers:
    - GET    /servers
    - POST   /servers/link
    - DELETE /servers/{id}
    - GET    /servers/{id}/health
```

#### Database Schema
```sql
-- المستخدمون
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    mfa_enabled BOOLEAN DEFAULT FALSE
);

-- المشاريع
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- السيرفرات
CREATE TABLE servers (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    name VARCHAR(255),
    ip_address INET NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    bridge_token TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- الوكلاء
CREATE TABLE agents (
    id UUID PRIMARY KEY,
    server_id UUID REFERENCES servers(id),
    type VARCHAR(100) NOT NULL,
    config JSONB,
    status VARCHAR(50) DEFAULT 'stopped',
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

### Bridge Daemon (جسر الاتصال)

```yaml
purpose: الاتصال بين المنصة والسيرفر البعيد
technology: Python + asyncio
installation: systemd service على VPS المستخدم

components:
  websocket_client:
    - اتصال دائم بالمنصة
    - heartbeat كل 30 ثانية
    - reconnection تلقائي
    
  command_executor:
    - تنفيذ أوامر آمنة
    - sandboxing
    - logging شامل
    
  file_watcher:
    - مراقبة ملفات المشروع
    - sync تلقائي
    - conflict resolution
```

راجع [02_INTEGRATION_PLAN/BRIDGE_TOOL.md](../02_INTEGRATION_PLAN/BRIDGE_TOOL.md) للتفاصيل.

---

### AI Agents (الوكلاء الذكية)

```yaml
types:
  monitoring_agent:
    purpose: مراقبة صحة التطبيقات
    frequency: كل دقيقة
    actions:
      - check /health endpoint
      - alert on failures
      
  backup_agent:
    purpose: نسخ احتياطي تلقائي
    frequency: يومياً
    actions:
      - backup database
      - upload to S3
      - verify integrity
      
  security_agent:
    purpose: مراقبة أمنية
    frequency: مستمر
    actions:
      - scan logs للأنشطة المشبوهة
      - block IPs المشبوهة
      - alert on threats
```

راجع [03_SYSTEMS/01_Agents/](../03_SYSTEMS/01_Agents/) للتفاصيل.

---

### Docker Manager

```yaml
purpose: إدارة حاويات Docker للمشاريع
technology: Docker SDK for Python

features:
  - إنشاء حاويات معزولة
  - تحديد الموارد (CPU, Memory)
  - بث السجلات مباشرة
  - تنظيف تلقائي
  
security:
  - user namespaces
  - network isolation
  - resource limits
  - read-only filesystems
```

راجع [03_SYSTEMS/04_Docker_Management/](../03_SYSTEMS/04_Docker_Management/) للتفاصيل.

---

## 3. التدفق المعماري (Architecture Flow)

```
┌─────────────┐
│  المستخدم   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Dashboard      │  (Next.js)
│  (Frontend)     │
└────────┬────────┘
         │ HTTPS/WSS
         ▼
┌──────────────────┐
│  API Server      │  (FastAPI)
│  (Backend)       │
└─────┬─────┬──────┘
      │     │
      │     └──► PostgreSQL (قاعدة البيانات)
      │     └──► Redis (Cache)
      │
      │ WSS (WebSocket Secure)
      ▼
┌──────────────────┐
│  Bridge Daemon   │  (على VPS المستخدم)
└─────┬────────────┘
      │
      ├──► Docker Manager
      ├──► File System
      └──► AI Agents
```

---

## 4. الاتصالات (Communication Patterns)

### REST API
```
Frontend ←→ Backend (HTTP/HTTPS)
- GET/POST/PUT/DELETE requests
- JWT authentication
- JSON responses
```

### WebSocket
```
Backend ←→ Bridge Daemon (WSS)
- Real-time bi-directional
- Command execution
- Log streaming
- Status updates
```

### Message Queue (اختياري)
```
Backend → Redis Pub/Sub → Workers
- Async job processing
- Background tasks
- Agent scheduling
```

---

## 5. الأمان (Security)

### Authentication Flow
```
1. User → Login (email + password)
2. Backend → Verify credentials
3. Backend → Generate JWT (access + refresh)
4. Frontend → Store tokens (httpOnly cookies)
5. Frontend → Include token في requests
6. Backend → Validate token
```

### Authorization
```yaml
roles:
  admin:
    - full access
    - user management
    - system config
    
  user:
    - own projects only
    - own servers only
    - own agents only
    
  agent:
    - execute commands
    - read/write files
    - no admin access
```

---

## 6. القابلية للتوسع (Scalability)

### Horizontal Scaling
- API Server: متعدد instances خلف Load Balancer
- Database: PostgreSQL replication
- Cache: Redis cluster

### Vertical Scaling
- زيادة resources للـ containers
- Optimize database queries
- CDN للـ static assets

---

## 7. الوثائق ذات الصلة

- [SYSTEM_OVERVIEW.md](./SYSTEM_OVERVIEW.md) - نظرة عامة على النظام
- [02_INTEGRATION_PLAN/](../02_INTEGRATION_PLAN/) - خطط التكامل
- [03_SYSTEMS/](../03_SYSTEMS/) - تفاصيل الأنظمة الفرعية
- [04_SECURITY/](../04_SECURITY/) - سياسات الأمان

---

**آخر تحديث**: 2025-11-18  
**المسؤول**: Architecture Team
