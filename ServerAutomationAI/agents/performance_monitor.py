import psutil
import time
from datetime import datetime
from typing import Dict
import yaml
from pathlib import Path
from tools.logger import get_logger
from tools.agent_communication import get_communication_system


class PerformanceMonitor:
    def __init__(self):
        self.logger = get_logger('performance_monitor')
        self.config = self._load_config()
        self.comm_system = get_communication_system()
        
        self.agent_name = 'performance_monitor'
        self.running = False
        
        self.thresholds = self.config.get('agents', {}).get('performance_monitor', {}).get('thresholds', {})
        self.check_interval = self.config.get('agents', {}).get('performance_monitor', {}).get('check_interval', 30)
        
        self.metrics_history = []
        self.max_history = 100
        
        self.comm_system.register_agent(self.agent_name)
        self.logger.info("Performance Monitor initialized")
    
    def _load_config(self):
        config_path = Path(__file__).parent.parent / 'configs' / 'config.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def start(self):
        self.running = True
        self.logger.info("Performance Monitor started")
        
        try:
            while self.running:
                metrics = self._collect_metrics()
                self._analyze_metrics(metrics)
                self._store_metrics(metrics)
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.logger.info("Performance Monitor shutting down...")
            self.stop()
    
    def stop(self):
        self.running = False
        self.comm_system.unregister_agent(self.agent_name)
        self.logger.info("Performance Monitor stopped")
    
    def _collect_metrics(self) -> Dict:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        net_io = psutil.net_io_counters()
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'percent': cpu_percent,
                'count': psutil.cpu_count(),
                'per_cpu': psutil.cpu_percent(percpu=True)
            },
            'memory': {
                'total_gb': round(memory.total / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2),
                'used_gb': round(memory.used / (1024**3), 2),
                'percent': memory.percent
            },
            'disk': {
                'total_gb': round(disk.total / (1024**3), 2),
                'used_gb': round(disk.used / (1024**3), 2),
                'free_gb': round(disk.free / (1024**3), 2),
                'percent': disk.percent
            },
            'network': {
                'bytes_sent_mb': round(net_io.bytes_sent / (1024**2), 2),
                'bytes_recv_mb': round(net_io.bytes_recv / (1024**2), 2),
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            }
        }
        
        self.logger.debug(f"Metrics collected - CPU: {cpu_percent}%, Memory: {memory.percent}%, Disk: {disk.percent}%")
        return metrics
    
    def _analyze_metrics(self, metrics: Dict):
        alerts = []
        
        cpu_threshold = self.thresholds.get('cpu_percent', 80)
        if metrics['cpu']['percent'] > cpu_threshold:
            alerts.append({
                'type': 'cpu',
                'level': 'warning',
                'message': f"CPU usage high: {metrics['cpu']['percent']}% (threshold: {cpu_threshold}%)",
                'value': metrics['cpu']['percent']
            })
        
        memory_threshold = self.thresholds.get('memory_percent', 85)
        if metrics['memory']['percent'] > memory_threshold:
            alerts.append({
                'type': 'memory',
                'level': 'warning',
                'message': f"Memory usage high: {metrics['memory']['percent']}% (threshold: {memory_threshold}%)",
                'value': metrics['memory']['percent']
            })
        
        disk_threshold = self.thresholds.get('disk_percent', 90)
        if metrics['disk']['percent'] > disk_threshold:
            alerts.append({
                'type': 'disk',
                'level': 'critical',
                'message': f"Disk usage critical: {metrics['disk']['percent']}% (threshold: {disk_threshold}%)",
                'value': metrics['disk']['percent']
            })
        
        if alerts:
            for alert in alerts:
                self.logger.warning(alert['message'])
                self._send_alert(alert)
    
    def _send_alert(self, alert: Dict):
        self.comm_system.send_message(
            self.agent_name,
            'ai_manager',
            'alert',
            {
                'level': alert['level'],
                'message': alert['message'],
                'alert_type': alert['type'],
                'value': alert['value'],
                'timestamp': datetime.now().isoformat()
            },
            priority=2 if alert['level'] == 'critical' else 5
        )
    
    def _store_metrics(self, metrics: Dict):
        self.metrics_history.append(metrics)
        
        if len(self.metrics_history) > self.max_history:
            self.metrics_history = self.metrics_history[-self.max_history:]
    
    def get_current_status(self) -> Dict:
        if self.metrics_history:
            return self.metrics_history[-1]
        return {}
    
    def get_metrics_summary(self, count: int = 10) -> Dict:
        recent_metrics = self.metrics_history[-count:] if count > 0 else self.metrics_history
        
        if not recent_metrics:
            return {}
        
        cpu_values = [m['cpu']['percent'] for m in recent_metrics]
        memory_values = [m['memory']['percent'] for m in recent_metrics]
        disk_values = [m['disk']['percent'] for m in recent_metrics]
        
        return {
            'cpu': {
                'avg': round(sum(cpu_values) / len(cpu_values), 2),
                'max': max(cpu_values),
                'min': min(cpu_values)
            },
            'memory': {
                'avg': round(sum(memory_values) / len(memory_values), 2),
                'max': max(memory_values),
                'min': min(memory_values)
            },
            'disk': {
                'avg': round(sum(disk_values) / len(disk_values), 2),
                'max': max(disk_values),
                'min': min(disk_values)
            },
            'samples': len(recent_metrics)
        }


if __name__ == "__main__":
    monitor = PerformanceMonitor()
    print("✓ Performance Monitor initialized")
    print("Collecting metrics for 5 seconds...")
    
    import threading
    thread = threading.Thread(target=monitor.start, daemon=True)
    thread.start()
    time.sleep(5)
    monitor.stop()
    
    current = monitor.get_current_status()
    print(f"✓ Current CPU: {current['cpu']['percent']}%")
    print(f"✓ Current Memory: {current['memory']['percent']}%")
    print(f"✓ Current Disk: {current['disk']['percent']}%")
