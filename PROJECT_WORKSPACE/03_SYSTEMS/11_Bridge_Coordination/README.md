# 🌉 Bridge Coordination System

## نظرة عامة

**Bridge Coordination** هو النظام الذي يربط بين **Control Plane** (المنصة) و **VPS المستخدم** - يعمل كجسر اتصال ثنائي الاتجاه لتنفيذ الأوامر ونقل البيانات.

---

## المكونات

### 1. Bridge Daemon (على VPS المستخدم)
```yaml
التقنية: Python/Node.js + WebSocket
المسؤولية: البرنامج الذي يعمل على سيرفر المستخدم
```

**المسؤوليات:**
- الاتصال الدائم مع Control Plane عبر WebSocket
- استقبال الأوامر من المنصة وتنفيذها
- جمع telemetry وإرسالها للمنصة
- إدارة دورة حياة AI Agents
- تنفيذ عمليات Git (pull, push, status)
- File synchronization
- Build & Test execution

### 2. Control Plane Bridge API (على المنصة)
```yaml
التقنية: WebSocket Server
المسؤولية: استقبال الاتصالات من Bridge Daemons
```

**المسؤوليات:**
- إدارة اتصالات WebSocket النشطة
- توجيه الأوامر للـ Bridge المناسب
- استقبال telemetry من جميع السيرفرات
- Health check للسيرفرات المتصلة
- Queue management للمهام

### 3. Command Executor
```yaml
المسؤولية: تنفيذ الأوامر على السيرفر
```

**أنواع الأوامر:**
- **Git Commands**: `git pull`, `git push`, `git status`
- **File Operations**: `create`, `read`, `update`, `delete`
- **Build Commands**: `npm install`, `npm build`
- **Test Commands**: `npm test`, `pytest`
- **Agent Commands**: `start_agent`, `stop_agent`, `agent_status`
- **System Commands**: `reboot`, `update`, `cleanup`

### 4. Security Layer
```yaml
المسؤولية: تأمين الاتصال والأوامر
```

**الميزات:**
- Token-based authentication
- Short-lived tokens (تنتهي بعد ساعات)
- Command validation (whitelist)
- Rate limiting
- Encryption (TLS/SSL)

### 5. Telemetry Collector
```yaml
المسؤولية: جمع بيانات المراقبة
```

**البيانات المجموعة:**
- Server metrics (CPU, RAM, Disk, Network)
- Agent status
- Build/Test results
- Error logs
- Performance metrics

---

## البنية المعمارية

```
┌─────────────────────────────────────────────────────────┐
│              Control Plane (المنصة)                     │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │       Bridge API (WebSocket Server)               │ │
│  │  • Accepts connections from Bridge Daemons        │ │
│  │  • Routes commands to appropriate bridge          │ │
│  │  • Collects telemetry from all servers            │ │
│  └────────────┬──────────────────────────────────────┘ │
│               │                                         │
└───────────────┼─────────────────────────────────────────┘
                │
                │ WebSocket (wss://)
                │ (Secure bidirectional channel)
                │
    ┌───────────┼───────────┬───────────┐
    │           │           │           │
    ↓           ↓           ↓           ↓
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│ VPS 1   │ │ VPS 2   │ │ VPS 3   │ │ VPS N   │
│         │ │         │ │         │ │         │
│ ┌─────────────────────────────────────────┐ │
│ │       Bridge Daemon Process             │ │
│ │                                         │ │
│ │  ┌─────────────────────────────────┐   │ │
│ │  │  WebSocket Client               │   │ │
│ │  │  → Maintains connection         │   │ │
│ │  │  → Handles reconnection         │   │ │
│ │  └─────────────────────────────────┘   │ │
│ │                                         │ │
│ │  ┌─────────────────────────────────┐   │ │
│ │  │  Command Executor               │   │ │
│ │  │  → Git, Files, Build, Test      │   │ │
│ │  └─────────────────────────────────┘   │ │
│ │                                         │ │
│ │  ┌─────────────────────────────────┐   │ │
│ │  │  Telemetry Collector            │   │ │
│ │  │  → CPU, RAM, Disk, Logs         │   │ │
│ │  └─────────────────────────────────┘   │ │
│ │                                         │ │
│ │  ┌─────────────────────────────────┐   │ │
│ │  │  Security & Auth                │   │ │
│ │  │  → Token validation             │   │ │
│ │  └─────────────────────────────────┘   │ │
│ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

---

## التكامل مع الأنظمة الأخرى

### مع Control Plane:
```typescript
// إرسال أمر من Dashboard للـ Bridge
import { useBridge } from '@/hooks/useBridge'

const { sendCommand, isConnected } = useBridge(serverId)

const deployProject = async () => {
  const result = await sendCommand({
    type: 'git:push',
    params: { branch: 'main' }
  })
  
  if (result.success) {
    console.log('Deployed successfully')
  }
}
```

### مع Monitoring System:
```typescript
// استقبال telemetry من Bridge
socket.on('telemetry', (data) => {
  updateServerMetrics(data.serverId, {
    cpu: data.cpu,
    memory: data.memory,
    disk: data.disk,
    timestamp: data.timestamp
  })
})
```

### مع AI Agents:
```typescript
// تفويض مهمة لوكيل على VPS
const delegateToAgent = async (agentId: string, task: string) => {
  const result = await sendCommand({
    type: 'agent:execute',
    params: {
      agent: agentId,
      task: task,
      context: getCurrentContext()
    }
  })
  
  return result
}
```

---

## المهام ذات الصلة

- المطور 3: Infrastructure Setup (تثبيت Bridge على السيرفرات)
- المطور 10: Server Monitoring (استقبال telemetry)
- المطور 1-2: AI Agents (تنفيذ مهام الوكلاء)

---

## الحالة الحالية

**ما هو موجود:**
- ❌ لا شيء بعد - يجب بناء كل شيء من الصفر

**ما يجب إضافته:**
- [ ] Bridge Daemon (Python/Node.js)
- [ ] WebSocket Client (في Bridge Daemon)
- [ ] WebSocket Server (في Control Plane)
- [ ] Command Executor
- [ ] Telemetry Collector
- [ ] Security & Authentication
- [ ] Installation script
- [ ] Reconnection logic
- [ ] Queue management
- [ ] Error handling & logging

---

## التوسعة المطلوبة

### مثال: Bridge Daemon (Python)

```python
# bridge_daemon.py

import asyncio
import websockets
import json
import subprocess
import psutil
from typing import Dict, Any

class BridgeDaemon:
    def __init__(self, platform_url: str, token: str):
        self.platform_url = platform_url
        self.token = token
        self.ws = None
        self.running = True
        
    async def connect(self):
        """Connect to Control Plane"""
        headers = {'Authorization': f'Bearer {self.token}'}
        
        while self.running:
            try:
                async with websockets.connect(
                    self.platform_url,
                    extra_headers=headers
                ) as ws:
                    self.ws = ws
                    print("✅ Connected to Control Plane")
                    
                    # Start telemetry loop
                    asyncio.create_task(self.send_telemetry())
                    
                    # Listen for commands
                    await self.listen_commands()
                    
            except Exception as e:
                print(f"❌ Connection failed: {e}")
                await asyncio.sleep(5)  # Retry after 5 seconds
    
    async def listen_commands(self):
        """Listen for commands from Control Plane"""
        async for message in self.ws:
            data = json.loads(message)
            result = await self.execute_command(data)
            await self.ws.send(json.dumps(result))
    
    async def execute_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Execute received command"""
        cmd_type = command['type']
        params = command.get('params', {})
        
        try:
            if cmd_type == 'git:pull':
                return await self.git_pull(params)
            elif cmd_type == 'build':
                return await self.run_build(params)
            elif cmd_type == 'test':
                return await self.run_tests(params)
            elif cmd_type == 'agent:execute':
                return await self.run_agent(params)
            else:
                return {'success': False, 'error': f'Unknown command: {cmd_type}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def git_pull(self, params: Dict) -> Dict:
        """Execute git pull"""
        result = subprocess.run(
            ['git', 'pull'],
            cwd=params.get('repo_path', '.'),
            capture_output=True,
            text=True
        )
        
        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr
        }
    
    async def run_build(self, params: Dict) -> Dict:
        """Run build command"""
        cmd = params.get('command', 'npm run build')
        result = subprocess.run(
            cmd.split(),
            cwd=params.get('cwd', '.'),
            capture_output=True,
            text=True
        )
        
        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr
        }
    
    async def send_telemetry(self):
        """Send server metrics periodically"""
        while self.running:
            try:
                metrics = {
                    'type': 'telemetry',
                    'data': {
                        'cpu': psutil.cpu_percent(interval=1),
                        'memory': psutil.virtual_memory().percent,
                        'disk': psutil.disk_usage('/').percent,
                        'timestamp': int(time.time())
                    }
                }
                
                await self.ws.send(json.dumps(metrics))
                await asyncio.sleep(30)  # Send every 30 seconds
                
            except Exception as e:
                print(f"Error sending telemetry: {e}")
                break

# Run daemon
if __name__ == '__main__':
    daemon = BridgeDaemon(
        platform_url='wss://platform.example.com/bridge',
        token='your-auth-token'
    )
    
    asyncio.run(daemon.connect())
```

### مثال: Bridge API (Control Plane)

```typescript
// api/bridge/route.ts (Next.js API Route)

import { WebSocketServer } from 'ws'
import { verifyToken } from '@/lib/auth'

const wss = new WebSocketServer({ noServer: true })

// Store active connections
const connections = new Map<string, WebSocket>()

wss.on('connection', async (ws, request) => {
  // Verify authentication
  const token = request.headers['authorization']?.replace('Bearer ', '')
  const user = await verifyToken(token)
  
  if (!user) {
    ws.close(1008, 'Unauthorized')
    return
  }
  
  // Get server ID from user
  const serverId = user.serverId
  connections.set(serverId, ws)
  
  console.log(`✅ Server ${serverId} connected`)
  
  // Handle messages from bridge
  ws.on('message', (data) => {
    const message = JSON.parse(data.toString())
    
    if (message.type === 'telemetry') {
      // Store telemetry in database
      storeTelemetry(serverId, message.data)
    } else {
      // Handle command response
      handleCommandResponse(serverId, message)
    }
  })
  
  // Handle disconnection
  ws.on('close', () => {
    connections.delete(serverId)
    console.log(`❌ Server ${serverId} disconnected`)
  })
})

// Send command to specific server
export async function sendCommand(serverId: string, command: any) {
  const ws = connections.get(serverId)
  
  if (!ws) {
    throw new Error('Server not connected')
  }
  
  return new Promise((resolve, reject) => {
    // Send command
    ws.send(JSON.stringify(command))
    
    // Wait for response (with timeout)
    const timeout = setTimeout(() => {
      reject(new Error('Command timeout'))
    }, 30000)
    
    ws.once('message', (data) => {
      clearTimeout(timeout)
      resolve(JSON.parse(data.toString()))
    })
  })
}
```

### مثال: Installation Script

```bash
#!/bin/bash
# install-bridge.sh

set -e

echo "🌉 Installing Bridge Daemon..."

# Variables
PLATFORM_URL="wss://platform.example.com/bridge"
INSTALL_DIR="/opt/bridge-daemon"

# Create directory
sudo mkdir -p $INSTALL_DIR
cd $INSTALL_DIR

# Download daemon
echo "📥 Downloading daemon..."
curl -sSL https://platform.example.com/downloads/bridge-daemon.tar.gz | tar xz

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Configure
echo "⚙️ Configuring..."
read -p "Enter your platform token: " TOKEN
cat > config.json <<EOF
{
  "platform_url": "$PLATFORM_URL",
  "token": "$TOKEN"
}
EOF

# Create systemd service
echo "🔧 Creating service..."
sudo cat > /etc/systemd/system/bridge-daemon.service <<EOF
[Unit]
Description=Bridge Daemon
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 bridge_daemon.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start service
echo "🚀 Starting service..."
sudo systemctl daemon-reload
sudo systemctl enable bridge-daemon
sudo systemctl start bridge-daemon

echo "✅ Bridge Daemon installed and running!"
echo "Check status: sudo systemctl status bridge-daemon"
```

---

## التحديات التقنية

### 1. Connection Reliability
```python
# حل: Auto-reconnection مع exponential backoff
async def connect_with_retry(self):
    retry_delay = 1
    max_delay = 60
    
    while self.running:
        try:
            await self.connect()
        except Exception as e:
            print(f"Retry in {retry_delay}s...")
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, max_delay)
```

### 2. Command Timeout
```typescript
// حل: Timeout wrapper
const withTimeout = (promise, ms) => {
  return Promise.race([
    promise,
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Timeout')), ms)
    )
  ])
}
```

### 3. Security
```python
# حل: Command whitelist
ALLOWED_COMMANDS = [
    'git:pull', 'git:push', 'git:status',
    'build', 'test',
    'agent:execute', 'agent:status'
]

def validate_command(cmd_type):
    if cmd_type not in ALLOWED_COMMANDS:
        raise SecurityError(f'Command not allowed: {cmd_type}')
```

---

## الوثائق ذات الصلة

- [`../01_ARCHITECTURE/SYSTEM_OVERVIEW.md`](../../01_ARCHITECTURE/SYSTEM_OVERVIEW.md)
- [`../03_SYSTEMS/10_Monitoring_Alerting/README.md`](../10_Monitoring_Alerting/README.md)
- [`../02_INTEGRATION_PLAN/MERGE_STRATEGY.md`](../../02_INTEGRATION_PLAN/MERGE_STRATEGY.md)

---

**آخر تحديث**: 2025-11-18  
**الحالة**: ✅ موثق
