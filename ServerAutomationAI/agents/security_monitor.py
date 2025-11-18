import os
import re
import time
import subprocess
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional
from pathlib import Path
import yaml
from collections import defaultdict
from tools.logger import get_logger
from tools.agent_communication import get_communication_system


class SecurityMonitor:
    def __init__(self):
        self.logger = get_logger('security_monitor')
        self.config = self._load_config()
        self.comm_system = get_communication_system()
        
        self.agent_name = 'security_monitor'
        self.running = False
        
        agent_config = self.config.get('agents', {}).get('security_monitor', {})
        self.check_interval = agent_config.get('check_interval', 60)
        self.monitored_ports = agent_config.get('monitored_ports', [])
        self.max_failed_logins = agent_config.get('max_failed_logins', 5)
        
        self.failed_login_attempts = defaultdict(list)
        self.security_events = []
        self.max_events = 1000
        
        self.blocked_ips: Set[str] = set()
        self.blocked_ips_file = Path(agent_config.get('suspicious_ips_file', './configs/suspicious_ips.txt'))
        
        self.whitelist_ips: Set[str] = set()
        self.whitelist_ips_file = Path(agent_config.get('whitelist_ips_file', './configs/whitelist_ips.txt'))
        
        self.auto_block_enabled = agent_config.get('auto_block_enabled', True)
        self.block_duration_minutes = agent_config.get('block_duration_minutes', 1440)
        
        self._load_whitelist_ips()
        self._load_blocked_ips()
        self._restore_iptables_rules()
        
        self.comm_system.register_agent(self.agent_name)
        self.logger.info("Security Monitor initialized")
    
    def _load_config(self):
        config_path = Path(__file__).parent.parent / 'configs' / 'config.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def start(self):
        self.running = True
        self.logger.info("Security Monitor started")
        
        try:
            while self.running:
                self._perform_security_checks()
                self._cleanup_old_events()
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.logger.info("Security Monitor shutting down...")
            self.stop()
    
    def stop(self):
        self.running = False
        self.comm_system.unregister_agent(self.agent_name)
        self.logger.info("Security Monitor stopped")
    
    def _perform_security_checks(self):
        self.logger.debug("Performing security checks")
        
        self._check_authentication_logs()
        self._check_suspicious_processes()
        self._check_file_permissions()
    
    def _check_authentication_logs(self):
        auth_log_paths = [
            './logs/security.log',
            './logs/ai_manager.log',
        ]
        
        system_log_paths = [
            '/var/log/auth.log',
            '/var/log/secure',
        ]
        
        all_paths = auth_log_paths + system_log_paths
        
        for log_path in all_paths:
            if not os.path.exists(log_path):
                continue
                
            try:
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()[-100:]
                
                for line in lines:
                    self._analyze_auth_line(line)
                    
            except PermissionError:
                self.logger.debug(f"No permission to read {log_path}")
            except Exception as e:
                self.logger.debug(f"Could not read {log_path}: {e}")
    
    def _analyze_auth_line(self, line: str):
        failed_patterns = [
            r'Failed password for (\w+) from ([\d\.]+)',
            r'Failed password for invalid user (\w+) from ([\d\.]+)',
            r'authentication failure.*user=(\w+)',
            r'Invalid user (\w+) from ([\d\.]+)',
            r'Connection closed by authenticating user (\w+) ([\d\.]+)',
            r'maximum authentication attempts exceeded for (\w+) from ([\d\.]+)',
        ]
        
        for pattern in failed_patterns:
            match = re.search(pattern, line)
            if match:
                self._record_failed_login(line, match.groups())
                break
    
    def _record_failed_login(self, log_line: str, match_groups: tuple):
        timestamp = datetime.now()
        
        ip_address = 'unknown'
        username = 'unknown'
        
        if len(match_groups) >= 2:
            username = match_groups[0]
            ip_address = match_groups[1]
        elif len(match_groups) == 1:
            username = match_groups[0]
        
        event = {
            'timestamp': timestamp.isoformat(),
            'type': 'failed_login',
            'username': username,
            'ip_address': ip_address,
            'log_line': log_line.strip()
        }
        
        self._add_security_event(event)
        
        if ip_address == 'unknown' or ip_address in self.blocked_ips:
            return
        
        self.failed_login_attempts[ip_address].append(timestamp)
        
        recent_attempts = [
            t for t in self.failed_login_attempts[ip_address]
            if timestamp - t < timedelta(minutes=30)
        ]
        self.failed_login_attempts[ip_address] = recent_attempts
        
        if len(recent_attempts) >= self.max_failed_logins:
            self._block_ip_address(ip_address, username, len(recent_attempts))
            self._send_security_alert(
                f"تم حظر IP {ip_address} تلقائياً",
                {
                    'ip_address': ip_address,
                    'username': username,
                    'attempts': len(recent_attempts),
                    'threshold': self.max_failed_logins,
                    'action': 'blocked'
                },
                severity='critical'
            )
    
    def _check_suspicious_processes(self):
        try:
            import psutil
            
            suspicious_names = ['nc', 'ncat', 'netcat', 'cryptominer']
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_name = proc.info['name'].lower()
                    
                    for suspicious in suspicious_names:
                        if suspicious in proc_name:
                            event = {
                                'timestamp': datetime.now().isoformat(),
                                'type': 'suspicious_process',
                                'process_name': proc.info['name'],
                                'pid': proc.info['pid'],
                                'cmdline': ' '.join(proc.info['cmdline'] or [])
                            }
                            
                            self._add_security_event(event)
                            self._send_security_alert(
                                f"Suspicious process detected: {proc.info['name']}",
                                event,
                                severity='warning'
                            )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except ImportError:
            pass
        except Exception as e:
            self.logger.error(f"Error checking processes: {e}")
    
    def _check_file_permissions(self):
        critical_paths = [
            '/srv/ai_system/configs/config.yaml',
            '/srv/ai_system/configs/'
        ]
        
        for path in critical_paths:
            if os.path.exists(path):
                try:
                    stat_info = os.stat(path)
                    mode = stat_info.st_mode
                    
                    world_readable = bool(mode & 0o004)
                    world_writable = bool(mode & 0o002)
                    
                    if world_writable:
                        event = {
                            'timestamp': datetime.now().isoformat(),
                            'type': 'insecure_permissions',
                            'path': path,
                            'issue': 'world_writable',
                            'permissions': oct(mode)
                        }
                        
                        self._add_security_event(event)
                        self._send_security_alert(
                            f"Insecure file permissions: {path}",
                            event,
                            severity='warning'
                        )
                except Exception as e:
                    self.logger.debug(f"Could not check permissions for {path}: {e}")
    
    def _load_whitelist_ips(self):
        try:
            if self.whitelist_ips_file.exists():
                with open(self.whitelist_ips_file, 'r') as f:
                    self.whitelist_ips = {line.strip() for line in f if line.strip() and not line.startswith('#')}
                self.logger.info(f"✅ تم تحميل {len(self.whitelist_ips)} IP موثوق")
            else:
                self.whitelist_ips_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.whitelist_ips_file, 'w') as f:
                    f.write("# قائمة IPs الموثوقة التي لن يتم حظرها\n")
                    f.write("# مثال: 192.168.1.1\n")
                    f.write("# 127.0.0.1\n")
                self.logger.info("📝 تم إنشاء ملف القائمة البيضاء")
        except Exception as e:
            self.logger.error(f"خطأ في تحميل IPs الموثوقة: {e}")
    
    def _load_blocked_ips(self):
        try:
            if self.blocked_ips_file.exists():
                with open(self.blocked_ips_file, 'r') as f:
                    self.blocked_ips = {line.strip() for line in f if line.strip()}
                self.logger.info(f"🛡️ تم تحميل {len(self.blocked_ips)} IP محظور")
        except Exception as e:
            self.logger.error(f"خطأ في تحميل IPs المحظورة: {e}")
    
    def _restore_iptables_rules(self):
        if not self.auto_block_enabled or not self.blocked_ips:
            return
        
        restored = 0
        failed = 0
        
        for ip in self.blocked_ips:
            try:
                result = subprocess.run(
                    ['sudo', 'iptables', '-C', 'INPUT', '-s', ip, '-j', 'DROP'],
                    capture_output=True,
                    timeout=5
                )
                
                if result.returncode != 0:
                    result = subprocess.run(
                        ['sudo', 'iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP'],
                        capture_output=True,
                        timeout=5
                    )
                    
                    if result.returncode == 0:
                        restored += 1
                    else:
                        failed += 1
                        self.logger.warning(f"فشل استعادة حظر {ip}")
            except Exception as e:
                failed += 1
                self.logger.error(f"خطأ في استعادة حظر {ip}: {e}")
        
        if restored > 0:
            self.logger.info(f"♻️ تم استعادة حظر {restored} IP بعد إعادة التشغيل")
        if failed > 0:
            self.logger.warning(f"⚠️ فشل استعادة {failed} IP")
    
    def _block_ip_address(self, ip_address: str, username: str, attempts: int):
        if not self.auto_block_enabled:
            self.logger.debug(f"الحظر التلقائي معطل: {ip_address}")
            return
        
        if ip_address in self.blocked_ips:
            return
        
        if ip_address in self.whitelist_ips:
            self.logger.warning(
                f"⚠️ IP {ip_address} في القائمة البيضاء - لن يتم حظره (المحاولات: {attempts})"
            )
            return
        
        try:
            result = subprocess.run(
                ['sudo', 'iptables', '-A', 'INPUT', '-s', ip_address, '-j', 'DROP'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.blocked_ips.add(ip_address)
                self._save_blocked_ip(ip_address)
                
                self.logger.warning(
                    f"🛡️ تم حظر IP {ip_address} | المستخدم: {username} | المحاولات: {attempts}"
                )
                
                self._notify_ai_manager_of_block(ip_address, username, attempts)
            else:
                self.logger.error(f"فشل حظر IP {ip_address}: {result.stderr}")
        except subprocess.TimeoutExpired:
            self.logger.error(f"انتهت مهلة حظر IP {ip_address}")
        except Exception as e:
            self.logger.error(f"خطأ في حظر IP {ip_address}: {e}")
    
    def _save_blocked_ip(self, ip_address: str):
        try:
            self.blocked_ips_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.blocked_ips_file, 'a') as f:
                f.write(f"{ip_address}\n")
        except Exception as e:
            self.logger.error(f"خطأ في حفظ IP المحظور: {e}")
    
    def _get_ip_geolocation(self, ip_address: str) -> Optional[Dict]:
        """الحصول على معلومات جغرافية عن IP"""
        if ip_address == 'unknown':
            return None
        
        try:
            response = requests.get(
                f'http://ip-api.com/json/{ip_address}?fields=status,country,countryCode,city,lat,lon,timezone',
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    return {
                        'country': data.get('country', 'غير معروف'),
                        'country_code': data.get('countryCode', ''),
                        'city': data.get('city', 'غير معروف'),
                        'latitude': data.get('lat'),
                        'longitude': data.get('lon'),
                        'timezone': data.get('timezone', 'غير معروف')
                    }
        except requests.Timeout:
            self.logger.debug(f"انتهت مهلة طلب موقع IP {ip_address}")
        except Exception as e:
            self.logger.debug(f"خطأ في الحصول على موقع IP {ip_address}: {e}")
        
        return None
    
    def _get_country_flag_emoji(self, country_code: str) -> str:
        """الحصول على علم الدولة من رمز الدولة"""
        if not country_code or len(country_code) != 2:
            return "🏴"
        
        country_code = country_code.upper()
        
        flag_offset = 127397
        flag = ''.join(chr(ord(char) + flag_offset) for char in country_code)
        return flag
    
    def _notify_ai_manager_of_block(self, ip_address: str, username: str, attempts: int):
        geo_info = self._get_ip_geolocation(ip_address)
        
        location_text = "غير معروف"
        country_flag = "🏴"
        
        if geo_info:
            city = geo_info.get('city', 'غير معروف')
            country = geo_info.get('country', 'غير معروف')
            country_code = geo_info.get('country_code', '')
            location_text = f"{city}, {country}"
            country_flag = self._get_country_flag_emoji(country_code)
        
        self.comm_system.send_message(
            self.agent_name,
            'ai_manager',
            'action_taken',
            {
                'action': 'ip_blocked',
                'ip_address': ip_address,
                'username': username,
                'attempts': attempts,
                'timestamp': datetime.now().isoformat(),
                'location': location_text,
                'country_flag': country_flag,
                'geo_info': geo_info,
                'reason': f'تجاوز الحد الأقصى ({self.max_failed_logins}) لمحاولات تسجيل الدخول الفاشلة'
            },
            priority=1
        )
    
    def _add_security_event(self, event: Dict):
        self.security_events.append(event)
        
        if len(self.security_events) > self.max_events:
            self.security_events = self.security_events[-self.max_events:]
        
        self.logger.warning(f"Security event: {event['type']}")
    
    def _send_security_alert(self, message: str, details: Dict, severity: str = 'warning'):
        self.comm_system.send_message(
            self.agent_name,
            'ai_manager',
            'alert',
            {
                'level': severity,
                'message': message,
                'details': details,
                'alert_type': 'security',
                'timestamp': datetime.now().isoformat()
            },
            priority=1 if severity == 'critical' else 3
        )
    
    def _cleanup_old_events(self):
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        for ip in list(self.failed_login_attempts.keys()):
            self.failed_login_attempts[ip] = [
                t for t in self.failed_login_attempts[ip]
                if t > cutoff_time
            ]
            
            if not self.failed_login_attempts[ip]:
                del self.failed_login_attempts[ip]
    
    def get_security_summary(self) -> Dict:
        recent_events = self.security_events[-100:]
        
        summary = {
            'total_events': len(self.security_events),
            'recent_events_count': len(recent_events),
            'by_type': defaultdict(int),
            'suspicious_ips': list(self.failed_login_attempts.keys())
        }
        
        for event in recent_events:
            summary['by_type'][event['type']] += 1
        
        return dict(summary)


if __name__ == "__main__":
    monitor = SecurityMonitor()
    print("✓ Security Monitor initialized")
    print("Running security checks for 5 seconds...")
    
    import threading
    thread = threading.Thread(target=monitor.start, daemon=True)
    thread.start()
    time.sleep(5)
    monitor.stop()
    
    summary = monitor.get_security_summary()
    print(f"✓ Security check completed")
    print(f"  Total events: {summary['total_events']}")
