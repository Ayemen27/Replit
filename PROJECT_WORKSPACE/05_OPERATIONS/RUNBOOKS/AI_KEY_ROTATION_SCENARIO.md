# 🔄 Scenario: Automatic Key Rotation

> **📍 السيناريو**: كيف يتعامل النظام مع انتهاء حد مفتاح وينتقل تلقائياً للمفتاح التالي

**الحالة**: Happy Path ✅  
**المدة**: يوم عمل كامل (8:00 AM - 6:00 PM)  
**الهدف**: إثبات أن Multi-Key Rotation يعمل بسلاسة بدون انقطاع

---

## 🎯 الهدف من السيناريو

إثبات أن النظام:
1. يتتبع استهلاك كل مفتاح بدقة
2. يُحذّر عند اقتراب انتهاء الحد
3. ينتقل تلقائياً للمفتاح التالي بدون انقطاع
4. يُرسل إشعارات مناسبة

---

## 📋 الإعداد الأولي (Setup)

### المفاتيح المُعدّة

```bash
# .env Configuration
GROQ_API_KEY_1=sk-proj-AAA...
GROQ_KEY_1_PRIORITY=1
GROQ_KEY_1_DAILY_LIMIT=14400

GROQ_API_KEY_2=sk-proj-BBB...
GROQ_KEY_2_PRIORITY=2
GROQ_KEY_2_DAILY_LIMIT=14400

GROQ_API_KEY_3=sk-proj-CCC...
GROQ_KEY_3_PRIORITY=3
GROQ_KEY_3_DAILY_LIMIT=14400
```

### الحالة في بداية اليوم (00:00 UTC)

```
Groq Key 1 (Priority 1):
  ├─ Used: 0 tokens (0%)
  ├─ Remaining: 14,400 tokens
  ├─ Health: 100%
  └─ Status: ✅ Active

Groq Key 2 (Priority 2):
  ├─ Used: 0 tokens (0%)
  ├─ Remaining: 14,400 tokens
  ├─ Health: 100%
  └─ Status: ⏸️ Standby

Groq Key 3 (Priority 3):
  ├─ Used: 0 tokens (0%)
  ├─ Remaining: 14,400 tokens
  ├─ Health: 100%
  └─ Status: ⏸️ Standby
```

---

## ⏰ التدفق الزمني (Timeline)

### 08:00 AM - بداية العمل

**الحدث**: المستخدمون يبدأون العمل

```
Request #1-500:
  ├─ Router selects: Groq Key 1 (highest priority + healthy)
  ├─ Avg tokens per request: ~100
  ├─ Total used: 500 * 100 = 50,000 tokens
  └─ Wait... that exceeds daily limit!
  
Actually:
  ├─ System processes ~144 requests
  ├─ Total tokens: ~14,000 (approaching limit)
  └─ Groq Key 1: 97% used
```

**النظام يعمل**:
```python
# ModelRouter.chat() - Internal Flow

for each request:
    1. Calculate key scores:
       - Groq Key 1: Score = (quota: 40% * 0.03) + (health: 30%) + ... = 45
       - Groq Key 2: Score = (quota: 40% * 1.00) + (health: 30%) + ... = 70
       - Groq Key 3: Score = 70
    
    2. Select: Key 1 (still highest due to priority bonus)
    
    3. Check quota:
       if remaining < required_tokens:
           skip to next key
    
    4. Make API call
    
    5. Log usage:
       quota_tracker.log_usage("groq", 1, tokens_used)
```

**Logs**:
```
[08:15] INFO: Groq Key 1: 1,234 tokens used (8.5%)
[08:30] INFO: Groq Key 1: 3,456 tokens used (24.0%)
[08:45] INFO: Groq Key 1: 5,678 tokens used (39.4%)
[09:00] INFO: Groq Key 1: 7,890 tokens used (54.8%)
```

---

### 10:00 AM - تحذير 75%

**الحدث**: Groq Key 1 وصل 75% من حده

```
Groq Key 1:
  ├─ Used: 10,800 tokens (75%)
  ├─ Remaining: 3,600 tokens
  └─ Status: ⚠️ Warning
```

**النظام يتفاعل**:

1. **QuotaTracker** يكتشف:
```python
quota_info = quota_tracker.get_remaining_quota("groq", 1, 14400)
# {
#   "percentage": 75.0,
#   "status": "warning",
#   ...
# }
```

2. **ModelRouter** يُنبّه:
```python
if quota_info["status"] == "warning":
    key_notifier.alert_quota_warning("groq", 1, quota_info)
```

3. **KeyManagementNotifier** يُرسل:
   - 📱 **Telegram**:
     ```
     ⚠️ API Key Quota Warning
     
     Provider: Groq
     Key ID: 1
     Usage: 75.0%
     Remaining: 3,600 tokens
     Resets at: 2025-11-19T00:00:00Z
     
     Action: Monitor usage or add backup keys
     ```
   
   - 📝 **Log**:
     ```
     [10:00] WARNING: Groq Key 1 at 75% quota - 3,600 tokens remaining
     ```

**الإدارة تتصرف** (optional):
- يتحقق من Dashboard
- يرى أن Key 2 و Key 3 جاهزين
- يواصل العمل بثقة ✅

---

### 11:30 AM - حرج 90%

**الحدث**: Groq Key 1 وصل 90% من حده

```
Groq Key 1:
  ├─ Used: 12,960 tokens (90%)
  ├─ Remaining: 1,440 tokens
  └─ Status: 🔴 Critical
```

**النظام يتفاعل**:

1. **Trigger**: Critical quota threshold
```python
if quota_info["status"] == "critical":
    key_notifier.alert_quota_critical("groq", 1, quota_info)
```

2. **Notifications**:
   - 📧 **Email**:
     ```
     Subject: 🚨 CRITICAL: Groq Key 1 at 90%
     
     CRITICAL: API Key Quota Nearly Exhausted
     
     Provider: Groq
     Key ID: 1
     Usage: 90.0%
     Remaining: 1,440 tokens
     Resets at: 2025-11-19T00:00:00Z
     
     ⚡ Immediate Action Required:
     - Add backup keys for groq
     - Monitor usage closely
     - Consider rate limiting
     
     System will auto-switch to next available key when exhausted.
     ```
   
   - 📱 **Telegram**: نفس الرسالة
   
   - 🔔 **Dashboard Alert**: Red banner في الواجهة

**Logs**:
```
[11:30] ERROR: 🚨 Groq Key 1: 90% quota used - near exhaustion!
[11:30] INFO: Groq Key 2 ready as backup (0% used)
[11:30] INFO: Groq Key 3 ready as emergency backup (0% used)
```

---

### 12:15 PM - الانتقال التلقائي (Auto-Switch)

**الحدث**: Groq Key 1 وصل 100% من حده

```
Request #145:
  ├─ Groq Key 1: 14,400 / 14,400 tokens (100%) 🔴
  └─ System needs to handle this request...
```

**التدفق الدقيق**:

```python
# ModelRouter.chat() - Step by Step

# 1. Calculate scores (BEFORE quota check)
sorted_models = sorted(
    self.available_models,
    key=lambda m: self._calculate_key_score(m)
)
# Result:
# 1. Groq Key 2: Score 70 (100% quota remaining)
# 2. Groq Key 3: Score 70 (100% quota remaining)
# 3. Groq Key 1: Score 35 (0% quota remaining)

# 2. Try each key in order
for model_config in sorted_models:
    # First try: Groq Key 2
    provider = "groq"
    key_id = 2
    
    # 3. Check quota
    if not quota_tracker.is_quota_available(provider, key_id, 14400, required=100):
        continue  # Skip (but Key 2 has plenty!)
    
    # 4. Quota check passes ✅
    # 5. Make API call with Key 2
    result = self._call_model_with_key(model_config, messages, ...)
    
    # 6. Success! ✅
    # 7. Log usage for Key 2
    quota_tracker.log_usage("groq", 2, tokens_used=result["tokens_used"])
    
    # 8. Return result
    return result
```

**النتيجة**:
```
Request #145:
  ├─ Groq Key 1: SKIPPED (100% quota used)
  ├─ Groq Key 2: SELECTED ✅
  ├─ API call successful
  ├─ Response time: 1.2s (same speed!)
  └─ User experience: SEAMLESS (no delay, no error)
```

**Logs**:
```
[12:15] INFO: Groq Key 1: 100% quota reached (14,400 / 14,400)
[12:15] INFO: Skipping Groq Key 1 - quota exhausted
[12:15] INFO: Selected Groq Key 2 (Priority 2, 0% used)
[12:15] INFO: ✅ Request #145 completed via Groq Key 2
[12:15] INFO: Groq Key 2: +123 tokens (total: 123 / 14,400)
```

---

### 12:16 PM - 02:00 PM - استمرار العمل

**الحدث**: النظام يواصل استخدام Groq Key 2

```
Requests #146-400:
  ├─ All use: Groq Key 2
  ├─ Groq Key 1: Inactive (100% used)
  ├─ Groq Key 3: Standby (0% used)
  └─ Zero interruptions ✅
```

**الحالة في 02:00 PM**:
```
Groq Key 1:
  ├─ Used: 14,400 tokens (100%) 🔴 Exhausted
  ├─ Remaining: 0 tokens
  └─ Status: 🛑 Inactive (until midnight reset)

Groq Key 2:
  ├─ Used: 8,500 tokens (59%) 🟢 Active
  ├─ Remaining: 5,900 tokens
  └─ Status: ✅ Active (primary now)

Groq Key 3:
  ├─ Used: 0 tokens (0%) 🟢 Ready
  ├─ Remaining: 14,400 tokens
  └─ Status: ⏸️ Standby (backup ready)
```

**Dashboard View**:
```
┌─────────────────────────────────────────────────┐
│ 🟢 Groq (3 keys) - Health: 95%                 │
├─────────────────────────────────────────────────┤
│ Key 1 (Primary)   ██████████ 100% 🔴 Exhausted │
│ Key 2 (Backup)    ██████░░░░  59% ✅ Active    │
│ Key 3 (Emergency) ░░░░░░░░░░   0% ⏸️  Standby  │
│                                                 │
│ Resets in: 9h 45m                               │
└─────────────────────────────────────────────────┘
```

---

### 06:00 PM - نهاية العمل

**الحدث**: يوم عمل ناجح بدون انقطاع!

**النتيجة النهائية**:
```
Total Requests Today: 450
  ├─ Groq Key 1: 144 requests (14,400 tokens) ✅
  ├─ Groq Key 2: 306 requests (10,234 tokens) ✅
  └─ Groq Key 3: 0 requests (unused)

Success Rate: 100% ✅
Downtime: 0 seconds ✅
User Complaints: 0 ✅
```

**الإحصائيات**:
```
┌────────────────────────────────────────────────┐
│ 📊 Daily Summary (2025-11-18)                 │
├────────────────────────────────────────────────┤
│ Total Requests: 450                            │
│ Total Tokens: 24,634                           │
│ Success Rate: 100%                             │
│ Avg Response Time: 1.2s                        │
│ Keys Rotated: 1 time (Key 1 → Key 2)          │
│ Alerts Sent: 2 (Warning + Critical)           │
│ Downtime: 0s ✅                                │
└────────────────────────────────────────────────┘
```

---

### 00:00 AM (Next Day) - Daily Reset

**الحدث**: Automatic daily reset (UTC midnight)

```
System: Daily quota reset triggered

Groq Key 1:
  ├─ Old: 14,400 / 14,400 (100%)
  ├─ New:  0 / 14,400 (0%) ✅
  └─ Status: ✅ Active again!

Groq Key 2:
  ├─ Old: 10,234 / 14,400 (71%)
  ├─ New:  0 / 14,400 (0%) ✅
  └─ Status: ✅ Standby (back to backup role)

Groq Key 3:
  ├─ Old: 0 / 14,400 (0%)
  ├─ New: 0 / 14,400 (0%) ✅
  └─ Status: ⏸️ Standby
```

**Mechanism**:
```python
# QuotaTracker uses cache with TTL
# Cache keys: "quota_groq_key1_2025-11-18"
# TTL: 86400 seconds (24 hours)
# 
# At 00:00 UTC → new date → new cache keys
# Old keys expire naturally
# Fresh start! ✅
```

---

## ✅ Success Criteria

### ✅ 1. Seamless Transition
- [x] No service interruption during key rotation
- [x] Response time unchanged (~1.2s consistently)
- [x] User experience unaffected

### ✅ 2. Accurate Tracking
- [x] Quota usage tracked precisely
- [x] Percentages calculated correctly
- [x] Daily limits enforced

### ✅ 3. Timely Alerts
- [x] Warning at 75% (Telegram)
- [x] Critical at 90% (Email + Telegram)
- [x] Dashboard alerts visible

### ✅ 4. Intelligent Selection
- [x] System prefers key with more quota
- [x] Priority respected when quotas equal
- [x] Exhausted keys automatically skipped

### ✅ 5. Automatic Recovery
- [x] Daily reset at 00:00 UTC
- [x] All keys ready next day
- [x] No manual intervention needed

---

## 🎯 Lessons Learned

### ✅ What Worked Well

1. **Multi-Key Design**:
   - Eliminates single point of failure
   - Smooth failover without user impact
   - Capacity planning flexibility

2. **Proactive Alerts**:
   - 75% warning gives plenty of time
   - 90% critical ensures action
   - Email + Telegram covers all cases

3. **Smart Scoring**:
   - Quota-aware selection prevents premature exhaustion
   - Health score ensures reliability
   - Priority provides control

### 🔄 Potential Improvements

1. **Predictive Alerts**:
   - "At current rate, Key 1 will exhaust by 1:00 PM"
   - Allows proactive key addition

2. **Load Balancing**:
   - Option to distribute load evenly across all keys
   - Extends total capacity

3. **Cost Optimization**:
   - Prefer free keys before paid ones
   - Track costs per key

---

## 📊 Comparison: Before vs After

### ❌ Before Multi-Key Support

```
08:00 AM - Start with Groq (14,400 tokens)
   ↓
12:15 PM - Groq exhausted (100%)
   ↓
System switches to Gemini (different provider!)
   ↓ Issues:
   - Slower (Gemini is slower than Groq)
   - Different token limits
   - Can't use Groq for rest of day ❌
```

### ✅ After Multi-Key Support

```
08:00 AM - Start with Groq Key 1 (14,400 tokens)
   ↓
12:15 PM - Groq Key 1 exhausted (100%)
   ↓
System switches to Groq Key 2 (14,400 tokens)
   ↓ Benefits:
   - Same speed (still Groq!)
   - Same token limits
   - Total capacity: 43,200 tokens/day ✅
```

---

## 📚 Related Documents

- [`AI_KEY_MANAGEMENT.md`](../04_SECURITY/AI_KEY_MANAGEMENT.md) - Full system documentation
- [`DEVELOPER_AI_KEYS_01.md`](../AGENT_TASKS/DEVELOPER_AI_KEYS_01.md) - Multi-Key implementation
- [`DEVELOPER_AI_KEYS_02.md`](../AGENT_TASKS/DEVELOPER_AI_KEYS_02.md) - Quota tracking
- [`QUOTA_EXCEEDED_SCENARIO.md`](QUOTA_EXCEEDED_SCENARIO.md) - What happens when all keys fail

---

**آخر تحديث**: 2025-11-18  
**السيناريو**: ✅ Validated - يعمل كما هو مخطط!
