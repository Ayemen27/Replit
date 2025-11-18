# Documentation Index

## 📚 Available Documentation

### Security & Secrets Management
- **[SECRETS_MANAGEMENT.md](SECRETS_MANAGEMENT.md)** - Comprehensive guide to managing secrets, credentials, and API keys
  - Available secrets reference (Telegram, Email, Dashboard, AI models)
  - Secrets CLI tool usage
  - Security features and best practices
  - Configuration integration examples
  - Troubleshooting guide

- **[SECURITY_SETUP.md](SECURITY_SETUP.md)** - Security setup and configuration guide
  - Dashboard token management
  - Encryption key handling
  - Secure deployment practices

## 🔑 Quick Reference

### View All Secrets
```bash
python dev_platform/tools/secrets_cli.py list
```

### Check Notification Credentials
```bash
# Telegram
python dev_platform/tools/secrets_cli.py get TELEGRAM_BOT_TOKEN
python dev_platform/tools/secrets_cli.py get TELEGRAM_CHAT_ID

# Email
python dev_platform/tools/secrets_cli.py get SMTP_USER
python dev_platform/tools/secrets_cli.py get EMAIL_HOST
```

### Dashboard Token
```bash
python dev_platform/tools/secrets_cli.py dashboard-token
```

## 📋 Documented Secrets

### ✅ Notification System
All credentials are stored in SecretsManager:

**Telegram:**
- `TELEGRAM_BOT_TOKEN` - Bot authentication token
- `TELEGRAM_CHAT_ID` - Target chat ID

**Email:**
- `SMTP_USER` - Email sender address
- `SMTP_PASSWORD` - SMTP authentication
- `EMAIL_HOST` - SMTP server hostname
- `EMAIL_PORT` - SMTP server port
- `SUPPORT_EMAIL` - Support/recipient email

**Status:** ✅ All credentials present and configured

### ✅ Dashboard
- `DASHBOARD_API_TOKEN` - Web dashboard API authentication

### ✅ AI Models
- `GROQ_API_KEY` - Groq LLM access
- `GEMINI_API_KEY` - Google Gemini access
- `MISTRAL_API_KEY` - Mistral AI access
- `HF_API_KEY` - HuggingFace access

### ✅ Database
- `DATABASE_URL`, `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`

## 🔒 Security Notes

1. **Never commit secrets** - All secret files are in `.gitignore`
2. **Backup encryption key** - Store `data/.encryption_key` securely
3. **Rotate regularly** - Use CLI tool to rotate dashboard tokens
4. **Production deployment** - Use platform-specific secret managers

## 📞 Support

For issues or questions:
1. Check [SECRETS_MANAGEMENT.md](SECRETS_MANAGEMENT.md) troubleshooting section
2. Review [SECURITY_SETUP.md](SECURITY_SETUP.md) for security guidance
3. Use the Secrets CLI tool for management tasks

---

**Last Updated:** November 15, 2025
