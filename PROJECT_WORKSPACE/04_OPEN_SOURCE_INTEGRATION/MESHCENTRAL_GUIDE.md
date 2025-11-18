# 🔌 دليل دمج MeshCentral

> **المشروع**: MeshCentral - Remote Management & Monitoring  
> **الموقع**: https://github.com/Ylianst/MeshCentral  
> **الترخيص**: Apache 2.0 (مفتوح المصدر ✅)

**📍 أنت هنا**: `PROJECT_WORKSPACE/04_OPEN_SOURCE_INTEGRATION/MESHCENTRAL_GUIDE.md`  
**🎯 الهدف**: استخراج ودمج مكونات MeshCentral في مشروعنا

---

## 📋 ما نحتاجه من MeshCentral

### ✅ المكونات المطلوبة:

1. **WebSocket Protocol** - للاتصال ثنائي الاتجاه
2. **Agent Installation System** - لتثبيت bridge daemon
3. **Certificate Management** - للأمان
4. **Command Execution Framework** - لتنفيذ الأوامر عن بُعد

### ❌ما لا نحتاجه:

- ❌ الواجهة الكاملة (لدينا Next.js)
- ❌ نظام المستخدمين (لدينا NextAuth)
- ❌ Database layer (لدينا SQLite)

---

## 📁 الملفات المحددة للنسخ

### 1️⃣ WebSocket Protocol

**الملف المصدر**: 
```
MeshCentral/
└── agents/
    └── meshagent.js
```

**ما نستخرج**:
- WebSocket connection logic
- Ping/Pong heartbeat
- Reconnection strategy
- Message serialization

**أين نضعه في مشروعنا**:
```
ServerAutomationAI/bridge_tool/services/websocket_client.py
```

**مثال الكود المستخرج**:
```javascript
// من meshagent.js
function connectWebSocket(url, token) {
  const ws = new WebSocket(url, {
    headers: { Authorization: `Bearer ${token}` }
  });
  
  ws.on('open', () => {
    // Send heartbeat every 30s
    setInterval(() => ws.ping(), 30000);
  });
  
  ws.on('message', (data) => {
    handleCommand(JSON.parse(data));
  });
  
  ws.on('close', () => {
    // Exponential backoff reconnect
    setTimeout(connectWebSocket, backoffTime);
  });
}
```

**نسخة Python للاستخدام**:
```python
# ServerAutomationAI/bridge_tool/services/websocket_client.py
import asyncio
import websockets
import json

class BridgeWebSocket:
    def __init__(self, url, token):
        self.url = url
        self.token = token
        self.ws = None
        
    async def connect(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        self.ws = await websockets.connect(
            self.url, 
            extra_headers=headers
        )
        
        # Start heartbeat
        asyncio.create_task(self._heartbeat())
        
        # Listen for messages
        await self._listen()
    
    async def _heartbeat(self):
        while True:
            await asyncio.sleep(30)
            await self.ws.ping()
    
    async def _listen(self):
        async for message in self.ws:
            data = json.loads(message)
            await self._handle_command(data)
```

---

### 2️⃣ Agent Installation

**الملف المصدر**:
```
MeshCentral/
└── agents/
    └── installer.sh
```

**ما نستخرج**:
- Auto-download script
- Service installation
- Auto-start configuration
- Update mechanism

**أين نضعه**:
```
ServerAutomationAI/bridge_tool/installers/install.sh
```

**الكود المكيّف**:
```bash
#!/bin/bash
# المصدر: MeshCentral installer.sh (modified)

PLATFORM_URL="https://your-platform.com"
TOKEN="$1"

# تحميل Bridge Daemon
curl -o /tmp/bridge-daemon "${PLATFORM_URL}/downloads/bridge-daemon"
chmod +x /tmp/bridge-daemon

# تثبيت كـ systemd service
cat > /etc/systemd/system/bridge-daemon.service << EOF
[Unit]
Description=Platform Bridge Daemon
After=network.target

[Service]
Type=simple
ExecStart=/opt/platform/bridge-daemon --token ${TOKEN}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# تفعيل الخدمة
systemctl enable bridge-daemon
systemctl start bridge-daemon

echo "✅ Bridge Daemon installed successfully!"
```

---

### 3️⃣ Certificate Management

**الملف المصدر**:
```
MeshCentral/
└── certoperations.js
```

**ما نستخرج**:
- Self-signed cert generation
- Cert validation
- TLS configuration

**أين نضعه**:
```
ServerAutomationAI/bridge_tool/services/cert_manager.py
```

**مثال**:
```python
# من MeshCentral certoperations.js
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa

class CertManager:
    @staticmethod
    def generate_self_signed_cert(hostname):
        """Generate self-signed certificate for bridge daemon"""
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        # Create certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(x509.NameOID.COMMON_NAME, hostname)
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)
        ).sign(private_key, hashes.SHA256())
        
        return cert, private_key
```

---

### 4️⃣ Command Execution

**الملف المصدر**:
```
MeshCentral/
└── agents/
    └── modules/
        └── command-handler.js
```

**ما نستخرج**:
- Command queue system
- Response handling
- Error recovery

**أين نضعه**:
```
ServerAutomationAI/dev_platform/tools/remote_executor.py
```

**مثال الدمج**:
```python
# مستوحى من MeshCentral command-handler.js
import asyncio
from typing import Dict, Callable

class RemoteCommandExecutor:
    def __init__(self):
        self.handlers: Dict[str, Callable] = {}
        self.queue = asyncio.Queue()
    
    def register_handler(self, command_type: str, handler: Callable):
        """Register command handler (pattern من MeshCentral)"""
        self.handlers[command_type] = handler
    
    async def execute(self, command: dict):
        """Execute command with response handling"""
        cmd_type = command.get("type")
        handler = self.handlers.get(cmd_type)
        
        if not handler:
            return {"error": f"Unknown command: {cmd_type}"}
        
        try:
            result = await handler(command.get("payload"))
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
```

---

## 🔧 خطوات التكامل

### الخطوة 1: نسخ الملفات الأساسية

```bash
# Clone MeshCentral
git clone https://github.com/Ylianst/MeshCentral.git /tmp/meshcentral

# نسخ الملفات المطلوبة
cp /tmp/meshcentral/agents/meshagent.js \
   ServerAutomationAI/bridge_tool/reference/meshagent.js

cp /tmp/meshcentral/agents/installer.sh \
   ServerAutomationAI/bridge_tool/installers/base_installer.sh

cp /tmp/meshcentral/certoperations.js \
   ServerAutomationAI/bridge_tool/reference/certoperations.js
```

### الخطوة 2: تكييف الكود

1. **تحويل JavaScript إلى Python** (للأجزاء المطلوبة)
2. **إزالة التبعيات غير الضرورية**
3. **التكامل مع الأنظمة الموجودة**

### الخطوة 3: الاختبار

```python
# test_meshcentral_integration.py
import pytest
from bridge_tool.services.websocket_client import BridgeWebSocket

async def test_websocket_connection():
    ws = BridgeWebSocket("ws://localhost:8080", "test-token")
    await ws.connect()
    assert ws.ws is not None
```

---

## 📊 التعديلات المطلوبة

| المكون الأصلي | التعديل المطلوب | السبب |
|---------------|------------------|-------|
| WebSocket Server | استخدام websockets lib | Python vs Node.js |
| Certificate Store | استخدام cryptography lib | Python standard |
| Installer Script | تبسيط + إزالة UI parts | لا نحتاج Web UI |
| Command Protocol | دمج مع code_executor.py | نظامنا الموجود |

---

## 🎯 معايير القبول

- [ ] WebSocket connection يعمل بنجاح
- [ ] Heartbeat و Reconnect يعملان
- [ ] Installer script يثبت bridge daemon
- [ ] Certificate management يعمل
- [ ] Command execution متكامل مع النظام الموجود

---

## 🔗 الروابط ذات الصلة

- **المشروع الأصلي**: https://github.com/Ylianst/MeshCentral
- **التوثيق**: https://meshcentral.com/info/
- **أمثلة**: https://github.com/Ylianst/MeshCentral/tree/master/agents

**المطور المسؤول**: Developer 9 (Bridge Integration)  
**الوثائق المتعلقة**: `05_OPERATIONS/AGENT_TASKS/DEVELOPER_09.md`

---

**آخر تحديث**: 2025-11-18  
**الحالة**: ✅ جاهز للتنفيذ
