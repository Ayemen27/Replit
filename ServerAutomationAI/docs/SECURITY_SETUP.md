# 🔐 Security Setup Guide - Phase 2D

This guide covers secure configuration for the AI Multi-Agent Platform dashboard and API authentication.

## Overview

Phase 2D replaces the insecure default token system with **encrypted secrets management** using:
- **SecretsManager**: Fernet encryption for sensitive data
- **Auto-generated tokens**: Cryptographically secure random tokens
- **Key rotation**: Built-in CLI tools for rotating API tokens

---

## 🚀 Quick Start

### 1. Dashboard Token Setup (Automatic)

The dashboard **automatically generates** a secure token on first run:

```bash
# Start the dashboard
python dev_platform/web_dashboard.py --host 0.0.0.0 --port 5000
```

The token is saved to **encrypted storage** at `data/secrets.enc`.

### 2. Retrieve Your Token

```bash
# Method 1: Using secrets CLI
python dev_platform/tools/secrets_cli.py dashboard-token

# Method 2: Python command
python -c "from dev_platform.core.secrets_manager import get_secrets_manager; print(get_secrets_manager().get('DASHBOARD_API_TOKEN'))"
```

### 3. Use the Token

```bash
# Example API request
export TOKEN="your-token-here"
curl -H "X-API-Token: $TOKEN" http://localhost:5000/api/metrics
```

---

## 🛠️ Secrets Management CLI

The `secrets_cli.py` tool provides comprehensive secret management:

### Get Dashboard Token
```bash
python dev_platform/tools/secrets_cli.py dashboard-token
```

### Set a New Secret
```bash
# Manual value
python dev_platform/tools/secrets_cli.py set MY_API_KEY "myvalue123"

# Auto-generate secure token
python dev_platform/tools/secrets_cli.py set MY_TOKEN --generate --encrypt

# Show generated value
python dev_platform/tools/secrets_cli.py set MY_TOKEN --generate --encrypt --show
```

### List All Secrets
```bash
# List with masked values
python dev_platform/tools/secrets_cli.py list

# Show actual values (careful!)
python dev_platform/tools/secrets_cli.py list --show

# Encrypted secrets only
python dev_platform/tools/secrets_cli.py list --encrypted-only
```

### Rotate a Token (Key Rotation)
```bash
# Rotate dashboard token
python dev_platform/tools/secrets_cli.py rotate DASHBOARD_API_TOKEN

# Skip confirmation
python dev_platform/tools/secrets_cli.py rotate DASHBOARD_API_TOKEN -y

# Show new value
python dev_platform/tools/secrets_cli.py rotate DASHBOARD_API_TOKEN --show
```

### Delete a Secret
```bash
# With confirmation
python dev_platform/tools/secrets_cli.py delete OLD_API_KEY

# Skip confirmation
python dev_platform/tools/secrets_cli.py delete OLD_API_KEY -y
```

---

## 🔒 Security Features

### 1. Encrypted Storage
- All sensitive secrets stored in `data/secrets.enc` using **Fernet encryption**
- Encryption key stored in `data/.encryption_key` with **600 permissions** (owner-only)
- No plaintext secrets in code or logs

### 2. Auto-Generated Tokens
- Cryptographically secure tokens using Python's `secrets` module
- Default length: 32 bytes (256-bit security)
- URL-safe base64 encoding

### 3. Priority Chain
Secrets are resolved in this order:
1. **Environment variables** (`.env` file)
2. **Encrypted storage** (`data/secrets.enc`)
3. **Auto-generation** (for dashboard token only)

### 4. Token Rotation
- Built-in CLI command for rotating tokens
- Old tokens immediately invalidated
- No downtime required (update clients after rotation)

---

## 📋 Production Deployment Checklist

### Before Production:

- [ ] **Rotate dashboard token**
  ```bash
  python dev_platform/tools/secrets_cli.py rotate DASHBOARD_API_TOKEN
  ```

- [ ] **Secure encryption key file**
  ```bash
  chmod 600 data/.encryption_key
  ```

- [ ] **Backup encryption key** (store securely!)
  ```bash
  cp data/.encryption_key ~/secure-backup/.encryption_key.backup
  ```

- [ ] **Set secure file permissions**
  ```bash
  chmod 600 data/secrets.enc
  chmod 600 .env
  ```

- [ ] **Document token location** for team access

- [ ] **Set up token rotation schedule** (recommended: every 90 days)

---

## 🔄 Token Rotation Schedule

### Recommended Schedule
- **Dashboard Token**: Rotate every 90 days
- **API Keys (external)**: Follow provider recommendations
- **Emergency Rotation**: Immediately if token compromised

### Rotation Procedure
1. Generate new token:
   ```bash
   python dev_platform/tools/secrets_cli.py rotate DASHBOARD_API_TOKEN --show
   ```

2. Update all API clients with new token

3. Verify new token works:
   ```bash
   curl -H "X-API-Token: NEW_TOKEN" http://localhost:5000/api/health
   ```

4. Old token is automatically invalidated

---

## 🐛 Troubleshooting

### "Invalid or missing API token" Error
```bash
# Check if token exists
python dev_platform/tools/secrets_cli.py get DASHBOARD_API_TOKEN

# If not found, regenerate
python dev_platform/tools/secrets_cli.py dashboard-token
```

### Cannot Read Encrypted Secrets
```bash
# Check encryption key permissions
ls -la data/.encryption_key

# Should be: -rw------- (600)
chmod 600 data/.encryption_key
```

### Lost Encryption Key
⚠️ **Cannot decrypt secrets without the encryption key!**
- Restore from backup if available
- Otherwise, regenerate all secrets:
  ```bash
  rm data/.encryption_key data/secrets.enc
  python dev_platform/tools/secrets_cli.py dashboard-token
  ```

---

## 📁 File Structure

```
.
├── .env                          # Environment variables (optional)
├── data/
│   ├── .encryption_key           # Fernet encryption key (600 permissions)
│   └── secrets.enc               # Encrypted secrets storage
├── dev_platform/
│   ├── core/
│   │   └── secrets_manager.py    # SecretsManager class
│   ├── tools/
│   │   └── secrets_cli.py        # CLI tool for secret management
│   └── web/
│       └── api_server.py         # Dashboard server (uses SecretsManager)
└── docs/
    └── SECURITY_SETUP.md         # This document
```

---

## 🔗 Related Documentation

- [SecretsManager API Reference](../dev_platform/core/secrets_manager.py)
- [Phase 2D Requirements](../PHASE_2D_REQUIREMENTS.md)
- [Security Architecture](../SECURITY_ARCHITECTURE.md)

---

## ✅ Success Criteria (Phase 2D - Security)

- ✅ No default/hardcoded tokens in code
- ✅ Auto-generated secure tokens on first run
- ✅ Encrypted storage with Fernet
- ✅ CLI tool for token management
- ✅ Key rotation capability
- ✅ Comprehensive documentation
- ✅ No security warnings in logs

---

**Last Updated**: November 15, 2025 (Phase 2D Implementation)
