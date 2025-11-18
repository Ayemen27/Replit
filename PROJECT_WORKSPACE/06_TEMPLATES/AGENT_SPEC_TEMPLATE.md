# Agent Specification: <اسم الوكيل>

## 1. نظرة عامة (Overview)

### الهدف (Purpose)
وصف موجز بـ 2-3 جمل يشرح دور هذا الوكيل والمشكلة التي يحلها.

### النطاق (Scope)

#### ما يفعله (In Scope)
- ✅ وظيفة 1
- ✅ وظيفة 2
- ✅ وظيفة 3

#### ما لا يفعله (Out of Scope)
- ❌ وظيفة خارج النطاق 1
- ❌ وظيفة خارج النطاق 2

---

## 2. المدخلات والمخرجات (Inputs & Outputs)

### المدخلات (Inputs)

#### API Endpoint
```
POST /agents/<agent-id>/execute
```

#### Request Body
```json
{
  "action": "string",
  "payload": {
    "param1": "value1",
    "param2": 123
  },
  "options": {
    "timeout": 30,
    "async": false
  }
}
```

#### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | Yes | نوع الإجراء المطلوب |
| `payload` | object | Yes | البيانات المطلوبة للتنفيذ |
| `timeout` | integer | No | مهلة التنفيذ بالثواني (default: 30) |

### المخرجات (Outputs)

#### Success Response (200 OK)
```json
{
  "job_id": "uuid",
  "status": "completed",
  "result": {
    "data": "...",
    "summary": "..."
  },
  "execution_time_ms": 1234
}
```

#### Error Response (4xx/5xx)
```json
{
  "error": "error_code",
  "message": "وصف الخطأ",
  "details": {}
}
```

---

## 3. الواجهات (APIs)

### REST API

#### Execute Action
```
POST /agents/<agent-id>/execute
Authorization: Bearer <jwt-token>
Content-Type: application/json

Body: {
  "action": "analyze",
  "payload": {...}
}

Response: {
  "job_id": "...",
  "status": "running"
}
```

#### Get Status
```
GET /agents/<agent-id>/jobs/<job-id>
Authorization: Bearer <jwt-token>

Response: {
  "status": "completed",
  "result": {...}
}
```

#### Cancel Job
```
DELETE /agents/<agent-id>/jobs/<job-id>
Authorization: Bearer <jwt-token>

Response: {
  "status": "cancelled"
}
```

### WebSocket (للتحديثات الحية)
```javascript
ws://platform.com/agents/<agent-id>/stream
Headers: {
  "Authorization": "Bearer <jwt-token>"
}

// Messages:
{
  "type": "progress",
  "data": {
    "percentage": 45,
    "message": "Processing..."
  }
}
```

---

## 4. الصلاحيات والأمان (Permissions & Security)

### صلاحيات التشغيل (Execution Permissions)
- **User**: `agent-runner` (UID: 1001)
- **Group**: `agents` (GID: 1001)
- **Capabilities**: `CAP_NET_BIND_SERVICE` فقط

### الأوامر المسموحة (Allowed Commands)
```bash
# Whitelist:
- docker ps
- docker logs <container>
- systemctl status <service>

# Blacklist:
- rm -rf /
- dd if=/dev/zero
- shutdown
```

### تقييد الموارد (Resource Limits)
```yaml
limits:
  memory: 512MB
  cpu: 0.5 cores
  disk_write: 100MB/s
  network: 10Mbps
```

### Audit Logging
- جميع الأوامر المُنفذة تُسجل
- الصلاحيات تُتحقق قبل التنفيذ
- الفشل يُسجل ويُشعر المسؤولين

---

## 5. التبعيات (Dependencies)

### Runtime Dependencies
- **Python**: >= 3.9
- **Docker**: >= 20.10
- **Git**: >= 2.30

### External Services
- **Database**: PostgreSQL 14+
- **Message Queue**: Redis 6+ (optional)
- **Storage**: Local filesystem or S3-compatible

### Python Packages
```txt
requests==2.31.0
docker==7.0.0
psycopg2-binary==2.9.9
```

---

## 6. معايير القبول (Acceptance Criteria)

### Functional
- [ ] الوكيل ينفذ جميع الـ actions المحددة بنجاح
- [ ] Error handling شامل لجميع الحالات
- [ ] Timeout handling يعمل بشكل صحيح

### Non-Functional
- [ ] Unit test coverage >= 90%
- [ ] Integration tests للسيناريوهات الأساسية
- [ ] زمن الاستجابة < 2 ثانية (95th percentile)
- [ ] استهلاك الذاكرة < 512MB

### Security
- [ ] لا execution بصلاحيات root
- [ ] جميع الأوامر في whitelist
- [ ] Audit logs شاملة
- [ ] Input validation صارم

---

## 7. ملاحظات التشغيل (Operational Notes)

### Deployment
```bash
# تثبيت:
pip install -r requirements.txt
python setup.py install

# تشغيل:
agent-runner --config config.yaml

# Systemd service:
systemctl start agent-<name>
```

### Monitoring
- **Metrics**: 
  - Execution count
  - Error rate
  - Average execution time
  - Resource usage
- **Alerts**:
  - Error rate > 5%
  - Memory usage > 80%
  - Execution time > 10s

### Troubleshooting
| مشكلة | الحل |
|------|------|
| الوكيل لا يستجيب | تحقق من logs: `journalctl -u agent-<name>` |
| Permission denied | تحقق من صلاحيات المستخدم |
| Timeout errors | زد قيمة timeout في config |

---

## 8. الاختبار (Testing)

### Unit Tests
```bash
pytest tests/unit/test_agent_<name>.py -v
```

### Integration Tests
```bash
pytest tests/integration/test_agent_<name>_integration.py -v
```

### Manual Testing
```bash
# اختبار يدوي:
curl -X POST http://localhost:8000/agents/<agent-id>/execute \
  -H "Authorization: Bearer <token>" \
  -d '{"action": "test", "payload": {}}'
```

---

## 9. الوثائق ذات الصلة (Related Documentation)

- [System Overview](../../01_ARCHITECTURE/SYSTEM_OVERVIEW.md)
- [Security Policy](../../04_SECURITY/SECURITY_POLICY.md)
- [API Documentation](./agents-api.md)

---

**تاريخ الإنشاء**: YYYY-MM-DD  
**آخر تحديث**: YYYY-MM-DD  
**المسؤول**: [اسم الفريق]  
**الحالة**: [Draft / In Review / Approved / Deprecated]
