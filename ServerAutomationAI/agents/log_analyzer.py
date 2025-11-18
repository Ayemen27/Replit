import os
import re
import time
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import yaml
from tools.logger import get_logger
from tools.agent_communication import get_communication_system


class LogAnalyzer:
    def __init__(self):
        self.logger = get_logger('log_analyzer')
        self.config = self._load_config()
        self.comm_system = get_communication_system()
        
        self.agent_name = 'log_analyzer'
        self.running = False
        
        agent_config = self.config.get('agents', {}).get('log_analyzer', {})
        self.check_interval = agent_config.get('check_interval', 120)
        self.log_paths = agent_config.get('log_paths', [])
        self.patterns = agent_config.get('patterns', {})
        
        self.findings = []
        self.max_findings = 500
        
        # Throttling/Debouncing: track last alert time per file+type
        self.last_alert_time = {}  # key: (file, type) -> timestamp
        self.alert_cooldown = 300  # 5 minutes cooldown per file+type
        
        self.comm_system.register_agent(self.agent_name)
        self.logger.info("Log Analyzer initialized")
    
    def _load_config(self):
        config_path = Path(__file__).parent.parent / 'configs' / 'config.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def start(self):
        self.running = True
        self.logger.info("Log Analyzer started")
        
        try:
            while self.running:
                self._analyze_logs()
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.logger.info("Log Analyzer shutting down...")
            self.stop()
    
    def stop(self):
        self.running = False
        self.comm_system.unregister_agent(self.agent_name)
        self.logger.info("Log Analyzer stopped")
    
    def _analyze_logs(self):
        self.logger.debug("Starting log analysis cycle")
        
        for log_path in self.log_paths:
            if os.path.isdir(log_path):
                self._analyze_directory(log_path)
            elif os.path.isfile(log_path):
                self._analyze_file(log_path)
            else:
                self.logger.warning(f"Log path not found: {log_path}")
    
    def _analyze_directory(self, directory: str):
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.log'):
                        # استبعاد السجلات التي قد تسبب حلقة لا نهائية
                        if file in ['notification_system.log', 'log_analyzer.log']:
                            continue
                        file_path = os.path.join(root, file)
                        self._analyze_file(file_path)
        except Exception as e:
            self.logger.error(f"Error analyzing directory {directory}: {e}")
    
    def _analyze_file(self, file_path: str):
        try:
            if not os.path.exists(file_path):
                return
            
            file_size = os.path.getsize(file_path)
            if file_size > 100 * 1024 * 1024:
                self.logger.warning(f"Skipping large file (>100MB): {file_path}")
                return
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()[-1000:]
            
            for line_num, line in enumerate(lines, 1):
                self._check_patterns(file_path, line_num, line)
                
        except Exception as e:
            self.logger.error(f"Error analyzing file {file_path}: {e}")
    
    def _check_patterns(self, file_path: str, line_num: int, line: str):
        for pattern_type, pattern_list in self.patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, line, re.IGNORECASE):
                    finding = {
                        'timestamp': datetime.now().isoformat(),
                        'file': file_path,
                        'line_number': line_num,
                        'type': pattern_type,
                        'pattern': pattern,
                        'content': line.strip()[:200]
                    }
                    
                    self._handle_finding(finding)
    
    def _handle_finding(self, finding: Dict):
        self.findings.append(finding)
        
        if len(self.findings) > self.max_findings:
            self.findings = self.findings[-self.max_findings:]
        
        severity = self._get_severity(finding['type'])
        
        self.logger.info(f"Log finding [{finding['type']}]: {finding['file']}:{finding['line_number']}")
        
        if severity in ['error', 'critical', 'security']:
            self._send_alert(finding, severity)
    
    def _get_severity(self, finding_type: str) -> str:
        severity_map = {
            'error': 'error',
            'warning': 'warning',
            'security': 'critical'
        }
        return severity_map.get(finding_type, 'info')
    
    def _send_alert(self, finding: Dict, severity: str):
        # Debouncing: prevent repeated alerts for same file+type
        alert_key = (finding['file'], finding['type'])
        current_time = time.time()
        
        # Check if we've sent an alert for this file+type recently
        if alert_key in self.last_alert_time:
            time_since_last_alert = current_time - self.last_alert_time[alert_key]
            if time_since_last_alert < self.alert_cooldown:
                # Skip this alert - too soon after last one
                return
        
        # Update last alert time
        self.last_alert_time[alert_key] = current_time
        
        self.comm_system.send_message(
            self.agent_name,
            'ai_manager',
            'alert',
            {
                'level': severity,
                'message': f"Log alert: {finding['type']} in {finding['file']}",
                'finding': finding,
                'timestamp': datetime.now().isoformat()
            },
            priority=2 if severity == 'critical' else 4
        )
    
    def get_recent_findings(self, count: int = 50, finding_type: Optional[str] = None) -> List[Dict]:
        findings = self.findings[-count:]
        
        if finding_type:
            findings = [f for f in findings if f['type'] == finding_type]
        
        return findings
    
    def get_findings_summary(self) -> Dict:
        if not self.findings:
            return {'total': 0}
        
        summary = {
            'total': len(self.findings),
            'by_type': {},
            'recent_count': min(10, len(self.findings))
        }
        
        for finding in self.findings:
            finding_type = finding['type']
            summary['by_type'][finding_type] = summary['by_type'].get(finding_type, 0) + 1
        
        return summary


if __name__ == "__main__":
    analyzer = LogAnalyzer()
    print("✓ Log Analyzer initialized")
    print("Analyzing logs for 5 seconds...")
    
    import threading
    thread = threading.Thread(target=analyzer.start, daemon=True)
    thread.start()
    time.sleep(5)
    analyzer.stop()
    
    summary = analyzer.get_findings_summary()
    print(f"✓ Log analysis completed")
    print(f"  Total findings: {summary.get('total', 0)}")
