# Notification System Guide

## Overview

The AI Multi-Agent Platform includes a robust notification system that supports multiple channels (Telegram and Email) with automatic retry logic, health monitoring, and seamless SecretsManager integration.

## ✨ Features

### 1. **SecretsManager Integration**
- Automatic credential loading from encrypted storage
- Environment variable fallback support
- No hardcoded credentials in configuration files

### 2. **Retry Logic with Exponential Backoff**
- Automatic retry on failure (3 attempts)
- Exponential backoff: 1s → 2s → 4s
- Detailed error logging with attempt tracking

### 3. **Configuration Validation**
- Automatic validation of required fields
- Auto-disable channels with incomplete configuration
- Clear warning messages for missing credentials

### 4. **Health Check API**
- Test Telegram bot connectivity
- Verify SMTP server connection
- Get channel status without sending messages

### 5. **Unified Dispatch API**
- Simple, consistent interface across channels
- Support for multiple severity levels
- Flexible channel selection

## 🔧 Configuration

### Setup Credentials in SecretsManager

```bash
# Set Telegram credentials
python dev_platform/tools/secrets_cli.py set TELEGRAM_BOT_TOKEN --value "your-bot-token"
python dev_platform/tools/secrets_cli.py set TELEGRAM_CHAT_ID --value "your-chat-id"

# Set Email credentials
python dev_platform/tools/secrets_cli.py set SMTP_USER --value "your-email@example.com"
python dev_platform/tools/secrets_cli.py set SMTP_PASSWORD --value "your-password"
python dev_platform/tools/secrets_cli.py set EMAIL_HOST --value "smtp.example.com"
python dev_platform/tools/secrets_cli.py set EMAIL_PORT --value "587"
python dev_platform/tools/secrets_cli.py set SUPPORT_EMAIL --value "support@example.com"
```

### Enable Notifications in config.yaml

```yaml
notifications:
  telegram:
    enabled: true
    bot_token: "${TELEGRAM_BOT_TOKEN}"    # Loaded from SecretsManager
    chat_id: "${TELEGRAM_CHAT_ID}"
    api_url: "https://api.telegram.org/bot"
    timeout: 10
    retry_attempts: 3
  
  email:
    enabled: true
    smtp_server: "${EMAIL_HOST}"          # Loaded from SecretsManager
    smtp_port: "${EMAIL_PORT}"
    sender_email: "${SMTP_USER}"
    sender_password: "${SMTP_PASSWORD}"
    recipient_emails:
      - "${SUPPORT_EMAIL}"
    use_tls: true
    timeout: 30
```

## 📝 Usage Examples

### Basic Usage

```python
from tools.notification_system import NotificationSystem

# Initialize (automatically loads credentials from SecretsManager)
notifier = NotificationSystem()

# Send simple info message
notifier.send_info("System started successfully")

# Send warning
notifier.send_warning_alert("High CPU usage detected", details="CPU: 85%")

# Send critical alert
notifier.send_critical_alert("Database connection lost", details="PostgreSQL unreachable")
```

### Using the Unified Dispatch API

```python
# Send to all enabled channels
result = notifier.dispatch(
    message="Deployment completed",
    level="info"
)

# Send to specific channel only
result = notifier.dispatch(
    message="Emergency: System overload",
    level="critical",
    channels=["telegram"]  # Only send to Telegram
)

# Check results
for channel, status in result.items():
    if status['success']:
        print(f"✅ {channel}: Sent successfully")
    else:
        print(f"❌ {channel}: {status['error']}")
```

### Health Check

```python
# Check channel availability
health = notifier.health_check()

if health['telegram']['available']:
    print(f"✅ Telegram bot online: @{health['telegram']['bot_name']}")
else:
    print(f"❌ Telegram unavailable: {health['telegram']['error']}")

if health['email']['available']:
    print(f"✅ Email server connected: {health['email']['server']}")
else:
    print(f"❌ Email unavailable: {health['email']['error']}")
```

### Custom Integration with Agents

```python
from tools.notification_system import NotificationSystem

class MonitoringAgent:
    def __init__(self):
        self.notifier = NotificationSystem()
    
    def on_alert(self, alert_type, message, details=None):
        """Send alerts when monitoring detects issues"""
        result = self.notifier.dispatch(
            message=f"{alert_type}: {message}",
            level="warning",
            channels=["telegram", "email"]
        )
        
        return result
```

## 🔍 API Reference

### Core Methods

#### `send_notification(message, level='info', channels=None)`
Send notification with specified level and channels.

**Parameters:**
- `message` (str): Message content
- `level` (str): Severity level (info, warning, alert, critical)
- `channels` (list): Channel list or None for all enabled

**Returns:** Dict with results for each channel

#### `dispatch(message, level='info', channels=None)`
Unified API for sending notifications (alias for `send_notification`).

**Parameters:** Same as `send_notification`

**Returns:** Same as `send_notification`

#### `health_check()`
Check health and availability of all notification channels.

**Returns:** Dict with channel status and details

```python
{
    'telegram': {
        'available': True,
        'bot_name': 'MyBot',
        'error': None
    },
    'email': {
        'available': True,
        'server': 'smtp.example.com',
        'error': None
    }
}
```

### Convenience Methods

#### `send_info(message)`
Send informational notification.

#### `send_warning_alert(message, details=None)`
Send warning alert with optional details.

#### `send_critical_alert(message, details=None)`
Send critical alert with optional details.

#### `send_alert(alert_type, message, details=None)`
Send custom alert type.

## 🔒 Security Features

### 1. **Credential Protection**
- All secrets stored encrypted via SecretsManager
- Fernet encryption (AES-128-CBC)
- No credentials in logs or error messages

### 2. **Validation**
- Automatic validation on initialization
- Channels auto-disabled if credentials missing
- Clear warnings without exposing sensitive data

### 3. **Environment Isolation**
- Development/production separation via SecretsManager
- Environment variable support
- Configuration file references only

## 🚨 Troubleshooting

### Telegram Not Working

```bash
# Check credentials
python dev_platform/tools/secrets_cli.py get TELEGRAM_BOT_TOKEN
python dev_platform/tools/secrets_cli.py get TELEGRAM_CHAT_ID

# Test health
python -c "
from tools.notification_system import NotificationSystem
n = NotificationSystem()
print(n.health_check()['telegram'])
"
```

**Common Issues:**
- Invalid bot token: Verify token from @BotFather
- Wrong chat ID: Send `/start` to bot and get ID from @userinfobot
- API timeout: Check network connectivity

### Email Not Working

```bash
# Check credentials
python dev_platform/tools/secrets_cli.py get SMTP_USER
python dev_platform/tools/secrets_cli.py get EMAIL_HOST

# Test health
python -c "
from tools.notification_system import NotificationSystem
n = NotificationSystem()
print(n.health_check()['email'])
"
```

**Common Issues:**
- SMTP authentication failed: Check password/app-specific password
- Connection timeout: Verify SMTP server and port
- TLS error: Ensure `use_tls` matches server requirements

### Retry Logic

The system automatically retries failed deliveries:
- Attempt 1: Immediate
- Attempt 2: After 1 second
- Attempt 3: After 2 seconds
- Attempt 4 (if configured): After 4 seconds

Check logs for retry attempts:
```bash
grep "attempt" logs/notification_system.log
```

## 📊 Monitoring

### Log Locations
- System logs: `logs/notification_system.log`
- Application logs: Check agent-specific logs

### Key Log Patterns

**Successful Delivery:**
```
Telegram notification sent successfully (attempt 1)
Email sent to 1 recipients (attempt 1)
```

**Retry in Progress:**
```
Telegram send failed (attempt 1): Connection timeout
Retrying in 1s...
Telegram notification sent successfully (attempt 2)
```

**Complete Failure:**
```
Failed to send Telegram notification after 3 attempts: HTTP 401
```

## 🎯 Best Practices

### 1. **Use Appropriate Severity Levels**
- `info`: Regular operational messages
- `warning`: Issues requiring attention
- `alert`: Important system events
- `critical`: Emergencies requiring immediate action

### 2. **Channel Selection**
- Use Telegram for real-time alerts
- Use Email for detailed reports and documentation
- Use both for critical alerts

### 3. **Message Format**
```python
# Good: Clear, actionable message
notifier.send_critical_alert(
    message="Database connection lost",
    details="Host: db.example.com\nError: Connection timeout\nAction: Check network and DB status"
)

# Bad: Vague message
notifier.send_alert("error", "something wrong")
```

### 4. **Health Monitoring**
```python
# Periodic health checks
import schedule

def check_notification_health():
    notifier = NotificationSystem()
    health = notifier.health_check()
    
    for channel, status in health.items():
        if not status['available']:
            log_error(f"Notification channel {channel} is down: {status['error']}")

schedule.every(1).hours.do(check_notification_health)
```

## 🔄 Migration from Old Version

### Before (Old API)
```python
from tools.notification_system import NotificationSystem

notifier = NotificationSystem()
notifier.send_notification("Test message", level='info')
```

### After (Enhanced API)
```python
from tools.notification_system import NotificationSystem

# Same initialization - now with SecretsManager integration
notifier = NotificationSystem()

# Same method - now with retry logic
notifier.send_notification("Test message", level='info')

# Or use new unified API
notifier.dispatch("Test message", level='info')

# New: Health check
health = notifier.health_check()
```

**Migration is fully backward compatible!** Existing code continues to work with enhanced features automatically.

## 📚 Related Documentation

- [Secrets Management Guide](SECRETS_MANAGEMENT.md)
- [Security Setup](SECURITY_SETUP.md)
- [Agent Integration Guide](../agents/README.md)

---

**Last Updated:** November 15, 2025  
**Version:** 2.3.0 (Enhanced with SecretsManager + Retry Logic)
