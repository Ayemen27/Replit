# 📊 Monitoring & Alerting System

## نظرة عامة

**Monitoring & Alerting** هو نظام المراقبة والإنذار الذي يتتبع صحة السيرفرات والتطبيقات ويرسل تنبيهات عند حدوث مشاكل.

---

## المكونات

### 1. Server Monitoring
```yaml
التقنية: WebSocket + Telemetry Collection
المسؤولية: مراقبة موارد السيرفر
```

**المقاييس المراقبة:**
- **CPU**: الاستخدام الحالي، المتوسط، الذروة
- **RAM**: المستخدم، المتاح، النسبة المئوية
- **Disk**: المساحة المستخدمة، المتاحة، I/O
- **Network**: Upload/Download speed، Bandwidth
- **Uptime**: مدة تشغيل السيرفر

### 2. Application Monitoring
```yaml
المسؤولية: مراقبة التطبيقات والخدمات
```

**المقاييس:**
- **Response Time**: سرعة الاستجابة
- **Error Rate**: معدل الأخطاء
- **Request Count**: عدد الطلبات
- **Database Queries**: أداء قاعدة البيانات
- **API Endpoints**: حالة الـ endpoints

### 3. AI Agents Monitoring
```yaml
المسؤولية: مراقبة حالة الوكلاء الذكية
```

**المقاييس:**
- حالة كل وكيل (Active, Idle, Error)
- عدد المهام المنفذة
- معدل النجاح/الفشل
- وقت الاستجابة
- استهلاك الموارد

### 4. Alerting System
```yaml
المسؤولية: إرسال تنبيهات عند المشاكل
```

**قنوات الإشعارات:**
- **Email**: للتنبيهات المهمة
- **In-App Notifications**: داخل Dashboard
- **Webhooks**: للتكامل مع أدوات خارجية
- **SMS** (اختياري): للحالات الحرجة

### 5. Dashboard Visualization
```yaml
التقنية: Chart.js / Recharts
المسؤولية: عرض البيانات بصرياً
```

**أنواع الرسوم:**
- Line charts (للاتجاهات الزمنية)
- Bar charts (للمقارنات)
- Pie charts (للتوزيعات)
- Gauges (للقيم الحالية)
- Heatmaps (لتحديد الأنماط)

---

## البنية المعمارية

```
src/
├── components/features/Monitoring/
│   ├── ServerMetrics.tsx       # عرض مقاييس السيرفر
│   ├── CPUChart.tsx            # رسم بياني للـ CPU
│   ├── MemoryChart.tsx         # رسم بياني للذاكرة
│   ├── DiskChart.tsx           # رسم بياني للقرص
│   ├── NetworkChart.tsx        # رسم بياني للشبكة
│   ├── AlertsList.tsx          # قائمة التنبيهات
│   └── AgentStatus.tsx         # حالة الوكلاء
│
├── lib/monitoring/
│   ├── metricsCollector.ts     # جمع المقاييس
│   ├── alertEngine.ts          # محرك التنبيهات
│   └── thresholds.ts           # عتبات التنبيه
│
└── api/monitoring/
    ├── route.ts                # API endpoints
    └── websocket.ts            # WebSocket للبيانات الحية
```

---

## التكامل مع الأنظمة الأخرى

### مع Bridge Coordination:
```typescript
// استقبال telemetry من Bridge Daemon
import { useTelemetry } from '@/hooks/useTelemetry'

const { metrics, subscribe } = useTelemetry()

subscribe('server:metrics', (data) => {
  updateCharts(data)
  checkThresholds(data)
})
```

### مع Alert System:
```typescript
// إرسال تنبيه عند تجاوز عتبة
import { useAlerts } from '@/hooks/useAlerts'

const { sendAlert } = useAlerts()

const checkThresholds = (metrics: ServerMetrics) => {
  if (metrics.cpu > 90) {
    sendAlert({
      level: 'critical',
      title: 'CPU Usage High',
      message: `CPU usage at ${metrics.cpu}%`,
      server: metrics.serverId
    })
  }
}
```

### مع Agents System:
```typescript
// مراقبة حالة الوكلاء
import { useAgentStatus } from '@/hooks/useAgents'

const { agents, getStatus } = useAgentStatus()

agents.forEach((agent) => {
  if (agent.status === 'error') {
    sendAlert({
      level: 'warning',
      title: `Agent ${agent.name} Failed`,
      message: agent.lastError
    })
  }
})
```

---

## المهام ذات الصلة

- المطور 10: Server Monitoring Dashboard
- المطور 3: Infrastructure Monitoring
- المطور 11: Bridge Daemon (Telemetry)

---

## الحالة الحالية

**ما هو موجود:**
- ❌ لا شيء بعد - يجب بناء كل شيء من الصفر

**ما يجب إضافته:**
- [ ] Telemetry collection system
- [ ] WebSocket للبيانات الحية
- [ ] Dashboard components (Charts)
- [ ] Alert engine
- [ ] Notification system
- [ ] Threshold configuration
- [ ] Historical data storage
- [ ] Logs viewer
- [ ] Performance reports

---

## التوسعة المطلوبة

### مثال: Server Metrics Component

```typescript
// components/features/Monitoring/ServerMetrics.tsx

import { useTelemetry } from '@/hooks/useTelemetry'
import CPUChart from './CPUChart'
import MemoryChart from './MemoryChart'
import DiskChart from './DiskChart'

interface ServerMetricsProps {
  serverId: string
}

export default function ServerMetrics({ serverId }: ServerMetricsProps) {
  const { metrics, isConnected } = useTelemetry(serverId)

  if (!isConnected) {
    return <div>Connecting to server...</div>
  }

  return (
    <div className="grid grid-cols-2 gap-4">
      {/* CPU */}
      <div className="bg-gray-800 p-4 rounded">
        <h3 className="text-white mb-2">CPU Usage</h3>
        <CPUChart data={metrics.cpu} />
        <div className="text-2xl text-white mt-2">
          {metrics.cpu.current}%
        </div>
      </div>

      {/* Memory */}
      <div className="bg-gray-800 p-4 rounded">
        <h3 className="text-white mb-2">Memory Usage</h3>
        <MemoryChart data={metrics.memory} />
        <div className="text-2xl text-white mt-2">
          {metrics.memory.used} / {metrics.memory.total} GB
        </div>
      </div>

      {/* Disk */}
      <div className="bg-gray-800 p-4 rounded">
        <h3 className="text-white mb-2">Disk Usage</h3>
        <DiskChart data={metrics.disk} />
        <div className="text-2xl text-white mt-2">
          {metrics.disk.percentage}%
        </div>
      </div>

      {/* Network */}
      <div className="bg-gray-800 p-4 rounded">
        <h3 className="text-white mb-2">Network</h3>
        <div className="space-y-2">
          <div className="flex justify-between text-white">
            <span>Download:</span>
            <span>{metrics.network.download} MB/s</span>
          </div>
          <div className="flex justify-between text-white">
            <span>Upload:</span>
            <span>{metrics.network.upload} MB/s</span>
          </div>
        </div>
      </div>
    </div>
  )
}
```

### مثال: Alert Engine

```typescript
// lib/monitoring/alertEngine.ts

interface AlertRule {
  metric: string
  threshold: number
  comparison: 'gt' | 'lt' | 'eq'
  severity: 'info' | 'warning' | 'critical'
  message: string
}

const ALERT_RULES: AlertRule[] = [
  {
    metric: 'cpu',
    threshold: 90,
    comparison: 'gt',
    severity: 'critical',
    message: 'CPU usage exceeded 90%'
  },
  {
    metric: 'memory.percentage',
    threshold: 85,
    comparison: 'gt',
    severity: 'warning',
    message: 'Memory usage exceeded 85%'
  },
  {
    metric: 'disk.percentage',
    threshold: 80,
    comparison: 'gt',
    severity: 'warning',
    message: 'Disk usage exceeded 80%'
  }
]

export class AlertEngine {
  private sentAlerts = new Map<string, number>()

  checkMetrics(metrics: ServerMetrics): Alert[] {
    const alerts: Alert[] = []

    for (const rule of ALERT_RULES) {
      const value = this.getMetricValue(metrics, rule.metric)
      
      if (this.shouldAlert(value, rule)) {
        const alertKey = `${metrics.serverId}:${rule.metric}`
        
        // Avoid duplicate alerts (cooldown: 5 minutes)
        if (this.canSendAlert(alertKey)) {
          alerts.push({
            serverId: metrics.serverId,
            severity: rule.severity,
            message: rule.message,
            value,
            timestamp: Date.now()
          })
          
          this.sentAlerts.set(alertKey, Date.now())
        }
      }
    }

    return alerts
  }

  private getMetricValue(metrics: any, path: string): number {
    return path.split('.').reduce((obj, key) => obj?.[key], metrics)
  }

  private shouldAlert(value: number, rule: AlertRule): boolean {
    switch (rule.comparison) {
      case 'gt': return value > rule.threshold
      case 'lt': return value < rule.threshold
      case 'eq': return value === rule.threshold
      default: return false
    }
  }

  private canSendAlert(key: string): boolean {
    const lastSent = this.sentAlerts.get(key)
    if (!lastSent) return true
    
    const cooldown = 5 * 60 * 1000 // 5 minutes
    return Date.now() - lastSent > cooldown
  }
}
```

### مثال: Telemetry Hook

```typescript
// hooks/useTelemetry.ts

import { useState, useEffect } from 'react'
import { io } from 'socket.io-client'

export function useTelemetry(serverId: string) {
  const [metrics, setMetrics] = useState<ServerMetrics | null>(null)
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    const socket = io('/monitoring')

    socket.on('connect', () => {
      setIsConnected(true)
      // Subscribe to server metrics
      socket.emit('subscribe', { serverId })
    })

    socket.on('disconnect', () => {
      setIsConnected(false)
    })

    socket.on('metrics:update', (data: ServerMetrics) => {
      if (data.serverId === serverId) {
        setMetrics(data)
      }
    })

    return () => {
      socket.disconnect()
    }
  }, [serverId])

  return { metrics, isConnected }
}
```

---

## التحديات التقنية

### 1. Real-time Updates Performance
```typescript
// حل: Throttling للتحديثات
import { throttle } from 'lodash'

const updateCharts = throttle((data) => {
  setChartData(data)
}, 1000) // Update at most once per second
```

### 2. Historical Data Storage
```typescript
// حل: Time-series database أو aggregation
const storeMetrics = (metrics: ServerMetrics) => {
  // Store only aggregated data after 1 hour
  if (metrics.timestamp < Date.now() - 3600000) {
    return storeAggregated(metrics)
  }
  return storeRaw(metrics)
}
```

### 3. Alert Fatigue
```typescript
// حل: Alert grouping & cooldown
const groupAlerts = (alerts: Alert[]) => {
  return alerts.reduce((groups, alert) => {
    const key = alert.serverId
    groups[key] = groups[key] || []
    groups[key].push(alert)
    return groups
  }, {})
}
```

---

## الوثائق ذات الصلة

- [`../01_ARCHITECTURE/SYSTEM_OVERVIEW.md`](../../01_ARCHITECTURE/SYSTEM_OVERVIEW.md)
- [`../03_SYSTEMS/11_Bridge_Coordination/README.md`](../11_Bridge_Coordination/README.md)
- [`../05_OPERATIONS/AGENT_TASKS/DEVELOPER_10.md`](../../05_OPERATIONS/AGENT_TASKS/DEVELOPER_10.md)

---

**آخر تحديث**: 2025-11-18  
**الحالة**: ✅ موثق
