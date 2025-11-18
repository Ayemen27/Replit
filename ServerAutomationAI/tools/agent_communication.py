import queue
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional
import json
from tools.logger import get_logger


class Message:
    def __init__(self, sender: str, recipient: str, message_type: str, content: Any, priority: int = 5):
        self.id = f"{sender}_{datetime.now().timestamp()}"
        self.sender = sender
        self.recipient = recipient
        self.message_type = message_type
        self.content = content
        self.priority = priority
        self.timestamp = datetime.now()
        self.status = 'pending'
    
    def to_dict(self):
        return {
            'id': self.id,
            'sender': self.sender,
            'recipient': self.recipient,
            'message_type': self.message_type,
            'content': self.content,
            'priority': self.priority,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status
        }
    
    def __lt__(self, other):
        return self.priority < other.priority


class AgentCommunication:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentCommunication, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.logger = get_logger('agent_communication')
        self.message_queues: Dict[str, queue.PriorityQueue] = {}
        self.agents: Dict[str, bool] = {}
        self.message_history = []
        self.max_history = 1000
        self.lock = threading.Lock()
        
        self.logger.info("Agent Communication System initialized")
    
    def register_agent(self, agent_name: str):
        with self.lock:
            if agent_name not in self.message_queues:
                self.message_queues[agent_name] = queue.PriorityQueue(maxsize=1000)
                self.agents[agent_name] = True
                self.logger.info(f"Agent registered: {agent_name}")
                return True
            return False
    
    def unregister_agent(self, agent_name: str):
        with self.lock:
            if agent_name in self.agents:
                self.agents[agent_name] = False
                self.logger.info(f"Agent unregistered: {agent_name}")
                return True
            return False
    
    def send_message(self, sender: str, recipient: str, message_type: str, content: Any, priority: int = 5) -> bool:
        try:
            if recipient not in self.message_queues:
                self.logger.warning(f"Recipient agent '{recipient}' not registered")
                return False
            
            message = Message(sender, recipient, message_type, content, priority)
            
            self.message_queues[recipient].put((priority, message))
            
            self._add_to_history(message)
            
            self.logger.debug(f"Message sent from {sender} to {recipient}: {message_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return False
    
    def receive_message(self, agent_name: str, timeout: Optional[int] = None) -> Optional[Message]:
        try:
            if agent_name not in self.message_queues:
                self.logger.warning(f"Agent '{agent_name}' not registered")
                return None
            
            priority, message = self.message_queues[agent_name].get(timeout=timeout)
            message.status = 'delivered'
            
            self.logger.debug(f"Message received by {agent_name} from {message.sender}")
            return message
            
        except queue.Empty:
            return None
        except Exception as e:
            self.logger.error(f"Failed to receive message: {e}")
            return None
    
    def broadcast_message(self, sender: str, message_type: str, content: Any, priority: int = 5) -> int:
        count = 0
        for agent_name in self.agents.keys():
            if agent_name != sender and self.agents[agent_name]:
                if self.send_message(sender, agent_name, message_type, content, priority):
                    count += 1
        
        self.logger.info(f"Broadcast from {sender} to {count} agents")
        return count
    
    def get_queue_size(self, agent_name: str) -> int:
        if agent_name in self.message_queues:
            return self.message_queues[agent_name].qsize()
        return 0
    
    def clear_queue(self, agent_name: str):
        if agent_name in self.message_queues:
            while not self.message_queues[agent_name].empty():
                try:
                    self.message_queues[agent_name].get_nowait()
                except queue.Empty:
                    break
            self.logger.info(f"Queue cleared for agent: {agent_name}")
    
    def _add_to_history(self, message: Message):
        self.message_history.append(message.to_dict())
        
        if len(self.message_history) > self.max_history:
            self.message_history = self.message_history[-self.max_history:]
    
    def get_message_history(self, agent_name: Optional[str] = None, limit: int = 100):
        if agent_name:
            filtered = [
                msg for msg in self.message_history
                if msg['sender'] == agent_name or msg['recipient'] == agent_name
            ]
            return filtered[-limit:]
        return self.message_history[-limit:]
    
    def get_system_status(self) -> Dict[str, Any]:
        """الحصول على حالة النظام الكاملة
        
        Returns:
            Dict يحتوي على معلومات الحالة الشاملة
        """
        return {
            'registered_agents': list(self.agents.keys()),
            'active_agents': [name for name, active in self.agents.items() if active],
            'inactive_agents': [name for name, active in self.agents.items() if not active],
            'queue_sizes': {name: self.get_queue_size(name) for name in self.agents.keys()},
            'total_messages_processed': len(self.message_history),
            'system_health': self._calculate_health_score()
        }
    
    def _calculate_health_score(self) -> Dict[str, Any]:
        """حساب نقاط صحة النظام
        
        Returns:
            Dict يحتوي على نقاط الصحة والتفاصيل
        """
        total_agents = len(self.agents)
        active_agents = sum(1 for active in self.agents.values() if active)
        
        # فحص الطوابير الممتلئة
        full_queues = 0
        overloaded_agents = []
        for name, agent_queue in self.message_queues.items():
            size = agent_queue.qsize()
            if size > 800:  # 80% من الحد الأقصى 1000
                full_queues += 1
                overloaded_agents.append({'agent': name, 'queue_size': size})
        
        # حساب النقاط (0-100)
        health_score = 100
        
        # خصم نقاط للوكلاء غير النشطين
        if total_agents > 0:
            inactive_penalty = ((total_agents - active_agents) / total_agents) * 30
            health_score -= inactive_penalty
        
        # خصم نقاط للطوابير الممتلئة
        if total_agents > 0:
            queue_penalty = (full_queues / total_agents) * 40
            health_score -= queue_penalty
        
        return {
            'score': max(0, int(health_score)),
            'status': 'healthy' if health_score >= 80 else 'degraded' if health_score >= 50 else 'unhealthy',
            'active_agents_ratio': f"{active_agents}/{total_agents}" if total_agents > 0 else "0/0",
            'overloaded_agents': overloaded_agents,
            'warnings': self._generate_health_warnings(health_score, overloaded_agents)
        }
    
    def _generate_health_warnings(self, health_score: float, overloaded_agents: list) -> list:
        """توليد تحذيرات صحية
        
        Args:
            health_score: نقاط الصحة الحالية
            overloaded_agents: قائمة الوكلاء المحملة بشكل زائد
        
        Returns:
            قائمة التحذيرات
        """
        warnings = []
        
        if health_score < 50:
            warnings.append("صحة النظام منخفضة للغاية - تحقق من الوكلاء غير النشطين")
        elif health_score < 80:
            warnings.append("صحة النظام متدهورة - مراقبة موصى بها")
        
        if overloaded_agents:
            for agent_info in overloaded_agents:
                warnings.append(
                    f"الطابور ممتلئ تقريباً للوكيل '{agent_info['agent']}' "
                    f"({agent_info['queue_size']}/1000 رسالة)"
                )
        
        return warnings
    
    def health_check(self) -> Dict[str, Any]:
        """فحص صحة نظام الاتصال
        
        Returns:
            Dict يحتوي على حالة الصحة والتفاصيل
        """
        status = self.get_system_status()
        health = status['system_health']
        
        return {
            'healthy': health['status'] == 'healthy',
            'status': health['status'],
            'score': health['score'],
            'active_agents': len(status['active_agents']),
            'total_agents': len(status['registered_agents']),
            'warnings': health['warnings'],
            'details': {
                'queue_sizes': status['queue_sizes'],
                'overloaded_agents': health['overloaded_agents']
            }
        }
    
    def is_agent_responsive(self, agent_name: str, timeout: int = 5) -> bool:
        """فحص استجابة الوكيل
        
        Args:
            agent_name: اسم الوكيل
            timeout: مهلة الانتظار بالثواني
        
        Returns:
            True إذا كان الوكيل مستجيباً
        """
        if agent_name not in self.agents:
            self.logger.warning(f"الوكيل '{agent_name}' غير مسجل")
            return False
        
        if not self.agents[agent_name]:
            self.logger.debug(f"الوكيل '{agent_name}' غير نشط")
            return False
        
        # فحص حجم الطابور
        queue_size = self.get_queue_size(agent_name)
        if queue_size >= 900:  # 90% ممتلئ
            self.logger.warning(f"طابور الوكيل '{agent_name}' ممتلئ تقريباً ({queue_size}/1000)")
            return False
        
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """الحصول على إحصائيات النظام التفصيلية
        
        Returns:
            Dict يحتوي على الإحصائيات
        """
        # حساب إحصائيات الرسائل
        message_types_count = {}
        priority_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        for msg in self.message_history:
            msg_type = msg.get('message_type', 'unknown')
            message_types_count[msg_type] = message_types_count.get(msg_type, 0) + 1
            
            priority = msg.get('priority', 5)
            if priority in priority_distribution:
                priority_distribution[priority] += 1
        
        # حساب متوسط حجم الطوابير
        queue_sizes = [self.get_queue_size(name) for name in self.agents.keys()]
        avg_queue_size = sum(queue_sizes) / len(queue_sizes) if queue_sizes else 0
        
        return {
            'total_messages': len(self.message_history),
            'message_types': message_types_count,
            'priority_distribution': priority_distribution,
            'average_queue_size': round(avg_queue_size, 2),
            'max_queue_size': max(queue_sizes) if queue_sizes else 0,
            'agents': {
                'total': len(self.agents),
                'active': sum(1 for active in self.agents.values() if active),
                'inactive': sum(1 for active in self.agents.values() if not active)
            }
        }


def get_communication_system():
    return AgentCommunication()


if __name__ == "__main__":
    comm = AgentCommunication()
    comm.register_agent('test_agent_1')
    comm.register_agent('test_agent_2')
    
    comm.send_message('test_agent_1', 'test_agent_2', 'test', {'data': 'Hello!'})
    
    msg = comm.receive_message('test_agent_2', timeout=1)
    if msg:
        print(f"✓ Message received: {msg.content}")
    
    status = comm.get_system_status()
    print(f"✓ Communication system test completed")
    print(f"  Active agents: {status['active_agents']}")
