# 📊 Developer AI-Keys-02: Daily Quota Tracking

> **📍 المهمة**: تطبيق نظام تتبع الحد اليومي لكل مفتاح API مع اختيار ذكي بناءً على الحد المتبقي

**الأولوية**: 🔴🔴🔴🔴🔴 (حرجة - عالية جداً)  
**المدة المتوقعة**: 2-3 أيام  
**المتطلبات السابقة**: ✅ DEVELOPER_AI_KEYS_01 مكتمل (Multi-Key Support)  
**المخرجات**: نظام دقيق لتتبع استهلاك كل مفتاح + اختيار ذكي

---

## 📋 الهدف

تتبع دقيق لاستهلاك **كل مفتاح API** بشكل يومي، مع اختيار المفتاح الأفضل بناءً على:
1. الحد المتبقي (Remaining Quota)
2. Health Score
3. Priority

### المشكلة الحالية

```python
# الوضع الحالي (❌):
- لا نعرف كم استهلكنا من كل مفتاح
- نكتشف انتهاء الحد فقط عند error من API
- Reactive (بعد المشكلة) بدلاً من Proactive (قبل المشكلة)
```

### الحل المطلوب

```python
# الوضع الجديد (✅):
Groq Key 1:
  ├─ Used today: 11,234 tokens (78%)
  ├─ Remaining: 3,166 tokens (22%)
  └─ Status: ⚠️ Warning (>75%)

Groq Key 2:
  ├─ Used today: 450 tokens (3%)
  ├─ Remaining: 13,950 tokens (97%)
  └─ Status: ✅ Healthy

→ الاختيار الذكي: Key 2 (لديه حد أكبر!)
```

---

## 🎯 المخرجات المطلوبة

### ✅ Acceptance Criteria

1. ✅ **تسجيل دقيق**:
   - كل طلب يُسجل: `provider`, `key_id`, `tokens_used`, `timestamp`
   - التخزين: cache (Redis-compatible) مع expire يومي

2. ✅ **حساب الحد المتبقي**:
   - دالة `get_remaining_quota(provider, key_id)`
   - ترجع: `{used, limit, remaining, percentage}`

3. ✅ **الاختيار الذكي**:
   - يُفضل المفتاح ذو الحد الأكبر المتبقي
   - يأخذ بالاعتبار: quota (40%), health (30%), latency (20%), priority (10%)

4. ✅ **Reset يومي**:
   - كل 24 ساعة → reset جميع counters
   - استخدام UTC timezone

5. ✅ **تحذيرات استباقية**:
   - عند 75% → Warning log
   - عند 90% → إشعار (Phase 3)

---

## 📝 المهام التفصيلية

### Task 1: إنشاء QuotaTracker Class (1 يوم)

**ملف جديد**: `ServerAutomationAI/dev_platform/core/quota_tracker.py`

```python
"""
Daily Quota Tracker for API Keys
Tracks token/request usage per key with daily reset
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from .cache_manager import get_cache_manager


logger = logging.getLogger(__name__)


class QuotaTracker:
    """
    Track daily quota usage for each API key
    
    Features:
    - Per-key usage tracking
    - Daily automatic reset (UTC 00:00)
    - Remaining quota calculation
    - Warning thresholds (75%, 90%)
    - Usage statistics
    """
    
    def __init__(self):
        self.cache = get_cache_manager()
    
    def log_usage(
        self,
        provider: str,
        key_id: int,
        tokens_used: int,
        requests_count: int = 1
    ) -> Dict[str, Any]:
        """
        Log usage for a specific key
        
        Args:
            provider: "groq", "gemini", etc.
            key_id: 1, 2, 3, ...
            tokens_used: Number of tokens consumed
            requests_count: Number of requests (default 1)
        
        Returns:
            Updated usage stats:
            {
                "tokens_used": 12345,
                "requests_count": 123,
                "last_updated": "2025-11-18T14:23:00Z"
            }
        """
        today = self._get_today_key()
        cache_key = self._make_cache_key(provider, key_id, today)
        
        # Get current usage
        current = self.cache.cache_get(cache_key) or {
            "tokens_used": 0,
            "requests_count": 0
        }
        
        # Update
        new_usage = {
            "tokens_used": current["tokens_used"] + tokens_used,
            "requests_count": current["requests_count"] + requests_count,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
        # Save with 24h expiry
        self.cache.cache_set(cache_key, new_usage, expire=86400)
        
        logger.debug(
            f"{provider} Key {key_id}: "
            f"+{tokens_used} tokens "
            f"(total: {new_usage['tokens_used']})"
        )
        
        return new_usage
    
    def get_today_usage(
        self,
        provider: str,
        key_id: int
    ) -> Dict[str, int]:
        """
        Get today's usage for a specific key
        
        Returns:
            {
                "tokens_used": 12345,
                "requests_count": 123
            }
        """
        today = self._get_today_key()
        cache_key = self._make_cache_key(provider, key_id, today)
        
        usage = self.cache.cache_get(cache_key)
        
        if not usage:
            return {"tokens_used": 0, "requests_count": 0}
        
        return {
            "tokens_used": usage["tokens_used"],
            "requests_count": usage["requests_count"]
        }
    
    def get_remaining_quota(
        self,
        provider: str,
        key_id: int,
        daily_limit: int,
        metric: str = "tokens"  # "tokens" or "requests"
    ) -> Dict[str, Any]:
        """
        Calculate remaining quota for a key
        
        Args:
            provider: Provider name
            key_id: Key ID
            daily_limit: Daily limit (tokens or requests)
            metric: "tokens" or "requests"
        
        Returns:
            {
                "used": 11234,
                "limit": 14400,
                "remaining": 3166,
                "percentage": 78.0,
                "status": "warning",  # "healthy", "warning", "critical", "exhausted"
                "resets_at": "2025-11-19T00:00:00Z"
            }
        """
        usage = self.get_today_usage(provider, key_id)
        
        if metric == "tokens":
            used = usage["tokens_used"]
        elif metric == "requests":
            used = usage["requests_count"]
        else:
            raise ValueError(f"Invalid metric: {metric}")
        
        remaining = max(0, daily_limit - used)
        percentage = (used / daily_limit * 100) if daily_limit > 0 else 0
        
        # Determine status
        if percentage >= 100:
            status = "exhausted"
        elif percentage >= 90:
            status = "critical"
        elif percentage >= 75:
            status = "warning"
        else:
            status = "healthy"
        
        # Calculate reset time (next midnight UTC)
        now = datetime.now(timezone.utc)
        tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if tomorrow <= now:
            from datetime import timedelta
            tomorrow += timedelta(days=1)
        
        return {
            "used": used,
            "limit": daily_limit,
            "remaining": remaining,
            "percentage": round(percentage, 1),
            "status": status,
            "resets_at": tomorrow.isoformat(),
            "metric": metric
        }
    
    def is_quota_available(
        self,
        provider: str,
        key_id: int,
        daily_limit: int,
        required: int = 100,
        metric: str = "tokens"
    ) -> bool:
        """
        Check if key has enough quota for a request
        
        Args:
            provider: Provider name
            key_id: Key ID
            daily_limit: Daily limit
            required: Required tokens/requests (default 100)
            metric: "tokens" or "requests"
        
        Returns:
            True if quota available, False otherwise
        """
        quota_info = self.get_remaining_quota(
            provider, key_id, daily_limit, metric
        )
        
        available = quota_info["remaining"] >= required
        
        if not available:
            logger.warning(
                f"{provider} Key {key_id}: Insufficient quota "
                f"(remaining: {quota_info['remaining']}, "
                f"required: {required})"
            )
        
        return available
    
    def get_all_quotas(
        self,
        keys_config: Dict[str, list]
    ) -> Dict[str, list]:
        """
        Get quota info for all keys
        
        Args:
            keys_config: {
                "groq": [
                    {"id": 1, "daily_limit": 14400},
                    {"id": 2, "daily_limit": 14400}
                ],
                "gemini": [...]
            }
        
        Returns:
            Same structure with quota info added
        """
        result = {}
        
        for provider, keys in keys_config.items():
            result[provider] = []
            
            for key_info in keys:
                quota = self.get_remaining_quota(
                    provider,
                    key_info["id"],
                    key_info["daily_limit"]
                )
                
                result[provider].append({
                    **key_info,
                    "quota": quota
                })
        
        return result
    
    def _get_today_key(self) -> str:
        """Get today's date key in UTC (YYYY-MM-DD)"""
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    def _make_cache_key(
        self,
        provider: str,
        key_id: int,
        date: str
    ) -> str:
        """Generate cache key for quota data"""
        return f"quota_{provider}_key{key_id}_{date}"
    
    def reset_daily_quotas(self):
        """
        Manually reset all quotas (for testing)
        In production, this happens automatically via cache expiry
        """
        logger.info("Manually resetting all daily quotas")
        # Cache entries auto-expire after 24h, no manual cleanup needed
        # This method is primarily for testing


# Global instance
_quota_tracker = None

def get_quota_tracker() -> QuotaTracker:
    """Get global quota tracker instance"""
    global _quota_tracker
    if _quota_tracker is None:
        _quota_tracker = QuotaTracker()
    return _quota_tracker
```

---

### Task 2: دمج QuotaTracker مع ModelRouter (1 يوم)

**الملف**: `ServerAutomationAI/dev_platform/core/model_router.py`

#### 2.1 إضافة QuotaTracker في `__init__()`

```python
from .quota_tracker import get_quota_tracker

class ModelRouter:
    def __init__(self):
        self.secrets = get_secrets_manager()
        self.cache = get_cache_manager()
        self.quota_tracker = get_quota_tracker()  # NEW!
        
        # ... rest of init
```

#### 2.2 تعديل `chat()` - التحقق قبل الطلب

```python
def chat(self, messages, temperature=0.7, max_tokens=None, ...):
    # ... existing code ...
    
    # Sort models by intelligent scoring
    sorted_models = sorted(
        self.available_models,
        key=lambda m: self._calculate_key_score(m)
    )
    
    # Try each model
    for model_config in sorted_models:
        provider = model_config["provider"]
        key_id = model_config["key_id"]
        daily_limit = model_config["daily_limit"]
        
        # NEW: Check quota BEFORE making the call
        if not self.quota_tracker.is_quota_available(
            provider,
            key_id,
            daily_limit,
            required=max_tokens or 100,
            metric="tokens"
        ):
            quota_info = self.quota_tracker.get_remaining_quota(
                provider, key_id, daily_limit
            )
            logger.warning(
                f"Skipping {provider} Key {key_id}: "
                f"{quota_info['status']} "
                f"({quota_info['percentage']}% used)"
            )
            continue  # Skip to next key
        
        # Try the request...
        try:
            result = self._call_model_with_key(...)
            
            # NEW: Log usage AFTER successful call
            self.quota_tracker.log_usage(
                provider,
                key_id,
                tokens_used=result["tokens_used"],
                requests_count=1
            )
            
            # Check if we should warn
            quota_info = self.quota_tracker.get_remaining_quota(
                provider, key_id, daily_limit
            )
            
            if quota_info["status"] == "warning":
                logger.warning(
                    f"⚠️ {provider} Key {key_id}: "
                    f"{quota_info['percentage']}% quota used"
                )
            elif quota_info["status"] == "critical":
                logger.error(
                    f"🚨 {provider} Key {key_id}: "
                    f"{quota_info['percentage']}% quota used - "
                    f"near exhaustion!"
                )
            
            return result
            
        except ...:
            # ... existing error handling ...
```

#### 2.3 إضافة Intelligent Scoring

```python
def _calculate_key_score(self, model_config: Dict) -> float:
    """
    Calculate score for key selection
    
    Factors (weighted):
    - Remaining quota: 40%
    - Health score: 30%
    - Latency: 20%
    - Priority: 10%
    
    Returns:
        Higher score = better key
    """
    provider = model_config["provider"]
    key_id = model_config["key_id"]
    daily_limit = model_config["daily_limit"]
    priority = model_config["priority"]
    
    # 1. Quota factor (40%)
    quota_info = self.quota_tracker.get_remaining_quota(
        provider, key_id, daily_limit
    )
    quota_factor = (quota_info["remaining"] / daily_limit) * 40
    
    # 2. Health factor (30%)
    health_key = f"{provider}_key{key_id}"
    health_score = self.health_scores.get(health_key, 100)
    health_factor = (health_score / 100) * 30
    
    # 3. Latency factor (20%) - lower is better
    # Get average latency from cache
    latency_key = f"latency_{provider}_key{key_id}"
    avg_latency = self.cache.cache_get(latency_key) or 1.0
    latency_factor = (1 / max(avg_latency, 0.1)) * 20
    
    # 4. Priority factor (10%) - lower priority number = higher score
    # Priority 1 = 10 points, Priority 2 = 5 points, Priority 3+ = 2 points
    if priority == 1:
        priority_factor = 10
    elif priority == 2:
        priority_factor = 5
    else:
        priority_factor = 2
    
    total_score = (
        quota_factor +
        health_factor +
        latency_factor +
        priority_factor
    )
    
    logger.debug(
        f"{provider} Key {key_id} score: {total_score:.1f} "
        f"(quota: {quota_factor:.1f}, "
        f"health: {health_factor:.1f}, "
        f"latency: {latency_factor:.1f}, "
        f"priority: {priority_factor:.1f})"
    )
    
    return total_score
```

---

### Task 3: Testing (0.5-1 يوم)

#### 3.1 Unit Tests

```python
# test_quota_tracker.py

def test_log_usage():
    """Test usage logging"""
    tracker = QuotaTracker()
    
    # Log usage
    result = tracker.log_usage("groq", 1, tokens_used=100)
    
    assert result["tokens_used"] == 100
    assert result["requests_count"] == 1

def test_get_remaining_quota():
    """Test quota calculation"""
    tracker = QuotaTracker()
    
    # Use 10,000 tokens
    tracker.log_usage("groq", 1, tokens_used=10000)
    
    # Check remaining (limit: 14,400)
    quota = tracker.get_remaining_quota("groq", 1, 14400)
    
    assert quota["used"] == 10000
    assert quota["limit"] == 14400
    assert quota["remaining"] == 4400
    assert quota["percentage"] == pytest.approx(69.4, rel=0.1)
    assert quota["status"] == "healthy"

def test_quota_warning_thresholds():
    """Test warning status at 75% and 90%"""
    tracker = QuotaTracker()
    
    # 75% usage
    tracker.log_usage("groq", 1, tokens_used=10800)  # 75% of 14400
    quota = tracker.get_remaining_quota("groq", 1, 14400)
    assert quota["status"] == "warning"
    
    # 90% usage
    tracker.log_usage("groq", 2, tokens_used=12960)  # 90% of 14400
    quota = tracker.get_remaining_quota("groq", 2, 14400)
    assert quota["status"] == "critical"
    
    # 100% usage
    tracker.log_usage("groq", 3, tokens_used=14400)
    quota = tracker.get_remaining_quota("groq", 3, 14400)
    assert quota["status"] == "exhausted"

def test_is_quota_available():
    """Test quota availability check"""
    tracker = QuotaTracker()
    
    # Use 14,300 tokens (100 remaining)
    tracker.log_usage("groq", 1, tokens_used=14300)
    
    # Check if 50 tokens available (should be True)
    assert tracker.is_quota_available("groq", 1, 14400, required=50)
    
    # Check if 200 tokens available (should be False)
    assert not tracker.is_quota_available("groq", 1, 14400, required=200)
```

#### 3.2 Integration Test

```python
def test_intelligent_key_selection():
    """Test that ModelRouter selects best key based on quota"""
    # Setup: 3 Groq keys with different usage
    router = ModelRouter()
    
    # Simulate usage:
    # Key 1: 14,000 tokens used (97% - critical)
    router.quota_tracker.log_usage("groq", 1, 14000)
    
    # Key 2: 500 tokens used (3% - healthy)
    router.quota_tracker.log_usage("groq", 2, 500)
    
    # Key 3: 10,000 tokens used (69% - healthy)
    router.quota_tracker.log_usage("groq", 3, 10000)
    
    # Make request
    response = router.chat([
        {"role": "user", "content": "test"}
    ])
    
    # Should use Key 2 (has most remaining quota)
    assert "groq" in response["model"]
    # Check logs to verify it used key_2
```

---

## 📊 Dashboard Integration (مثال)

```python
# Example API endpoint
@app.route("/api/admin/quota-stats")
@require_admin
def get_quota_stats():
    """Get quota statistics for all keys"""
    router = ModelRouter()
    
    # Get all keys
    all_keys = {}
    for provider in ["groq", "gemini", "mistral"]:
        provider_keys = router.secrets.get_provider_keys(provider)
        all_keys[provider] = provider_keys
    
    # Get quota info
    quota_stats = router.quota_tracker.get_all_quotas(all_keys)
    
    return jsonify(quota_stats)

# Response example:
# {
#   "groq": [
#     {
#       "id": 1,
#       "priority": 1,
#       "daily_limit": 14400,
#       "quota": {
#         "used": 11234,
#         "limit": 14400,
#         "remaining": 3166,
#         "percentage": 78.0,
#         "status": "warning",
#         "resets_at": "2025-11-19T00:00:00Z"
#       }
#     }
#   ]
# }
```

---

## 🧪 Testing Checklist

### ✅ Unit Tests

- [ ] `test_log_usage()` - Log tokens and requests
- [ ] `test_get_today_usage()` - Retrieve today's usage
- [ ] `test_get_remaining_quota()` - Calculate remaining
- [ ] `test_quota_warning_thresholds()` - 75%, 90%, 100% status
- [ ] `test_is_quota_available()` - Check availability
- [ ] `test_get_all_quotas()` - Batch retrieval
- [ ] `test_daily_reset()` - Verify 24h expiry
- [ ] `test_calculate_key_score()` - Intelligent scoring

### ✅ Integration Tests

- [ ] Test with real API calls
- [ ] Verify quota tracking accuracy
- [ ] Test intelligent key selection (prefers key with more quota)
- [ ] Test skip key when quota exhausted
- [ ] Test warning logs at 75% and 90%

### ✅ Manual Testing

```bash
# Test script
python -c "
from dev_platform.core.model_router import ModelRouter

router = ModelRouter()

# Make 50 requests
for i in range(50):
    response = router.chat([
        {'role': 'user', 'content': f'Request {i+1}'}
    ])
    print(f'{i+1}. Used: {response[\"model\"]}')

# Check quota
for provider in ['groq', 'gemini']:
    keys = router.secrets.get_provider_keys(provider)
    for key_info in keys:
        quota = router.quota_tracker.get_remaining_quota(
            provider,
            key_info['id'],
            key_info['daily_limit']
        )
        print(f\"{provider} Key {key_info['id']}: {quota['percentage']}% used\")
"
```

---

## 📦 Deliverables

1. ✅ `quota_tracker.py` - Complete implementation
2. ✅ Modified `model_router.py` - Integrated quota tracking
3. ✅ All unit tests passing
4. ✅ Integration tests passing
5. ✅ Documentation updated
6. ✅ Example API endpoint for quota stats

---

## 🚀 Handoff to Next Developer

بعد إكمال هذه المهمة، سلّم إلى **Developer AI-Keys-03** لتطبيق:
- **Notification System** - إشعارات عند المشاكل والتحذيرات
- **Email + Telegram alerts** عند 90%, failures, etc.

---

**آخر تحديث**: 2025-11-18  
**الحالة**: 🟡 جاهز للتنفيذ (بعد AI-Keys-01)
