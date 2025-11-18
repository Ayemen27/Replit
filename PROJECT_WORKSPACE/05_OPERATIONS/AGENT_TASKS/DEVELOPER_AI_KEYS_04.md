# 📊 Developer AI-Keys-04: Monitoring Dashboard

> **📍 المهمة**: بناء dashboard متكامل لمراقبة وإدارة مفاتيح API

**الأولوية**: 🟢🟢🟢 (منخفضة - Nice to have)  
**المدة المتوقعة**: 3-4 أيام  
**المتطلبات السابقة**: ✅ AI-Keys-01, 02, 03 مكتملين  
**المخرجات**: واجهة ويب شاملة لمراقبة وإدارة المفاتيح

---

## 📋 الهدف

بناء **dashboard متكامل** يعرض:
- حالة جميع المفاتيح (live status)
- إحصائيات الاستخدام (usage stats)
- رسوم بيانية (charts)
- إدارة المفاتيح (add/edit/delete)
- تنبيهات (alerts history)

### الشكل المطلوب

```
/admin/api-keys
┌──────────────────────────────────────────────────────────┐
│ 🔑 API Keys Management Dashboard                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ 📊 Overview (Last 24 hours)                             │
│ ┌────────────────────────────────────────────────────┐  │
│ │ Total Requests: 1,234   Success Rate: 99.03%      │  │
│ │ Total Tokens: 45,678    Avg Latency: 1.2s         │  │
│ └────────────────────────────────────────────────────┘  │
│                                                          │
│ 🟢 Groq (3 keys) - Health: 95%                          │
│ ┌────────────────────────────────────────────────────┐  │
│ │ Key 1 (Primary)        ████████░░ 80% (11.5K/14.4K)│✅│
│ │ Key 2 (Backup)         ██████████ 100% (exhausted) │🔴│
│ │ Key 3 (Emergency)      ███░░░░░░░ 30% (4.3K/14.4K) │✅│
│ │ Resets in: 4h 23m                                  │  │
│ └────────────────────────────────────────────────────┘  │
│                                                          │
│ 🟢 Gemini (2 keys) - Health: 100%                       │
│ ┌────────────────────────────────────────────────────┐  │
│ │ Key 1                  ████░░░░░░ 40% (600/1500)   │✅│
│ │ Key 2                  █░░░░░░░░░ 10% (150/1500)   │✅│
│ │ Resets in: 4h 23m                                  │  │
│ └────────────────────────────────────────────────────┘  │
│                                                          │
│ 📈 Usage Graph (Last 7 days)                            │
│ [Interactive Chart]                                     │
│                                                          │
│ [Add New Key] [Refresh] [Export Report] [Settings]     │
└──────────────────────────────────────────────────────────┘
```

---

## 🎯 المخرجات المطلوبة

### ✅ Acceptance Criteria

1. ✅ **Real-time Status**:
   - عرض جميع المفاتيح مع حالتها الحالية
   - تحديث تلقائي (polling كل 30 ثانية أو WebSocket)
   - Status indicators (🟢✅ healthy, 🟡⚠️ warning, 🔴❌ critical)

2. ✅ **Usage Statistics**:
   - استهلاك كل مفتاح (tokens, requests)
   - Health score لكل provider
   - Avg latency
   - Success rate

3. ✅ **Visualizations**:
   - Progress bars للـ quota
   - Line charts للاستخدام (last 7 days)
   - Pie chart لتوزيع الاستخدام بين providers

4. ✅ **Key Management**:
   - عرض معلومات المفتاح (مخفية بشكل جزئي)
   - إضافة مفتاح جديد
   - تعديل Priority/Daily Limit
   - حذف مفتاح (بتأكيد)
   - اختبار مفتاح (test ping)

5. ✅ **Alerts History**:
   - عرض آخر 20 تنبيه
   - Filter حسب النوع (warning, critical, etc)
   - تفاصيل كل تنبيه

---

## 📝 المهام التفصيلية

### Task 1: Backend API Endpoints (1-1.5 يوم)

**الملف**: `ServerAutomationAI/dev_platform/web/api_server.py` (أو ملف جديد)

#### 1.1 GET /api/admin/keys/overview

```python
@app.route("/api/admin/keys/overview")
@require_admin
def get_keys_overview():
    """
    Get overview of all keys and stats
    
    Response:
    {
        "stats": {
            "total_requests_24h": 1234,
            "total_tokens_24h": 45678,
            "success_rate": 99.03,
            "avg_latency": 1.2
        },
        "providers": {
            "groq": {
                "health": 95,
                "keys_count": 3,
                "keys": [
                    {
                        "id": 1,
                        "priority": 1,
                        "daily_limit": 14400,
                        "key_preview": "sk-proj-AAA...xyz",
                        "quota": {
                            "used": 11520,
                            "limit": 14400,
                            "remaining": 2880,
                            "percentage": 80.0,
                            "status": "warning",
                            "resets_at": "2025-11-19T00:00:00Z"
                        },
                        "health_score": 95,
                        "avg_latency": 1.1
                    }
                ]
            },
            "gemini": {...}
        },
        "last_updated": "2025-11-18T14:23:00Z"
    }
    """
    from dev_platform.core.model_router import ModelRouter
    from dev_platform.core.quota_tracker import get_quota_tracker
    
    router = ModelRouter()
    quota_tracker = get_quota_tracker()
    
    # Collect stats
    stats = router.cache.cache_get("usage_stats_24h") or {
        "total_requests_24h": 0,
        "total_tokens_24h": 0,
        "success_rate": 100.0,
        "avg_latency": 0.0
    }
    
    # Collect providers info
    providers = {}
    for provider_name in ["groq", "gemini", "mistral"]:
        keys = router.secrets.get_provider_keys(provider_name)
        
        if not keys:
            continue
        
        # Get health for provider
        health_scores = [
            router.health_scores.get(f"{provider_name}_key{k['id']}", 100)
            for k in keys
        ]
        avg_health = sum(health_scores) / len(health_scores) if health_scores else 100
        
        # Get quota for each key
        keys_with_quota = []
        for key_info in keys:
            quota = quota_tracker.get_remaining_quota(
                provider_name,
                key_info["id"],
                key_info["daily_limit"]
            )
            
            # Get latency
            latency_key = f"latency_{provider_name}_key{key_info['id']}"
            avg_latency = router.cache.cache_get(latency_key) or 1.0
            
            keys_with_quota.append({
                "id": key_info["id"],
                "priority": key_info["priority"],
                "daily_limit": key_info["daily_limit"],
                "key_preview": _mask_api_key(key_info["key"]),
                "quota": quota,
                "health_score": router.health_scores.get(
                    f"{provider_name}_key{key_info['id']}", 100
                ),
                "avg_latency": round(avg_latency, 2)
            })
        
        providers[provider_name] = {
            "health": round(avg_health),
            "keys_count": len(keys),
            "keys": keys_with_quota
        }
    
    return jsonify({
        "stats": stats,
        "providers": providers,
        "last_updated": datetime.now(timezone.utc).isoformat()
    })

def _mask_api_key(key: str) -> str:
    """Mask API key for display (show first 10 and last 4)"""
    if len(key) <= 14:
        return key[:3] + "..." + key[-2:]
    return key[:10] + "..." + key[-4:]
```

#### 1.2 GET /api/admin/keys/history

```python
@app.route("/api/admin/keys/history")
@require_admin
def get_usage_history():
    """
    Get usage history for charts (last 7 days)
    
    Response:
    {
        "daily_usage": [
            {
                "date": "2025-11-12",
                "groq": 12345,
                "gemini": 5678,
                "mistral": 2345
            },
            ...
        ]
    }
    """
    # Implementation using cache data
    ...
```

#### 1.3 POST /api/admin/keys/add

```python
@app.route("/api/admin/keys/add", methods=["POST"])
@require_admin
def add_new_key():
    """
    Add a new API key
    
    Request:
    {
        "provider": "groq",
        "key": "sk-proj-xxx",
        "priority": 2,
        "daily_limit": 14400
    }
    """
    data = request.json
    provider = data["provider"]
    key = data["key"]
    priority = data.get("priority", 99)
    daily_limit = data.get("daily_limit", 14400)
    
    # Validate key with test ping
    router = ModelRouter()
    model_config = {
        "provider": provider,
        "model": _get_model_for_provider(provider),
        "key": key
    }
    
    if not router._test_ping_with_key(model_config):
        return jsonify({"error": "Key validation failed"}), 400
    
    # Find next available ID
    existing_keys = router.secrets.get_provider_keys(provider)
    next_id = max([k["id"] for k in existing_keys], default=0) + 1
    
    # Save to secrets
    router.secrets.set(f"{provider.upper()}_API_KEY_{next_id}", key)
    router.secrets.set(f"{provider.upper()}_KEY_{next_id}_PRIORITY", str(priority))
    router.secrets.set(f"{provider.upper()}_KEY_{next_id}_DAILY_LIMIT", str(daily_limit))
    
    # Reload router
    router._check_available_models()
    
    return jsonify({"success": True, "key_id": next_id})
```

#### 1.4 DELETE /api/admin/keys/delete

```python
@app.route("/api/admin/keys/delete", methods=["DELETE"])
@require_admin
def delete_key():
    """
    Delete an API key
    
    Request:
    {
        "provider": "groq",
        "key_id": 2
    }
    """
    data = request.json
    provider = data["provider"]
    key_id = data["key_id"]
    
    # Delete from secrets
    router = ModelRouter()
    router.secrets.delete(f"{provider.upper()}_API_KEY_{key_id}")
    router.secrets.delete(f"{provider.upper()}_KEY_{key_id}_PRIORITY")
    router.secrets.delete(f"{provider.upper()}_KEY_{key_id}_DAILY_LIMIT")
    
    # Reload
    router._check_available_models()
    
    return jsonify({"success": True})
```

---

### Task 2: Frontend Component (2-2.5 أيام)

**الملف**: `SaaSBoilerplate/src/pages/admin/api-keys.tsx` (أو مشابه)

#### 2.1 Main Dashboard Component

```typescript
// api-keys.tsx

import React, { useState, useEffect } from 'react';
import {
  Card,
  Progress,
  Badge,
  Button,
  Modal,
  Form,
  Input,
  Select,
  Table,
  Statistic,
  Row,
  Col,
  Alert
} from 'antd';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';

interface KeyInfo {
  id: number;
  priority: number;
  daily_limit: number;
  key_preview: string;
  quota: {
    used: number;
    limit: number;
    remaining: number;
    percentage: number;
    status: string;
    resets_at: string;
  };
  health_score: number;
  avg_latency: number;
}

interface ProviderInfo {
  health: number;
  keys_count: number;
  keys: KeyInfo[];
}

export default function APIKeysManagement() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [addKeyModal, setAddKeyModal] = useState(false);
  
  // Fetch data
  useEffect(() => {
    loadData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);
  
  const loadData = async () => {
    try {
      const res = await fetch('/api/admin/keys/overview');
      const json = await res.json();
      setData(json);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load keys data:', error);
    }
  };
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <div className="api-keys-dashboard">
      <h1>🔑 API Keys Management</h1>
      
      {/* Overview Stats */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total Requests (24h)"
              value={data.stats.total_requests_24h}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total Tokens (24h)"
              value={data.stats.total_tokens_24h}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Success Rate"
              value={data.stats.success_rate}
              suffix="%"
              precision={2}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Avg Latency"
              value={data.stats.avg_latency}
              suffix="s"
              precision={2}
            />
          </Card>
        </Col>
      </Row>
      
      {/* Providers */}
      {Object.entries(data.providers).map(([provider, info]: [string, any]) => (
        <ProviderCard
          key={provider}
          provider={provider}
          info={info}
          onRefresh={loadData}
        />
      ))}
      
      {/* Add Key Button */}
      <Button
        type="primary"
        onClick={() => setAddKeyModal(true)}
      >
        Add New Key
      </Button>
      
      {/* Add Key Modal */}
      <AddKeyModal
        visible={addKeyModal}
        onClose={() => setAddKeyModal(false)}
        onSuccess={loadData}
      />
    </div>
  );
}

// Provider Card Component
function ProviderCard({ provider, info, onRefresh }) {
  const healthColor = info.health >= 80 ? 'success' : info.health >= 50 ? 'warning' : 'error';
  
  return (
    <Card
      title={
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span>
            {provider.toUpperCase()} ({info.keys_count} keys)
          </span>
          <Badge
            status={healthColor}
            text={`Health: ${info.health}%`}
          />
        </div>
      }
      style={{ marginBottom: 16 }}
    >
      {info.keys.map((key: KeyInfo) => (
        <KeyRow
          key={key.id}
          provider={provider}
          keyInfo={key}
          onRefresh={onRefresh}
        />
      ))}
    </Card>
  );
}

// Key Row Component
function KeyRow({ provider, keyInfo, onRefresh }) {
  const { quota, health_score } = keyInfo;
  
  // Status color
  const statusColors = {
    healthy: 'success',
    warning: 'warning',
    critical: 'error',
    exhausted: 'default'
  };
  
  const progressColor = {
    healthy: '#52c41a',
    warning: '#faad14',
    critical: '#ff4d4f',
    exhausted: '#d9d9d9'
  };
  
  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
        <span>
          <strong>Key {keyInfo.id}</strong> (Priority {keyInfo.priority})
          <Badge
            status={statusColors[quota.status]}
            text={quota.status}
            style={{ marginLeft: 8 }}
          />
        </span>
        <span style={{ fontSize: 12, color: '#999' }}>
          {quota.used.toLocaleString()} / {quota.limit.toLocaleString()} tokens
        </span>
      </div>
      
      <Progress
        percent={quota.percentage}
        strokeColor={progressColor[quota.status]}
        format={() => `${quota.percentage.toFixed(1)}%`}
      />
      
      <div style={{ fontSize: 12, color: '#666', marginTop: 4 }}>
        Remaining: {quota.remaining.toLocaleString()} | 
        Health: {health_score}% | 
        Latency: {keyInfo.avg_latency}s | 
        Resets at: {new Date(quota.resets_at).toLocaleTimeString()}
      </div>
    </div>
  );
}

// Add Key Modal
function AddKeyModal({ visible, onClose, onSuccess }) {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  
  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      const res = await fetch('/api/admin/keys/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values)
      });
      
      if (res.ok) {
        message.success('Key added successfully');
        form.resetFields();
        onClose();
        onSuccess();
      } else {
        message.error('Failed to add key');
      }
    } catch (error) {
      message.error('Error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Modal
      title="Add New API Key"
      visible={visible}
      onCancel={onClose}
      footer={null}
    >
      <Form form={form} onFinish={handleSubmit} layout="vertical">
        <Form.Item
          label="Provider"
          name="provider"
          rules={[{ required: true }]}
        >
          <Select>
            <Select.Option value="groq">Groq</Select.Option>
            <Select.Option value="gemini">Gemini</Select.Option>
            <Select.Option value="mistral">Mistral</Select.Option>
          </Select>
        </Form.Item>
        
        <Form.Item
          label="API Key"
          name="key"
          rules={[{ required: true }]}
        >
          <Input.Password placeholder="sk-proj-..." />
        </Form.Item>
        
        <Form.Item
          label="Priority"
          name="priority"
          initialValue={99}
        >
          <Input type="number" />
        </Form.Item>
        
        <Form.Item
          label="Daily Limit (tokens)"
          name="daily_limit"
          initialValue={14400}
        >
          <Input type="number" />
        </Form.Item>
        
        <Button type="primary" htmlType="submit" loading={loading}>
          Add Key
        </Button>
      </Form>
    </Modal>
  );
}
```

---

## 🧪 Testing Checklist

### ✅ Backend Tests

- [ ] Test GET /api/admin/keys/overview
- [ ] Test POST /api/admin/keys/add (valid key)
- [ ] Test POST /api/admin/keys/add (invalid key)
- [ ] Test DELETE /api/admin/keys/delete
- [ ] Test GET /api/admin/keys/history

### ✅ Frontend Tests

- [ ] Dashboard loads successfully
- [ ] Stats display correctly
- [ ] Progress bars update
- [ ] Add key modal works
- [ ] Auto-refresh works (30s)
- [ ] Responsive design (mobile/tablet)

### ✅ Integration Tests

- [ ] Add key → appears in dashboard
- [ ] Delete key → removed from dashboard
- [ ] Quota updates reflect in real-time
- [ ] Health score changes reflected

---

## 📦 Deliverables

1. ✅ Backend API endpoints (5+ endpoints)
2. ✅ Frontend dashboard component
3. ✅ Charts and visualizations
4. ✅ Add/Edit/Delete key functionality
5. ✅ Real-time updates (polling or WebSocket)
6. ✅ Responsive design
7. ✅ All tests passing

---

## 🚀 Final Handoff

بعد إكمال جميع مهام AI-Keys (01-04)، النظام سيكون:
✅ **Multi-Key Support** - دعم مفاتيح متعددة  
✅ **Quota Tracking** - تتبع دقيق للاستهلاك  
✅ **Notifications** - إشعارات فورية  
✅ **Dashboard** - مراقبة شاملة

**النتيجة**: نظام إدارة مفاتيح API احترافي وقوي! 🎉

---

**آخر تحديث**: 2025-11-18  
**الحالة**: 🟡 جاهز للتنفيذ (بعد AI-Keys-01, 02, 03)
