# دليل ربط السيرفرات (Server Linking Guide)

## 1. نظرة عامة

هذا الدليل يشرح كيفية ربط VPS الخاص بالمستخدم بالمنصة.

---

## 2. المتطلبات (Prerequisites)

### VPS Requirements
```yaml
os: Linux (Ubuntu 20.04+ / Debian 11+ / CentOS 8+)
ram: >= 1GB
disk: >= 10GB
network: اتصال إنترنت مستقر
ports: 443 (HTTPS), 22 (SSH)
```

### Software Requirements
```bash
# Python 3.9+
python3 --version

# Docker (اختياري، للحاويات)
docker --version

# systemd (لإدارة الخدمات)
systemctl --version
```

---

## 3. خطوات الربط (Linking Steps)

### الخطوة 1: إنشاء رمز الربط (Link Token)

في Dashboard:
```
1. اذهب إلى "Servers" → "Link New Server"
2. أدخل اسم السيرفر (اختياري)
3. اضغط "Generate Token"
4. انسخ الأمر الذي يظهر
```

سيظهر لك أمر مثل:
```bash
curl -fsSL https://platform.com/bridge/install.sh | \
  sudo bash -s -- --token "YOUR_UNIQUE_TOKEN"
```

---

### الخطوة 2: تشغيل أمر التثبيت

على VPS الخاص بك:
```bash
# نسخ الأمر من Dashboard وتشغيله
curl -fsSL https://platform.com/bridge/install.sh | \
  sudo bash -s -- --token "YOUR_TOKEN"
```

**ما يحدث خلف الكواليس**:
1. تحميل Bridge Daemon
2. إنشاء مستخدم `bridge-agent`
3. تثبيت Dependencies
4. إعداد systemd service
5. تفعيل الخدمة وتشغيلها
6. اختبار الاتصال

---

### الخطوة 3: التحقق من الاتصال

```bash
# تحقق من حالة الخدمة
sudo systemctl status bridge-daemon

# Expected output:
# ● bridge-daemon.service - Bridge Daemon for Platform
#    Active: active (running) since ...
#    ...

# تحقق من السجلات
sudo journalctl -u bridge-daemon -f

# Expected output:
# [INFO] Connected to platform successfully
# [INFO] Heartbeat sent: OK
```

في Dashboard:
```
- اذهب إلى "Servers"
- يجب أن ترى السيرفر بحالة "Active" ✅
```

---

## 4. ما يتم تثبيته (What Gets Installed)

### الملفات
```bash
/opt/bridge-daemon/
├── daemon.py           # Bridge Daemon رئيسي
├── config.yaml         # إعدادات
├── requirements.txt    # Python dependencies
└── logs/              # السجلات

/etc/systemd/system/
└── bridge-daemon.service  # Systemd service file

/home/bridge-agent/
└── ...                # مجلد المستخدم bridge-agent
```

### Systemd Service
```ini
[Unit]
Description=Bridge Daemon for Platform
After=network.target

[Service]
Type=simple
User=bridge-agent
WorkingDirectory=/opt/bridge-daemon
ExecStart=/usr/bin/python3 daemon.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## 5. الأمان (Security)

### الصلاحيات
```yaml
bridge-agent user:
  uid: 1500
  groups: [docker]  # اختياري
  shell: /bin/bash
  home: /home/bridge-agent
  
permissions:
  - read: project files
  - write: project files
  - execute: whitelisted commands only
  - no: root access
```

### الأوامر المسموحة (Command Whitelist)
```yaml
allowed:
  - docker ps
  - docker logs <container>
  - systemctl status <service>
  - git pull
  - npm install
  - python manage.py migrate
  
blocked:
  - rm -rf /
  - dd if=/dev/zero
  - shutdown
  - reboot
  - chmod 777
```

### الاتصال
```yaml
protocol: WSS (WebSocket Secure)
encryption: TLS 1.3
authentication: JWT token (rotated monthly)
heartbeat: every 30 seconds
```

---

## 6. إدارة Bridge Daemon

### إيقاف الخدمة
```bash
sudo systemctl stop bridge-daemon
```

### إعادة تشغيل الخدمة
```bash
sudo systemctl restart bridge-daemon
```

### تعطيل auto-start
```bash
sudo systemctl disable bridge-daemon
```

### إزالة التثبيت الكامل
```bash
# إيقاف وحذف الخدمة
sudo systemctl stop bridge-daemon
sudo systemctl disable bridge-daemon
sudo rm /etc/systemd/system/bridge-daemon.service

# حذف الملفات
sudo rm -rf /opt/bridge-daemon

# حذف المستخدم (اختياري)
sudo userdel -r bridge-agent
```

---

## 7. استكشاف الأخطاء (Troubleshooting)

### المشكلة: الاتصال فاشل

```bash
# 1. تحقق من حالة الخدمة
sudo systemctl status bridge-daemon

# 2. تحقق من السجلات
sudo journalctl -u bridge-daemon -n 50

# 3. تحقق من الاتصال بالمنصة
curl -I https://platform.com/health

# 4. تحقق من Firewall
sudo ufw status
# تأكد أن port 443 مفتوح للخارج
```

### المشكلة: Permission Denied

```bash
# تحقق من صلاحيات المستخدم
sudo -u bridge-agent whoami
sudo -u bridge-agent ls -la /opt/bridge-daemon

# إصلاح الصلاحيات
sudo chown -R bridge-agent:bridge-agent /opt/bridge-daemon
sudo chmod 755 /opt/bridge-daemon
```

### المشكلة: Token Invalid

```
1. في Dashboard → "Servers" → اختر السيرفر
2. اضغط "Regenerate Token"
3. نسخ الأمر الجديد
4. على VPS:
   sudo /opt/bridge-daemon/update-token.sh "NEW_TOKEN"
   sudo systemctl restart bridge-daemon
```

---

## 8. الترقية (Upgrading)

### تحديث Bridge Daemon
```bash
# التحديث التلقائي (recommended)
# يحدث كل أسبوع تلقائياً

# التحديث اليدوي
curl -fsSL https://platform.com/bridge/update.sh | sudo bash
sudo systemctl restart bridge-daemon
```

---

## 9. الأسئلة الشائعة (FAQ)

**س: هل يمكنني ربط أكثر من VPS؟**  
ج: نعم! كل VPS يحتاج token منفصل.

**س: هل يؤثر Bridge Daemon على أداء السيرفر؟**  
ج: لا، الاستهلاك أقل من 50MB RAM و < 1% CPU.

**س: ماذا لو انقطع الاتصال؟**  
ج: Bridge Daemon يعيد الاتصال تلقائياً خلال 10 ثواني.

**س: هل يمكن استخدامه مع Shared Hosting؟**  
ج: لا، يتطلب VPS/Dedicated server مع صلاحيات root.

---

## 10. الوثائق ذات الصلة

- [BRIDGE_TOOL.md](./BRIDGE_TOOL.md) - تفاصيل تقنية عن Bridge
- [03_SYSTEMS/02_Remote_Execution/](../03_SYSTEMS/02_Remote_Execution/) - نظام التنفيذ عن بُعد
- [04_SECURITY/SECURITY_POLICY.md](../04_SECURITY/SECURITY_POLICY.md) - سياسات الأمان

---

**للدعم**:
- Email: support@platform.com
- Discord: [رابط]
- Docs: https://docs.platform.com

**آخر تحديث**: 2025-11-18
