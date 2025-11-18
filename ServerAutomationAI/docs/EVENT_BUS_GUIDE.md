# 📡 دليل Event Bus (نظام ناقل الأحداث)

## نظرة عامة

**نظام AgentCommunication** هو ناقل أحداث (Event Bus) قائم على الطوابير يسهّل الاتصال بين الوكلاء في لوحة تحكم الذكاء الاصطناعي. يستخدم نمط **Singleton** لضمان وجود نسخة واحدة فقط من النظام في جميع أنحاء التطبيق.

**الميزات الرئيسية:**
- ✅ إرسال رسائل نقطة لنقطة (Point-to-Point)
- ✅ بث الرسائل لجميع الوكلاء (Broadcast)
- ✅ نظام الأولويات (Priority Queuing)
- ✅ سجل الرسائل (Message History)
- ✅ فحوصات الصحة (Health Checks)
- ✅ إحصائيات شاملة (Detailed Statistics)
- ✅ آمن للخيوط (Thread-Safe)

---

## 📚 الاستخدام الأساسي

### 1. التهيئة والتسجيل

```python
from tools.agent_communication import AgentCommunication, get_communication_system

# الحصول على مثيل النظام (Singleton)
comm = get_communication_system()

# تسجيل الوكلاء
comm.register_agent('ai_manager')
comm.register_agent('performance_monitor')
comm.register_agent('log_analyzer')
```

### 2. إرسال الرسائل

```python
# إرسال رسالة بسيطة
success = comm.send_message(
    sender='performance_monitor',
    recipient='ai_manager',
    message_type='alert',
    content={'cpu_usage': 95, 'severity': 'high'},
    priority=2  # 1 = أعلى أولوية، 5 = أقل أولوية
)

if success:
    print("✓ تم إرسال الرسالة بنجاح")
```

### 3. استقبال الرسائل

```python
# استقبال رسالة من الطابور
message = comm.receive_message('ai_manager', timeout=5)

if message:
    print(f"من: {message.sender}")
    print(f"النوع: {message.message_type}")
    print(f"المحتوى: {message.content}")
    print(f"الأولوية: {message.priority}")
    print(f"التوقيت: {message.timestamp}")
```

### 4. بث الرسائل

```python
# إرسال رسالة لجميع الوكلاء النشطين
count = comm.broadcast_message(
    sender='ai_manager',
    message_type='system_update',
    content={'version': '2.0', 'restart_required': True},
    priority=3
)

print(f"✓ تم البث إلى {count} وكيل")
```

---

## 🏥 فحوصات الصحة

### فحص صحة النظام

```python
# فحص صحة شامل
health = comm.health_check()

print(f"الحالة: {health['status']}")  # healthy, degraded, or unhealthy
print(f"النقاط: {health['score']}/100")
print(f"الوكلاء النشطون: {health['active_agents']}/{health['total_agents']}")

if health['warnings']:
    print("\n⚠️  التحذيرات:")
    for warning in health['warnings']:
        print(f"  - {warning}")
```

### فحص استجابة وكيل محدد

```python
# التحقق من أن الوكيل مستجيب
if comm.is_agent_responsive('performance_monitor'):
    print("✓ الوكيل مستجيب")
else:
    print("✗ الوكيل غير مستجيب أو محمّل بشكل زائد")
```

### الحصول على حالة النظام

```python
status = comm.get_system_status()

print(f"الوكلاء المسجلون: {status['registered_agents']}")
print(f"الوكلاء النشطون: {status['active_agents']}")
print(f"الوكلاء غير النشطين: {status['inactive_agents']}")
print(f"أحجام الطوابير: {status['queue_sizes']}")
print(f"إجمالي الرسائل المعالجة: {status['total_messages_processed']}")

# معلومات الصحة
health_info = status['system_health']
print(f"\nصحة النظام:")
print(f"  النقاط: {health_info['score']}/100")
print(f"  الحالة: {health_info['status']}")
print(f"  نسبة النشاط: {health_info['active_agents_ratio']}")
```

---

## 📊 الإحصائيات المتقدمة

```python
stats = comm.get_statistics()

print(f"إجمالي الرسائل: {stats['total_messages']}")
print(f"أنواع الرسائل: {stats['message_types']}")
print(f"توزيع الأولويات: {stats['priority_distribution']}")
print(f"متوسط حجم الطوابير: {stats['average_queue_size']}")
print(f"أقصى حجم طابور: {stats['max_queue_size']}")

print(f"\nإحصائيات الوكلاء:")
print(f"  الإجمالي: {stats['agents']['total']}")
print(f"  النشطون: {stats['agents']['active']}")
print(f"  غير النشطين: {stats['agents']['inactive']}")
```

---

## 🔧 إدارة الطوابير

### التحقق من حجم الطابور

```python
queue_size = comm.get_queue_size('ai_manager')
print(f"حجم طابور AI Manager: {queue_size}")

# تحذير إذا كان الطابور ممتلئاً
if queue_size > 800:
    print("⚠️  الطابور ممتلئ تقريباً! (>80%)")
```

### مسح الطابور

```python
# مسح جميع الرسائل في طابور وكيل معين
comm.clear_queue('performance_monitor')
print("✓ تم مسح الطابور")
```

### إلغاء تسجيل الوكيل

```python
# إلغاء تسجيل وكيل (يحتفظ بالطابور لكن يضع علامة "غير نشط")
comm.unregister_agent('log_analyzer')
```

---

## 📜 سجل الرسائل

### عرض السجل الكامل

```python
# الحصول على آخر 100 رسالة
history = comm.get_message_history(limit=100)

for msg in history:
    print(f"{msg['timestamp']}: {msg['sender']} -> {msg['recipient']}")
    print(f"  النوع: {msg['message_type']}")
    print(f"  الحالة: {msg['status']}")
```

### تصفية حسب الوكيل

```python
# الحصول على رسائل وكيل محدد فقط
agent_history = comm.get_message_history(
    agent_name='ai_manager',
    limit=50
)

print(f"رسائل AI Manager: {len(agent_history)}")
```

---

## 💡 أمثلة عملية

### مثال 1: نظام تنبيهات المراقبة

```python
from tools.agent_communication import get_communication_system

class PerformanceMonitor:
    def __init__(self):
        self.comm = get_communication_system()
        self.comm.register_agent('performance_monitor')
    
    def check_cpu(self):
        cpu_usage = self._get_cpu_usage()
        
        if cpu_usage > 90:
            # إرسال تنبيه حرج عالي الأولوية
            self.comm.send_message(
                sender='performance_monitor',
                recipient='ai_manager',
                message_type='critical_alert',
                content={
                    'metric': 'cpu',
                    'value': cpu_usage,
                    'threshold': 90,
                    'action_required': 'immediate'
                },
                priority=1  # أعلى أولوية
            )
    
    def _get_cpu_usage(self):
        # محاكاة قراءة CPU
        import psutil
        return psutil.cpu_percent(interval=1)
```

### مثال 2: مدير الذكاء الاصطناعي (معالج الرسائل)

```python
class AIManager:
    def __init__(self):
        self.comm = get_communication_system()
        self.comm.register_agent('ai_manager')
        self.running = True
    
    def process_messages(self):
        while self.running:
            # استقبال الرسائل مع timeout
            message = self.comm.receive_message('ai_manager', timeout=1)
            
            if message:
                self._handle_message(message)
    
    def _handle_message(self, message):
        if message.message_type == 'critical_alert':
            self._handle_critical_alert(message.content)
        elif message.message_type == 'info':
            self._log_info(message.content)
        else:
            print(f"رسالة غير معروفة: {message.message_type}")
    
    def _handle_critical_alert(self, content):
        print(f"🚨 تنبيه حرج: {content}")
        # اتخاذ إجراء فوري...
```

### مثال 3: مراقبة صحة النظام

```python
import time

class HealthMonitor:
    def __init__(self):
        self.comm = get_communication_system()
    
    def monitor_health(self):
        while True:
            health = self.comm.health_check()
            
            if health['status'] == 'unhealthy':
                print("🔴 النظام غير صحي!")
                self._send_alert(health)
            elif health['status'] == 'degraded':
                print("🟡 النظام متدهور")
                for warning in health['warnings']:
                    print(f"  ⚠️  {warning}")
            else:
                print("🟢 النظام صحي")
            
            # إحصائيات
            stats = self.comm.get_statistics()
            print(f"📊 الرسائل المعالجة: {stats['total_messages']}")
            print(f"📈 متوسط حجم الطوابير: {stats['average_queue_size']}")
            
            time.sleep(60)  # فحص كل دقيقة
    
    def _send_alert(self, health):
        # إرسال تنبيه عبر نظام الإشعارات
        pass
```

---

## ⚙️ التكوين المتقدم

### حد أقصى للطابور

```python
# الحد الأقصى الافتراضي هو 1000 رسالة لكل وكيل
# يتم تعيينه عند التسجيل ولا يمكن تغييره ديناميكياً
```

### سجل الرسائل

```python
# الحد الأقصى للسجل هو 1000 رسالة
# يتم تدوير السجل تلقائياً عند الوصول للحد
```

---

## 🚨 معالجة الأخطاء

### أخطاء إرسال الرسائل

```python
# التعامل مع فشل الإرسال
success = comm.send_message('agent_a', 'agent_b', 'test', {})

if not success:
    print("فشل الإرسال - تحقق من:")
    print("  1. هل الوكيل المستقبل مسجل؟")
    print("  2. هل الطابور ممتلئ؟")
    print("  3. هل هناك استثناء في النظام؟")
```

### أخطاء استقبال الرسائل

```python
# استقبال مع timeout
message = comm.receive_message('agent_a', timeout=5)

if message is None:
    print("لا توجد رسائل متاحة")
    # قد يكون الطابور فارغاً أو timeout انتهى
```

### التحقق من التسجيل

```python
# قبل إرسال الرسائل، تأكد من تسجيل الوكيل
if 'my_agent' not in comm.agents:
    comm.register_agent('my_agent')
```

---

## 📊 نمذجة نظام الأولويات

| الأولوية | الاستخدام | مثال |
|----------|-----------|------|
| **1** | حرج للغاية | فشل النظام، فقدان البيانات |
| **2** | عالية | تنبيهات أمنية، موارد ممتلئة |
| **3** | متوسطة | تحذيرات، تحديثات النظام |
| **4** | منخفضة | معلومات عامة، حالات |
| **5** | روتينية | سجلات، إحصائيات دورية |

**ملاحظة:** الأولوية 1 = أعلى، الأولوية 5 = أقل. الرسائل ذات الأولوية الأعلى تُعالج أولاً.

---

## 🔒 الأمان وأفضل الممارسات

### 1. تجنب حشو الطوابير

```python
# تحقق من حجم الطابور قبل إرسال رسائل كثيرة
queue_size = comm.get_queue_size('target_agent')

if queue_size < 900:  # أقل من 90%
    comm.send_message(...)
else:
    print("⚠️  الطابور ممتلئ تقريباً - انتظر...")
    time.sleep(1)
```

### 2. استخدم الأولويات بحكمة

```python
# لا تضع جميع الرسائل على أولوية 1
# استخدم الأولوية 1 فقط للتنبيهات الحرجة حقاً

# سيء ❌
comm.send_message(..., priority=1)  # لمعلومة عادية

# جيد ✅
comm.send_message(..., priority=4)  # للمعلومات
comm.send_message(..., priority=1)  # فقط للحوادث الحرجة
```

### 3. قم بإلغاء تسجيل الوكلاء عند الإنهاء

```python
# في نهاية دورة حياة الوكيل
comm.unregister_agent('my_agent')
```

### 4. مراقبة صحة النظام بانتظام

```python
# تشغيل فحص صحة دوري
import threading

def health_check_loop():
    while True:
        health = comm.health_check()
        if not health['healthy']:
            # اتخاذ إجراء...
            pass
        time.sleep(300)  # كل 5 دقائق

health_thread = threading.Thread(target=health_check_loop, daemon=True)
health_thread.start()
```

---

## 🐛 استكشاف الأخطاء

### المشكلة: الرسائل لا تصل

**الحلول:**
```python
# 1. تحقق من تسجيل الوكيل
status = comm.get_system_status()
print("الوكلاء المسجلون:", status['registered_agents'])

# 2. تحقق من نشاط الوكيل
print("الوكلاء النشطون:", status['active_agents'])

# 3. فحص حجم الطابور
queue_size = comm.get_queue_size('recipient_agent')
print(f"حجم الطابور: {queue_size}/1000")
```

### المشكلة: الطوابير ممتلئة

**الحلول:**
```python
# 1. مسح الطابور
comm.clear_queue('overloaded_agent')

# 2. زيادة سرعة معالجة الرسائل
# تأكد من أن receive_message تُستدعى بشكل متكرر

# 3. فحص الوكلاء البطيئة
stats = comm.get_statistics()
if stats['max_queue_size'] > 800:
    print("⚠️  بعض الوكلاء بطيئة في المعالجة")
```

### المشكلة: استهلاك ذاكرة عالي

**الحلول:**
```python
# سجل الرسائل محدود بـ 1000 رسالة
# لكن يمكنك تقليل الحد إذا لزم الأمر

# تعديل في الكود المصدري:
# comm.max_history = 500  # تقليل الحد
```

---

## 📈 قياس الأداء

```python
import time

# قياس وقت الإرسال
start = time.time()
comm.send_message('a', 'b', 'test', {})
send_time = time.time() - start
print(f"وقت الإرسال: {send_time*1000:.2f}ms")

# قياس وقت الاستقبال
start = time.time()
msg = comm.receive_message('b', timeout=0.1)
receive_time = time.time() - start
print(f"وقت الاستقبال: {receive_time*1000:.2f}ms")

# قياس الإنتاجية (Throughput)
start = time.time()
for i in range(1000):
    comm.send_message('a', 'b', 'test', {'seq': i})
duration = time.time() - start
throughput = 1000 / duration
print(f"الإنتاجية: {throughput:.0f} رسالة/ثانية")
```

---

## 🔗 التكامل مع الأنظمة الأخرى

### التكامل مع نظام الإشعارات

```python
from tools.notification_system import NotificationSystem

comm = get_communication_system()
notifier = NotificationSystem()

# إرسال إشعارات تلقائياً عند تلقي تنبيهات حرجة
def handle_critical_alerts():
    message = comm.receive_message('ai_manager', timeout=1)
    
    if message and message.message_type == 'critical_alert':
        notifier.send_critical_alert(
            message=f"تنبيه من {message.sender}",
            details=str(message.content)
        )
```

### التكامل مع نظام السجلات

```python
from tools.logger import get_logger

logger = get_logger('event_bus_monitor')

# تسجيل جميع الرسائل
def log_all_messages():
    history = comm.get_message_history(limit=100)
    
    for msg in history:
        logger.info(f"رسالة: {msg['sender']} -> {msg['recipient']} ({msg['message_type']})")
```

---

## 📚 مراجع إضافية

- **أنواع الرسائل الشائعة:**
  - `alert` - تنبيهات عامة
  - `critical_alert` - تنبيهات حرجة
  - `status_update` - تحديثات الحالة
  - `info` - معلومات عامة
  - `command` - أوامر للوكلاء
  - `response` - ردود على الأوامر

- **سجلات النظام:**
  - `logs/agent_communication.log` - جميع أنشطة Event Bus

---

## ✅ قائمة التحقق للإنتاج

- [ ] جميع الوكلاء مسجلة بشكل صحيح
- [ ] فحوصات الصحة تعمل بشكل دوري
- [ ] معالجة الرسائل سريعة (لا طوابير ممتلئة)
- [ ] السجلات تُراقب بانتظام
- [ ] الأولويات مستخدمة بشكل صحيح
- [ ] معالجة الأخطاء موجودة في جميع الوكلاء
- [ ] التنبيهات الحرجة تُرسل للإشعارات

---

## 🎯 الخلاصة

نظام Event Bus يوفر طريقة موثوقة وفعّالة للتواصل بين الوكلاء. باستخدام الأولويات وفحوصات الصحة والإحصائيات المتقدمة، يمكنك بناء نظام قوي ومرن.

**للمساعدة:**
- راجع `tools/agent_communication.py` للكود المصدري
- راجع `logs/agent_communication.log` للسجلات
- استخدم `health_check()` للتشخيص الفوري

---

**الإصدار:** 2.0  
**آخر تحديث:** 15 نوفمبر 2025
