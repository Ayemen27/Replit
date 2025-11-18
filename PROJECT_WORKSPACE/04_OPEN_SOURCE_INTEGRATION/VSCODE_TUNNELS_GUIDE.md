# 🚇 دليل دمج VSCode Remote Tunnels

> **المشروع**: VSCode Remote Development  
> **الموقع**: https://github.com/microsoft/vscode-remote-release  
> **الترخيص**: MIT (مفتوح المصدر ✅)

**📍 أنت هنا**: `PROJECT_WORKSPACE/04_OPEN_SOURCE_INTEGRATION/VSCODE_TUNNELS_GUIDE.md`  
**🎯 الهدف**: استخراج ودمج تقنية Reverse Tunneling

---

## 📋 ما نحتاجه من VSCode Tunnels

### ✅ المكونات المطلوبة:

1. **Reverse Tunnel Implementation** - للاتصال من خلف Firewalls
2. **Secure Connection Patterns** - للأمان
3. **Session Management** - لإدارة الجلسات
4. **Port Forwarding** - لتوجيه المنافذ

---

## 🔍 كيف يعمل VSCode Tunnels

### البنية الأساسية:

```
User VPS (خلف Firewall)
    ↓ Reverse Connection
Cloud Relay Server (Microsoft/Custom)
    ↓ Forward Connection
Platform Control Plane
```

### المبدأ:
- VPS يفتح اتصال **خارج** (outbound) بدلاً من الانتظار للوارد
- لا يحتاج فتح منافذ في Firewall
- الأمان: certificate-based authentication

---

## 📁 المكونات للاستخراج

### 1️⃣ Reverse Tunnel Server

**الوظيفة**: سيرفر relay يستقبل الاتصالات

**التطبيق في مشروعنا**:
```
ServerAutomationAI/bridge_tool/services/tunnel_server.py
```

**الكود المكيّف**:
```python
import asyncio
import websockets
from typing import Dict, Set

class TunnelRelayServer:
    """Reverse tunnel server - مستوحى من VSCode"""
    
    def __init__(self, host='0.0.0.0', port=8443):
        self.host = host
        self.port = port
        self.agents: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.control_planes: Set[websockets.WebSocketServerProtocol] = set()
    
    async def start(self):
        """Start tunnel relay server"""
        async with websockets.serve(
            self.handle_connection,
            self.host,
            self.port,
            ssl=self._create_ssl_context()
        ):
            await asyncio.Future()  # run forever
    
    async def handle_connection(self, websocket, path):
        """Handle incoming connection (agent or control plane)"""
        try:
            # تعريف نوع الاتصال
            handshake = await websocket.recv()
            data = json.loads(handshake)
            
            if data['type'] == 'agent':
                agent_id = data['agent_id']
                self.agents[agent_id] = websocket
                await self._handle_agent(agent_id, websocket)
            
            elif data['type'] == 'control_plane':
                self.control_planes.add(websocket)
                await self._handle_control_plane(websocket)
        
        finally:
            # Cleanup on disconnect
            if websocket in self.control_planes:
                self.control_planes.remove(websocket)
    
    async def _handle_agent(self, agent_id: str, websocket):
        """Handle agent connection"""
        try:
            async for message in websocket:
                # إرسال رسالة Agent إلى Control Plane
                await self._forward_to_control_plane(agent_id, message)
        except Exception as e:
            print(f"Agent {agent_id} disconnected: {e}")
            del self.agents[agent_id]
    
    async def _handle_control_plane(self, websocket):
        """Handle control plane connection"""
        try:
            async for message in websocket:
                data = json.loads(message)
                target_agent = data.get('target_agent_id')
                
                # إرسال أمر إلى Agent المحدد
                if target_agent in self.agents:
                    await self.agents[target_agent].send(message)
        except Exception as e:
            print(f"Control plane disconnected: {e}")
    
    async def _forward_to_control_plane(self, agent_id: str, message: str):
        """Forward agent message to all control planes"""
        dead_connections = set()
        
        for cp in self.control_planes:
            try:
                wrapped = json.dumps({
                    'source_agent_id': agent_id,
                    'payload': message
                })
                await cp.send(wrapped)
            except:
                dead_connections.add(cp)
        
        # تنظيف الاتصالات الميتة
        self.control_planes -= dead_connections
```

---

### 2️⃣ Reverse Tunnel Client (Agent-side)

**الوظيفة**: يعمل على VPS المستخدم، يفتح اتصال إلى Relay

**التطبيق في مشروعنا**:
```
ServerAutomationAI/bridge_tool/daemon/tunnel_client.py
```

**الكود**:
```python
import asyncio
import websockets
import json

class TunnelClient:
    """Reverse tunnel client - يعمل على VPS المستخدم"""
    
    def __init__(self, relay_url: str, agent_id: str, token: str):
        self.relay_url = relay_url
        self.agent_id = agent_id
        self.token = token
        self.ws = None
    
    async def connect(self):
        """Connect to relay server"""
        while True:
            try:
                self.ws = await websockets.connect(
                    self.relay_url,
                    ssl=True,
                    extra_headers={'Authorization': f'Bearer {self.token}'}
                )
                
                # Handshake
                await self.ws.send(json.dumps({
                    'type': 'agent',
                    'agent_id': self.agent_id,
                    'token': self.token
                }))
                
                print(f"✅ Connected to relay as {self.agent_id}")
                
                # استقبال الأوامر
                await self._listen_for_commands()
            
            except Exception as e:
                print(f"❌ Connection failed: {e}")
                await asyncio.sleep(10)  # retry بعد 10 ثواني
    
    async def _listen_for_commands(self):
        """Listen for commands from control plane"""
        try:
            async for message in self.ws:
                await self._execute_command(message)
        except Exception as e:
            print(f"Connection lost: {e}")
    
    async def _execute_command(self, message: str):
        """Execute command and send response"""
        try:
            command = json.loads(message)
            cmd_type = command.get('type')
            
            if cmd_type == 'exec':
                # تنفيذ أمر bash
                result = await self._run_command(command['payload'])
                await self.ws.send(json.dumps({
                    'type': 'result',
                    'success': True,
                    'output': result
                }))
            
            elif cmd_type == 'ping':
                await self.ws.send(json.dumps({'type': 'pong'}))
        
        except Exception as e:
            await self.ws.send(json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    async def _run_command(self, cmd: str) -> str:
        """Run bash command"""
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        return stdout.decode() + stderr.decode()
```

---

### 3️⃣ Port Forwarding

**الوظيفة**: توجيه منفذ محلي من VPS إلى Control Plane

**التطبيق**:
```python
class PortForwarder:
    """Forward local ports through tunnel - مثل VSCode port forwarding"""
    
    def __init__(self, tunnel_client: TunnelClient):
        self.tunnel = tunnel_client
        self.forwarded_ports: Dict[int, asyncio.Server] = {}
    
    async def forward_port(self, local_port: int, remote_port: int):
        """Forward local_port on VPS to remote_port on control plane"""
        
        async def handle_connection(reader, writer):
            # عند اتصال محلي، أرسل البيانات عبر Tunnel
            try:
                while True:
                    data = await reader.read(4096)
                    if not data:
                        break
                    
                    # إرسال البيانات عبر WebSocket
                    await self.tunnel.ws.send(json.dumps({
                        'type': 'port_forward',
                        'port': remote_port,
                        'data': data.hex()  # hex encoding للبيانات الثنائية
                    }))
                    
                    # استقبال الرد
                    response = await self.tunnel.ws.recv()
                    writer.write(bytes.fromhex(json.loads(response)['data']))
            
            finally:
                writer.close()
        
        server = await asyncio.start_server(
            handle_connection,
            '127.0.0.1',
            local_port
        )
        
        self.forwarded_ports[local_port] = server
        print(f"✅ Forwarding {local_port} → {remote_port}")
```

---

## 🔧 خطوات التكامل

### 1. نشر Tunnel Relay Server

```bash
# على Platform Server (Control Plane)
cd ServerAutomationAI/bridge_tool/services
python3 tunnel_server.py --host 0.0.0.0 --port 8443
```

### 2. تثبيت Tunnel Client على VPS

```bash
# على VPS المستخدم
curl https://platform.com/downloads/tunnel-client.py -o tunnel_client.py

# تشغيل
python3 tunnel_client.py \
  --relay wss://platform.com:8443 \
  --agent-id user123_vps \
  --token abc123xyz
```

### 3. Port Forwarding (مثال)

```python
# في كود التطبيق
forwarder = PortForwarder(tunnel_client)

# توجيه منفذ 3000 (Next.js dev server على VPS)
# إلى منفذ 4000 (على Control Plane)
await forwarder.forward_port(local_port=3000, remote_port=4000)

# الآن يمكن للمستخدم الوصول إلى Next.js من المتصفح:
# http://platform.com:4000
```

---

## 🎯 معايير القبول

- [ ] Tunnel Relay Server يعمل ويقبل الاتصالات
- [ ] Tunnel Client يتصل بنجاح من خلف Firewall
- [ ] Reconnect تلقائي عند انقطاع الاتصال
- [ ] Port Forwarding يعمل للمنافذ المحددة
- [ ] Authentication آمن (token-based)
- [ ] TLS/SSL enabled

---

## 🔗 الروابط ذات الصلة

- **المشروع الأصلي**: https://github.com/microsoft/vscode-remote-release
- **التوثيق**: https://code.visualstudio.com/docs/remote/tunnels
- **Architecture**: https://code.visualstudio.com/api/advanced-topics/remote-extensions

**المطور المسؤول**: Developer 9 (Bridge Integration)  
**الوثائق المتعلقة**: `05_OPERATIONS/AGENT_TASKS/DEVELOPER_09.md`

---

**آخر تحديث**: 2025-11-18  
**الحالة**: ✅ جاهز للتنفيذ
