import threading
import time
from datetime import datetime
from typing import Dict, List
import yaml
from pathlib import Path
from tools.logger import get_logger
from tools.agent_communication import get_communication_system
from tools.notification_system import NotificationSystem


class AIManager:
    def __init__(self):
        self.logger = get_logger('ai_manager')
        self.config = self._load_config()
        self.comm_system = get_communication_system()
        self.notifier = NotificationSystem()
        
        self.agent_name = 'ai_manager'
        self.running = False
        self.agents_status = {}
        self.system_health = {
            'status': 'initializing',
            'uptime_start': datetime.now(),
            'total_alerts': 0,
            'last_check': None
        }
        
        self.comm_system.register_agent(self.agent_name)
        self.logger.info("AI Manager initialized")
    
    def _load_config(self):
        config_path = Path(__file__).parent.parent / 'configs' / 'config.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def start(self):
        self.running = True
        self.system_health['status'] = 'running'
        self.logger.info("AI Manager started")
        
        self.notifier.send_info("🤖 AI Manager started - System operational")
        
        check_interval = self.config.get('agents', {}).get('ai_manager', {}).get('check_interval', 60)
        
        try:
            while self.running:
                self._check_agents()
                self._process_messages()
                self._update_system_health()
                time.sleep(check_interval)
        except KeyboardInterrupt:
            self.logger.info("AI Manager shutting down...")
            self.stop()
    
    def stop(self):
        self.running = False
        self.system_health['status'] = 'stopped'
        self.comm_system.unregister_agent(self.agent_name)
        self.logger.info("AI Manager stopped")
        
    def _check_agents(self):
        agents_config = self.config.get('agents', {})
        
        for agent_type, agent_conf in agents_config.items():
            if agent_type == 'ai_manager':
                continue
            
            if agent_conf.get('enabled', False):
                status = self._get_agent_status(agent_type)
                self.agents_status[agent_type] = status
                
                if not status.get('healthy', True):
                    self._handle_unhealthy_agent(agent_type, status)
        
        self.logger.debug(f"Agent check completed: {len(self.agents_status)} agents monitored")
    
    def _get_agent_status(self, agent_name: str) -> Dict:
        queue_size = self.comm_system.get_queue_size(agent_name)
        
        return {
            'name': agent_name,
            'healthy': True,
            'queue_size': queue_size,
            'last_seen': datetime.now(),
            'status': 'active' if queue_size >= 0 else 'unknown'
        }
    
    def _handle_unhealthy_agent(self, agent_name: str, status: Dict):
        self.logger.warning(f"Unhealthy agent detected: {agent_name}")
        
        auto_restart = self.config.get('agents', {}).get(agent_name, {}).get('auto_restart', False)
        
        if auto_restart:
            self.logger.info(f"Attempting to restart agent: {agent_name}")
            self.comm_system.send_message(
                self.agent_name,
                agent_name,
                'restart',
                {'reason': 'health_check_failed'},
                priority=1
            )
            
            self.notifier.send_warning_alert(
                f"Agent {agent_name} restarted",
                f"Status: {status}"
            )
    
    def _process_messages(self):
        while True:
            message = self.comm_system.receive_message(self.agent_name, timeout=1)
            if message is None:
                break
            
            self.logger.debug(f"Processing message from {message.sender}: {message.message_type}")
            
            if message.message_type == 'alert':
                self._handle_alert(message)
            elif message.message_type == 'status_update':
                self._handle_status_update(message)
            elif message.message_type == 'request':
                self._handle_request(message)
            elif message.message_type == 'action_taken':
                self._handle_action_taken(message)
    
    def _handle_alert(self, message):
        self.system_health['total_alerts'] += 1
        
        alert_level = message.content.get('level', 'info')
        alert_message = message.content.get('message', 'Unknown alert')
        
        self.logger.warning(f"Alert from {message.sender}: {alert_message}")
        
        if alert_level in ['critical', 'error']:
            self.notifier.send_critical_alert(
                f"From {message.sender}",
                alert_message
            )
    
    def _handle_status_update(self, message):
        agent_name = message.sender
        self.agents_status[agent_name] = message.content
        self.logger.debug(f"Status update from {agent_name}")
    
    def _handle_request(self, message):
        request_type = message.content.get('type')
        
        if request_type == 'system_status':
            self._send_system_status(message.sender)
    
    def _handle_action_taken(self, message):
        action = message.content.get('action')
        
        if action == 'ip_blocked':
            ip_address = message.content.get('ip_address')
            username = message.content.get('username', 'غير معروف')
            attempts = message.content.get('attempts')
            timestamp_iso = message.content.get('timestamp')
            location = message.content.get('location', 'غير معروف')
            country_flag = message.content.get('country_flag', '🏴')
            reason = message.content.get('reason', 'غير محدد')
            
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(timestamp_iso)
                formatted_time = dt.strftime('%Y/%m/%d - %I:%M:%S %p')
            except:
                formatted_time = timestamp_iso
            
            self.logger.info(
                f"🛡️ تم حظر IP {ip_address} من قبل {message.sender} | المحاولات: {attempts}"
            )
            
            alert_message = f"""🚨 تم حظر محاولة اختراق تلقائياً

{country_flag} عنوان IP: {ip_address}

📍 الموقع: {location}

👤 المستخدم: {username}

🔐 طريقة المحاولة: كلمة مرور

🕐 التوقيت: {formatted_time}

⚠️ عدد المحاولات: {attempts}

✅ تم حظر IP من الوصول للسيرفر"""
            
            self.notifier.send_telegram(alert_message)
            
            self.logger.debug(f"تم إرسال تنبيه حظر IP {ip_address}")
    
    def _send_system_status(self, recipient: str):
        status = {
            'system_health': self.system_health,
            'agents_status': self.agents_status,
            'timestamp': datetime.now().isoformat()
        }
        
        self.comm_system.send_message(
            self.agent_name,
            recipient,
            'status_response',
            status
        )
    
    def _update_system_health(self):
        self.system_health['last_check'] = datetime.now()
        
        uptime = datetime.now() - self.system_health['uptime_start']
        self.system_health['uptime_seconds'] = int(uptime.total_seconds())
        
        active_agents = sum(1 for status in self.agents_status.values() if status.get('healthy', False))
        self.system_health['active_agents'] = active_agents
        self.system_health['total_agents'] = len(self.agents_status)
    
    def get_system_report(self) -> Dict:
        return {
            'system_health': self.system_health,
            'agents_status': self.agents_status,
            'communication_status': self.comm_system.get_system_status()
        }


if __name__ == "__main__":
    manager = AIManager()
    print("✓ AI Manager initialized successfully")
    print("Starting AI Manager in test mode for 10 seconds...")
    
    threading.Thread(target=manager.start, daemon=True).start()
    time.sleep(10)
    manager.stop()
    
    print("✓ AI Manager test completed")
    report = manager.get_system_report()
    print(f"  System status: {report['system_health']['status']}")
