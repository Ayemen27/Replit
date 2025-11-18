# Secrets Management Documentation

## Overview

The AI Multi-Agent Platform uses a centralized **SecretsManager** for secure storage and management of all sensitive credentials, API keys, and tokens. All secrets are encrypted using Fernet (symmetric encryption) and stored securely.

## 📋 Available Secrets

### 🔐 Dashboard Authentication
| Variable | Purpose | Status |
|----------|---------|--------|
| `DASHBOARD_API_TOKEN` | Web dashboard API authentication | ✅ Active |

### 📱 Telegram Notifications
| Variable | Purpose | Value Example | Status |
|----------|---------|---------------|--------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot authentication | `7858688325:AAGUuUS...` | ✅ Active |
| `TELEGRAM_CHAT_ID` | Target chat for notifications | `6988440994` | ✅ Active |

### 📧 Email Notifications
| Variable | Purpose | Value Example | Status |
|----------|---------|---------------|--------|
| `EMAIL_HOST` | SMTP server hostname | `mail.privateemail.com` | ✅ Active |
| `EMAIL_PORT` | SMTP server port | `587` | ✅ Active |
| `SMTP_USER` | Email sender address | `support@binarjoin...` | ✅ Active |
| `SMTP_PASSWORD` | Email authentication password | `***` (encrypted) | ✅ Active |
| `SUPPORT_EMAIL` | Support/recipient email | `support@binarjoin...` | ✅ Active |

### 🤖 AI Model API Keys
| Variable | Purpose | Status |
|----------|---------|--------|
| `GROQ_API_KEY` | Groq LLM API access | ✅ Active |
| `GEMINI_API_KEY` | Google Gemini API access | ⚠️ Needs update |
| `MISTRAL_API_KEY` | Mistral AI API access | ✅ Active |
| `HF_API_KEY` | HuggingFace API access | ✅ Active |

### 🗄️ Database Credentials
| Variable | Purpose | Status |
|----------|---------|--------|
| `DATABASE_URL` | PostgreSQL connection string | ✅ Active |
| `PGHOST` | PostgreSQL hostname | ✅ Active |
| `PGPORT` | PostgreSQL port | ✅ Active |
| `PGDATABASE` | PostgreSQL database name | ✅ Active |
| `PGUSER` | PostgreSQL username | ✅ Active |
| `PGPASSWORD` | PostgreSQL password | ✅ Active |

## 🛠️ Secrets CLI Tool

### View All Secrets
```bash
python dev_platform/tools/secrets_cli.py list
```

### Get Specific Secret
```bash
python dev_platform/tools/secrets_cli.py get TELEGRAM_BOT_TOKEN
python dev_platform/tools/secrets_cli.py get SMTP_USER
```

### Set/Update Secret
```bash
# Auto-generate secure value
python dev_platform/tools/secrets_cli.py set NEW_API_KEY --auto-generate

# Set manually
python dev_platform/tools/secrets_cli.py set NEW_API_KEY --value "your-secret-value"
```

### Delete Secret
```bash
python dev_platform/tools/secrets_cli.py delete OLD_SECRET_KEY
```

### Rotate Dashboard Token
```bash
python dev_platform/tools/secrets_cli.py rotate
```

## 🔒 Security Features

### Encryption
- **Algorithm:** Fernet (symmetric encryption based on AES-128-CBC)
- **Key Storage:** `data/.encryption_key` (600 permissions - owner read-only)
- **Encrypted Storage:** `data/secrets.enc` (600 permissions)

### Access Control
- Secrets files are readable only by the file owner
- Encryption key is auto-generated on first use
- All secrets are masked when listed

### Environment Integration
- Secrets from SecretsManager are automatically loaded as environment variables
- Config files reference secrets via `${VARIABLE_NAME}` syntax
- No hardcoded credentials in configuration files

## 📝 Configuration Integration

### Before (Insecure)
```yaml
notifications:
  telegram:
    bot_token: "hardcoded-token-here"
    chat_id: "123456789"
```

### After (Secure)
```yaml
notifications:
  telegram:
    bot_token: "${TELEGRAM_BOT_TOKEN}"
    chat_id: "${TELEGRAM_CHAT_ID}"
```

## 🔄 How It Works

1. **Initialization:**
   - SecretsManager loads on application startup
   - Checks for encryption key, generates if missing
   - Loads environment variables from `.env` and encrypted storage

2. **Priority Order:**
   - Environment variables (highest priority)
   - Encrypted storage (`data/secrets.enc`)
   - Default values (if specified)

3. **Runtime Access:**
   ```python
   from dev_platform.core.secrets_manager import get_secrets_manager
   
   secrets = get_secrets_manager()
   telegram_token = secrets.get("TELEGRAM_BOT_TOKEN")
   ```

## ✅ Verification

### Check Telegram Credentials
```bash
python -c "from dev_platform.core.secrets_manager import get_secrets_manager; s = get_secrets_manager(); print('Bot Token:', s.get('TELEGRAM_BOT_TOKEN')[:20]+'...'); print('Chat ID:', s.get('TELEGRAM_CHAT_ID'))"
```

### Check Email Credentials
```bash
python -c "from dev_platform.core.secrets_manager import get_secrets_manager; s = get_secrets_manager(); print('SMTP User:', s.get('SMTP_USER')); print('Email Host:', s.get('EMAIL_HOST'))"
```

### Check Dashboard Token
```bash
python dev_platform/tools/secrets_cli.py dashboard-token
```

## 🚨 Important Notes

1. **Never commit secrets to Git:**
   - `.env` is in `.gitignore`
   - `data/secrets.enc` is in `.gitignore`
   - `data/.encryption_key` is in `.gitignore`

2. **Backup encryption key:**
   - Store `data/.encryption_key` securely
   - Without it, encrypted secrets cannot be decrypted

3. **Rotate regularly:**
   - Dashboard tokens should be rotated periodically
   - Use `secrets_cli.py rotate` command

4. **Production deployment:**
   - Set environment variables directly in production
   - Avoid copying `.env` files to production servers
   - Use platform-specific secret managers (AWS Secrets Manager, Azure Key Vault, etc.)

## 📚 Related Documentation

- [Security Setup Guide](SECURITY_SETUP.md)
- [Notification System Configuration](../tools/notification_system.py)
- [Dashboard Authentication](../dev_platform/web/api_server.py)

## 🆘 Troubleshooting

### "Secret not found" error
```bash
# List all available secrets
python dev_platform/tools/secrets_cli.py list

# Set the missing secret
python dev_platform/tools/secrets_cli.py set SECRET_NAME --value "secret-value"
```

### "Cannot decrypt" error
- Encryption key may be corrupted
- Regenerate secrets if backup is not available
- Check file permissions on `data/.encryption_key`

### Notification not working
```bash
# Verify credentials are loaded
python -c "from dev_platform.core.secrets_manager import get_secrets_manager; import yaml; s = get_secrets_manager(); c = yaml.safe_load(open('configs/config.yaml')); print('Telegram enabled:', c['notifications']['telegram']['enabled']); print('Email enabled:', c['notifications']['email']['enabled'])"
```

---

**Last Updated:** November 15, 2025  
**Maintainer:** AI Multi-Agent Platform Team
