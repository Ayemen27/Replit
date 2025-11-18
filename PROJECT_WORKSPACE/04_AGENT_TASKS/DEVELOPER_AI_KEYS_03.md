# 📢 Developer AI-Keys-03: Notification System

> **📍 المهمة**: ربط نظام الإشعارات لتنبيه مسؤول المنصة عند المشاكل والتحذيرات

**الأولوية**: 🟡🟡🟡 (متوسطة)  
**المدة المتوقعة**: 1-2 يوم  
**المتطلبات السابقة**: ✅ AI-Keys-01 و AI-Keys-02 مكتملين  
**المخرجات**: نظام إشعارات شامل (Email + Telegram + Dashboard)

---

## 📋 الهدف

إشعار مسؤول المنصة **فوراً** عند:
- 🟡 تحذير: مفتاح وصل 75% من حده
- 🔴 حرج: مفتاح وصل 90% من حده  
- ❌ خطأ: مفتاح فشل (authentication error)
- 🚨 حرج جداً: **جميع** المفاتيح فشلت

### الميزة الحالية

```python
# notification_system.py موجود لكن غير متصل! ❌
- الملف موجود في: tools/notification_system.py
- لكن ModelRouter لا يستخدمه
- لا إشعارات عملية
```

### الحل المطلوب

```python
# بعد الدمج ✅:
Groq Key 1 → 90% quota used
  ↓ فوراً
📧 Email: "⚠️ Groq Key 1 at 90% quota"
📱 Telegram: "⚠️ Groq Key 1 critical"
🔔 Dashboard Alert: Red banner
```

---

## 🎯 المخرجات المطلوبة

### ✅ Acceptance Criteria

1. ✅ **Integration مع notification_system**:
   - ربط `notification_system.py` الموجود
   - أو إنشاء wrapper خفيف إذا لزم الأمر

2. ✅ **قنوات الإشعار**:
   - Email (للأمور الحرجة)
   - Telegram (للتنبيهات السريعة)
   - Dashboard alerts (في الواجهة)
   - Logs (دائماً)

3. ✅ **Trigger Points**:
   - عند 75% quota → Warning (Telegram)
   - عند 90% quota → Critical (Email + Telegram)
   - عند Auth Error → Immediate (Email)
   - عند All Keys Failed → Emergency (Email + Telegram + Dashboard)

4. ✅ **Rate Limiting**:
   - لا نرسل نفس التنبيه كل دقيقة
   - Cooldown: 15 دقيقة لنفس النوع من التنبيه

5. ✅ **Configuration**:
   - يمكن تفعيل/تعطيل كل قناة
   - إعدادات في `.env`

---

## 📝 المهام التفصيلية

### Task 1: استكشاف notification_system الموجود (0.5 يوم)

```bash
# فحص الملف الموجود
cat ServerAutomationAI/tools/notification_system.py

# فهم:
- ما الميزات المتاحة؟
- هل يدعم Email/Telegram؟
- ما الـ API؟
- هل نحتاج modifications؟
```

### Task 2: إنشاء KeyManagementNotifier (0.5 يوم)

**ملف جديد**: `ServerAutomationAI/dev_platform/core/key_notifier.py`

```python
"""
Key Management Notification System
Alerts admin about key issues and quota warnings
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from .cache_manager import get_cache_manager

# Import existing notification system
try:
    from tools.notification_system import NotificationSystem
    HAS_NOTIFIER = True
except ImportError:
    HAS_NOTIFIER = False


logger = logging.getLogger(__name__)


class KeyManagementNotifier:
    """
    Notification system for API key management
    
    Features:
    - Email alerts for critical issues
    - Telegram alerts for warnings
    - Dashboard alerts
    - Rate limiting (avoid spam)
    - Configurable channels
    """
    
    def __init__(self):
        self.cache = get_cache_manager()
        
        # Load notification system if available
        if HAS_NOTIFIER:
            self.notifier = NotificationSystem()
        else:
            self.notifier = None
            logger.warning("NotificationSystem not available - alerts disabled")
        
        # Cooldown periods (seconds)
        self.cooldowns = {
            "quota_warning": 900,      # 15 minutes
            "quota_critical": 600,     # 10 minutes
            "auth_failure": 300,       # 5 minutes
            "all_failed": 180          # 3 minutes (critical!)
        }
    
    def alert_quota_warning(
        self,
        provider: str,
        key_id: int,
        quota_info: Dict[str, Any]
    ):
        """
        Alert when key reaches 75% quota
        
        Args:
            provider: "groq", "gemini", etc.
            key_id: Key ID
            quota_info: From quota_tracker.get_remaining_quota()
        """
        alert_id = f"quota_warning_{provider}_key{key_id}"
        
        # Check cooldown
        if self._is_cooldown_active(alert_id, "quota_warning"):
            logger.debug(f"Skipping {alert_id} - cooldown active")
            return
        
        percentage = quota_info["percentage"]
        remaining = quota_info["remaining"]
        
        message = (
            f"⚠️ **API Key Quota Warning**\n\n"
            f"Provider: {provider.title()}\n"
            f"Key ID: {key_id}\n"
            f"Usage: {percentage}%\n"
            f"Remaining: {remaining:,} tokens\n"
            f"Resets at: {quota_info['resets_at']}\n\n"
            f"Action: Monitor usage or add backup keys"
        )
        
        # Send Telegram (fast notification)
        self._send_telegram(message)
        
        # Log
        logger.warning(
            f"Quota warning sent for {provider} Key {key_id} ({percentage}%)"
        )
        
        # Set cooldown
        self._set_cooldown(alert_id, "quota_warning")
    
    def alert_quota_critical(
        self,
        provider: str,
        key_id: int,
        quota_info: Dict[str, Any]
    ):
        """
        Alert when key reaches 90% quota (critical!)
        
        Sends both Email and Telegram
        """
        alert_id = f"quota_critical_{provider}_key{key_id}"
        
        if self._is_cooldown_active(alert_id, "quota_critical"):
            return
        
        percentage = quota_info["percentage"]
        remaining = quota_info["remaining"]
        
        subject = f"🚨 CRITICAL: {provider.title()} Key {key_id} at {percentage}%"
        
        message = (
            f"🚨 **CRITICAL: API Key Quota Nearly Exhausted**\n\n"
            f"Provider: {provider.title()}\n"
            f"Key ID: {key_id}\n"
            f"Usage: {percentage}%\n"
            f"Remaining: {remaining:,} tokens\n"
            f"Resets at: {quota_info['resets_at']}\n\n"
            f"⚡ **Immediate Action Required:**\n"
            f"- Add backup keys for {provider}\n"
            f"- Monitor usage closely\n"
            f"- Consider rate limiting\n\n"
            f"System will auto-switch to next available key when exhausted."
        )
        
        # Send both channels
        self._send_email(subject, message)
        self._send_telegram(message)
        
        logger.error(
            f"CRITICAL quota alert sent for {provider} Key {key_id} ({percentage}%)"
        )
        
        self._set_cooldown(alert_id, "quota_critical")
    
    def alert_key_authentication_failed(
        self,
        provider: str,
        key_id: int,
        error_details: str
    ):
        """
        Alert when key authentication fails (expired/invalid key)
        """
        alert_id = f"auth_failed_{provider}_key{key_id}"
        
        if self._is_cooldown_active(alert_id, "auth_failure"):
            return
        
        subject = f"❌ {provider.title()} Key {key_id} Authentication Failed"
        
        message = (
            f"❌ **API Key Authentication Failure**\n\n"
            f"Provider: {provider.title()}\n"
            f"Key ID: {key_id}\n"
            f"Error: {error_details}\n"
            f"Time: {datetime.now().isoformat()}\n\n"
            f"**Action Required:**\n"
            f"1. Check if key is expired\n"
            f"2. Verify key in provider dashboard\n"
            f"3. Update .env with new key if needed\n"
            f"4. Restart platform after update\n\n"
            f"Key has been quarantined for 5 minutes.\n"
            f"Requests are being routed to backup keys."
        )
        
        self._send_email(subject, message)
        self._send_telegram(message)
        
        logger.error(f"Auth failure alert sent for {provider} Key {key_id}")
        
        self._set_cooldown(alert_id, "auth_failure")
    
    def alert_all_keys_failed(
        self,
        errors_by_provider: Dict[str, str]
    ):
        """
        🚨 EMERGENCY: All AI providers failed!
        
        This is the most critical alert - platform AI is down!
        """
        alert_id = "all_keys_failed"
        
        if self._is_cooldown_active(alert_id, "all_failed"):
            return
        
        subject = "🚨 EMERGENCY: All AI Keys Failed!"
        
        # Format errors
        error_list = "\n".join([
            f"- {provider}: {error}"
            for provider, error in errors_by_provider.items()
        ])
        
        message = (
            f"🚨 **EMERGENCY: All AI Providers Down**\n\n"
            f"**Status:** Platform AI is completely unavailable\n"
            f"**Time:** {datetime.now().isoformat()}\n\n"
            f"**Failed Providers:**\n{error_list}\n\n"
            f"**Impact:**\n"
            f"- All AI features are disabled\n"
            f"- Users seeing fallback messages\n"
            f"- Platform operating in degraded mode\n\n"
            f"**IMMEDIATE ACTIONS REQUIRED:**\n"
            f"1. Check all API keys in .env\n"
            f"2. Verify keys in provider dashboards\n"
            f"3. Check for service outages:\n"
            f"   - Groq: https://status.groq.com\n"
            f"   - Google: https://status.cloud.google.com\n"
            f"4. Add new backup keys immediately\n"
            f"5. Monitor recovery status\n\n"
            f"This is a critical system alert!"
        )
        
        # Send all channels
        self._send_email(subject, message, priority="high")
        self._send_telegram(message)
        self._send_dashboard_alert("critical", "All AI providers failed", message)
        
        logger.critical("EMERGENCY: All AI keys failed alert sent!")
        
        self._set_cooldown(alert_id, "all_failed")
    
    def alert_provider_recovered(
        self,
        provider: str,
        key_id: int
    ):
        """
        Good news: A provider recovered!
        """
        message = (
            f"✅ **Provider Recovered**\n\n"
            f"{provider.title()} Key {key_id} is back online!\n"
            f"Time: {datetime.now().isoformat()}\n\n"
            f"System resumed normal operations."
        )
        
        self._send_telegram(message)
        logger.info(f"{provider} Key {key_id} recovery alert sent")
    
    # ========== Helper Methods ==========
    
    def _send_email(
        self,
        subject: str,
        message: str,
        priority: str = "normal"
    ):
        """Send email notification"""
        if not self.notifier:
            logger.warning("Email notification skipped - notifier not available")
            return
        
        try:
            self.notifier.send_email(
                subject=subject,
                body=message,
                priority=priority
            )
            logger.debug(f"Email sent: {subject}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
    
    def _send_telegram(self, message: str):
        """Send Telegram notification"""
        if not self.notifier:
            logger.warning("Telegram notification skipped - notifier not available")
            return
        
        try:
            self.notifier.send_telegram(message)
            logger.debug("Telegram message sent")
        except Exception as e:
            logger.error(f"Failed to send Telegram: {e}")
    
    def _send_dashboard_alert(
        self,
        level: str,
        title: str,
        message: str
    ):
        """Send dashboard alert (for UI display)"""
        # Store in cache for dashboard to retrieve
        alert = {
            "level": level,  # "info", "warning", "critical"
            "title": title,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        # Get existing alerts
        alerts = self.cache.cache_get("dashboard_alerts") or []
        alerts.insert(0, alert)  # Add to front
        
        # Keep last 10 alerts only
        alerts = alerts[:10]
        
        # Save
        self.cache.cache_set("dashboard_alerts", alerts, expire=86400)  # 24h
        
        logger.debug(f"Dashboard alert added: {title}")
    
    def _is_cooldown_active(
        self,
        alert_id: str,
        alert_type: str
    ) -> bool:
        """Check if alert is in cooldown period"""
        cache_key = f"alert_cooldown_{alert_id}"
        last_sent = self.cache.cache_get(cache_key)
        
        if not last_sent:
            return False
        
        cooldown_seconds = self.cooldowns.get(alert_type, 600)
        cooldown_until = last_sent + cooldown_seconds
        
        return datetime.now().timestamp() < cooldown_until
    
    def _set_cooldown(self, alert_id: str, alert_type: str):
        """Set cooldown for an alert"""
        cache_key = f"alert_cooldown_{alert_id}"
        self.cache.cache_set(
            cache_key,
            datetime.now().timestamp(),
            expire=self.cooldowns.get(alert_type, 600)
        )


# Global instance
_key_notifier = None

def get_key_notifier() -> KeyManagementNotifier:
    """Get global key notifier instance"""
    global _key_notifier
    if _key_notifier is None:
        _key_notifier = KeyManagementNotifier()
    return _key_notifier
```

---

### Task 3: دمج مع ModelRouter (0.5 يوم)

**الملف**: `ServerAutomationAI/dev_platform/core/model_router.py`

```python
from .key_notifier import get_key_notifier

class ModelRouter:
    def __init__(self):
        # ... existing ...
        self.key_notifier = get_key_notifier()  # NEW!
    
    def chat(self, ...):
        # ... existing code ...
        
        # بعد نجاح الطلب:
        quota_info = self.quota_tracker.get_remaining_quota(...)
        
        # Check and alert
        if quota_info["status"] == "warning":
            self.key_notifier.alert_quota_warning(
                provider, key_id, quota_info
            )
        elif quota_info["status"] == "critical":
            self.key_notifier.alert_quota_critical(
                provider, key_id, quota_info
            )
        
        # ... rest of code ...
    
    def _quarantine_key(self, provider, key_id, model_config):
        # ... existing quarantine code ...
        
        # NEW: Send alert
        self.key_notifier.alert_key_authentication_failed(
            provider,
            key_id,
            "Invalid or expired API key"
        )
    
    def _graceful_downgrade(self, messages, error, errors_by_provider):
        # ... existing code ...
        
        # If all providers failed
        if errors_by_provider and len(errors_by_provider) >= len(self.available_models):
            # NEW: Send emergency alert
            self.key_notifier.alert_all_keys_failed(errors_by_provider)
        
        # ... rest of code ...
```

---

### Task 4: Configuration (.env) (0.25 يوم)

```bash
# .env additions

# ============================================
# Notification Settings
# ============================================

# Email
NOTIFICATION_EMAIL_ENABLED=true
NOTIFICATION_EMAIL_TO=admin@platform.com
NOTIFICATION_EMAIL_FROM=alerts@platform.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Telegram
NOTIFICATION_TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=123456789:ABC-DEF...
TELEGRAM_CHAT_ID=987654321

# Dashboard
NOTIFICATION_DASHBOARD_ENABLED=true

# Cooldown periods (seconds)
ALERT_COOLDOWN_WARNING=900      # 15 minutes
ALERT_COOLDOWN_CRITICAL=600     # 10 minutes
ALERT_COOLDOWN_AUTH_FAIL=300    # 5 minutes
ALERT_COOLDOWN_ALL_FAILED=180   # 3 minutes
```

---

### Task 5: Dashboard API (0.25 يوم)

```python
# Example API endpoint
@app.route("/api/admin/alerts")
@require_admin
def get_dashboard_alerts():
    """Get latest dashboard alerts"""
    cache = get_cache_manager()
    alerts = cache.cache_get("dashboard_alerts") or []
    
    return jsonify({
        "alerts": alerts,
        "count": len(alerts)
    })

# Frontend (React example)
function AlertsBanner() {
    const [alerts, setAlerts] = useState([]);
    
    useEffect(() => {
        fetch('/api/admin/alerts')
            .then(res => res.json())
            .then(data => setAlerts(data.alerts));
    }, []);
    
    const criticalAlerts = alerts.filter(a => a.level === 'critical');
    
    if (criticalAlerts.length === 0) return null;
    
    return (
        <div className="alert-banner critical">
            <strong>🚨 {criticalAlerts[0].title}</strong>
            <p>{criticalAlerts[0].message}</p>
        </div>
    );
}
```

---

## 🧪 Testing Checklist

### ✅ Unit Tests

- [ ] `test_alert_quota_warning()` - Send warning at 75%
- [ ] `test_alert_quota_critical()` - Send critical at 90%
- [ ] `test_alert_auth_failed()` - Auth failure alert
- [ ] `test_alert_all_failed()` - Emergency alert
- [ ] `test_cooldown_prevents_spam()` - Cooldown works
- [ ] `test_dashboard_alerts_stored()` - Dashboard storage

### ✅ Integration Tests

- [ ] Real Email sending (test SMTP)
- [ ] Real Telegram sending (test bot)
- [ ] Trigger warnings in ModelRouter
- [ ] Verify cooldown behavior
- [ ] Test all-keys-failed scenario

### ✅ Manual Testing

```bash
# Test notifications
python -c "
from dev_platform.core.key_notifier import get_key_notifier

notifier = get_key_notifier()

# Test warning
notifier.alert_quota_warning('groq', 1, {
    'percentage': 78.0,
    'remaining': 3166,
    'resets_at': '2025-11-19T00:00:00Z'
})

# Check email inbox and Telegram
print('Check your email and Telegram!')
"
```

---

## 📦 Deliverables

1. ✅ `key_notifier.py` - Complete implementation
2. ✅ Modified `model_router.py` - Integrated notifications
3. ✅ `.env.example` updated with notification settings
4. ✅ Dashboard API endpoint for alerts
5. ✅ All unit tests passing
6. ✅ Integration tests passing
7. ✅ Manual testing completed (real email/telegram sent)

---

## 🚀 Handoff to Next Developer

بعد إكمال هذه المهمة، سلّم إلى **Developer AI-Keys-04** لتطبيق:
- **Monitoring Dashboard** - واجهة لمراقبة المفاتيح والإحصائيات

---

**آخر تحديث**: 2025-11-18  
**الحالة**: 🟡 جاهز للتنفيذ (بعد AI-Keys-01 و AI-Keys-02)
