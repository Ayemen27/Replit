import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import yaml
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from tools.logger import get_logger


class NotificationSystem:
    def __init__(self, secrets_manager=None):
        self.logger = get_logger('notification_system')
        
        if secrets_manager is None:
            try:
                from dev_platform.core.secrets_manager import get_secrets_manager
                secrets_manager = get_secrets_manager()
            except ImportError:
                self.logger.warning("SecretsManager not available, using environment variables only")
        
        self.secrets = secrets_manager
        self.config = self._load_config()
        
        self.telegram_config = self._build_telegram_config()
        self.email_config = self._build_email_config()
        
        self._validate_configs()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load base configuration from config.yaml"""
        config_path = Path(__file__).parent.parent / 'configs' / 'config.yaml'
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return {}
    
    def _get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret from SecretsManager or environment"""
        if self.secrets:
            return self.secrets.get(key, default)
        return os.getenv(key, default)
    
    def _safe_int(self, value: Any, default: int) -> int:
        """Safely convert value to int with fallback"""
        if value is None:
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            self.logger.warning(f"Invalid int value '{value}', using default {default}")
            return default
    
    def _build_telegram_config(self) -> Dict[str, Any]:
        """Build Telegram config from SecretsManager + config file"""
        base_config = self.config.get('notifications', {}).get('telegram', {})
        
        return {
            'enabled': base_config.get('enabled', False),
            'bot_token': self._get_secret('TELEGRAM_BOT_TOKEN', base_config.get('bot_token')),
            'chat_id': self._get_secret('TELEGRAM_CHAT_ID', base_config.get('chat_id')),
            'api_url': base_config.get('api_url', 'https://api.telegram.org/bot'),
            'timeout': self._safe_int(base_config.get('timeout'), 10),
            'retry_attempts': self._safe_int(base_config.get('retry_attempts'), 3)
        }
    
    def _build_email_config(self) -> Dict[str, Any]:
        """Build Email config from SecretsManager + config file"""
        base_config = self.config.get('notifications', {}).get('email', {})
        
        recipient_emails = base_config.get('recipient_emails', [])
        if isinstance(recipient_emails, list) and len(recipient_emails) > 0:
            resolved_recipients = []
            for email in recipient_emails:
                if email.startswith('${') and email.endswith('}'):
                    var_name = email[2:-1]
                    resolved_email = self._get_secret(var_name)
                    if resolved_email:
                        resolved_recipients.append(resolved_email)
                else:
                    resolved_recipients.append(email)
            recipient_emails = resolved_recipients
        
        email_port_str = self._get_secret('EMAIL_PORT', str(base_config.get('smtp_port', 587)))
        
        return {
            'enabled': base_config.get('enabled', False),
            'smtp_server': self._get_secret('EMAIL_HOST', base_config.get('smtp_server', '')),
            'smtp_port': self._safe_int(email_port_str, 587),
            'sender_email': self._get_secret('SMTP_USER', base_config.get('sender_email', '')),
            'sender_password': self._get_secret('SMTP_PASSWORD', base_config.get('sender_password', '')),
            'recipient_emails': recipient_emails,
            'use_tls': base_config.get('use_tls', True),
            'timeout': self._safe_int(base_config.get('timeout'), 30),
            'retry_attempts': self._safe_int(base_config.get('retry_attempts'), 3)
        }
    
    def _is_unresolved_placeholder(self, value: Optional[str]) -> bool:
        """Check if value is an unresolved ${...} placeholder"""
        if not value or not isinstance(value, str):
            return False
        return value.startswith('${') and value.endswith('}')
    
    def _is_invalid_credential(self, value: Optional[str], sentinels: List[str]) -> bool:
        """Check if credential is invalid (None, placeholder, or sentinel value)"""
        if not value:
            return True
        if self._is_unresolved_placeholder(value):
            return True
        return value in sentinels
    
    def _validate_configs(self):
        """Validate notification configurations and auto-disable on missing credentials"""
        if self.telegram_config.get('enabled'):
            bot_token = self.telegram_config.get('bot_token')
            chat_id = self.telegram_config.get('chat_id')
            
            if self._is_invalid_credential(bot_token, ['YOUR_TELEGRAM_BOT_TOKEN_HERE']):
                self.logger.warning(
                    "تم تفعيل تيليجرام ولكن bot_token غير مُعد أو غير محلول. "
                    "قم بتعيين TELEGRAM_BOT_TOKEN في مدير الأسرار. جاري تعطيل تيليجرام."
                )
                self.telegram_config['enabled'] = False
            
            if self._is_invalid_credential(chat_id, ['YOUR_CHAT_ID_HERE']):
                self.logger.warning(
                    "تم تفعيل تيليجرام ولكن chat_id غير مُعد أو غير محلول. "
                    "قم بتعيين TELEGRAM_CHAT_ID في مدير الأسرار. جاري تعطيل تيليجرام."
                )
                self.telegram_config['enabled'] = False
        
        if self.email_config.get('enabled'):
            smtp_server = self.email_config.get('smtp_server')
            sender_email = self.email_config.get('sender_email')
            sender_password = self.email_config.get('sender_password')
            recipient_emails = self.email_config.get('recipient_emails', [])
            
            if self._is_invalid_credential(smtp_server, []):
                self.logger.warning(
                    "تم تفعيل البريد الإلكتروني ولكن خادم SMTP غير مُعد أو غير محلول. "
                    "قم بتعيين EMAIL_HOST في مدير الأسرار. جاري تعطيل البريد الإلكتروني."
                )
                self.email_config['enabled'] = False
            
            if self._is_invalid_credential(sender_email, ['your-email@gmail.com']):
                self.logger.warning(
                    "تم تفعيل البريد الإلكتروني ولكن البريد المرسل غير مُعد أو غير محلول. "
                    "قم بتعيين SMTP_USER في مدير الأسرار. جاري تعطيل البريد الإلكتروني."
                )
                self.email_config['enabled'] = False
            
            if self._is_invalid_credential(sender_password, ['your-app-password']):
                self.logger.warning(
                    "تم تفعيل البريد الإلكتروني ولكن كلمة مرور المرسل غير مُعدة أو غير محلولة. "
                    "قم بتعيين SMTP_PASSWORD في مدير الأسرار. جاري تعطيل البريد الإلكتروني."
                )
                self.email_config['enabled'] = False
            
            if not recipient_emails or 'admin@example.com' in recipient_emails:
                self.logger.warning(
                    "تم تفعيل البريد الإلكتروني ولكن المستلمون غير مُعدون بشكل صحيح. "
                    "قم بتعيين SUPPORT_EMAIL في مدير الأسرار. جاري تعطيل البريد الإلكتروني."
                )
                self.email_config['enabled'] = False
    
    def send_notification(self, message, level='info', channels=None):
        if channels is None:
            channels = ['telegram', 'email']
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatted_message = f"[{level.upper()}] {timestamp}\n{message}"
        
        results = {}
        
        if 'telegram' in channels and self.telegram_config.get('enabled', False):
            results['telegram'] = self._send_telegram(formatted_message)
        
        if 'email' in channels and self.email_config.get('enabled', False):
            results['email'] = self._send_email(f"{level.upper()}: System Alert", formatted_message)
        
        return results
    
    def _send_telegram(self, message: str) -> Dict[str, Any]:
        """إرسال إشعار تيليجرام مع منطق إعادة المحاولة"""
        if not self.telegram_config.get('enabled'):
            self.logger.debug("إشعارات تيليجرام معطلة")
            return {'success': False, 'error': 'تيليجرام معطل'}
        
        bot_token = self.telegram_config.get('bot_token')
        chat_id = self.telegram_config.get('chat_id')
        api_url = self.telegram_config.get('api_url', 'https://api.telegram.org/bot')
        timeout = self.telegram_config.get('timeout', 10)
        retry_attempts = self.telegram_config.get('retry_attempts', 3)
        
        url = f"{api_url}{bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        last_error = None
        for attempt in range(retry_attempts):
            try:
                response = requests.post(url, json=payload, timeout=timeout)
                
                if response.status_code == 200:
                    self.logger.info(f"تم إرسال إشعار تيليجرام بنجاح (محاولة {attempt + 1})")
                    return {'success': True, 'response': response.json(), 'attempt': attempt + 1}
                else:
                    last_error = f"HTTP {response.status_code}: {response.text}"
                    self.logger.warning(f"خطأ في API تيليجرام (محاولة {attempt + 1}): {last_error}")
                    
            except Exception as e:
                last_error = str(e)
                self.logger.warning(f"فشل إرسال تيليجرام (محاولة {attempt + 1}): {e}")
            
            if attempt < retry_attempts - 1:
                backoff_time = 2 ** attempt
                self.logger.debug(f"إعادة المحاولة خلال {backoff_time} ثانية...")
                time.sleep(backoff_time)
        
        self.logger.error(f"فشل إرسال إشعار تيليجرام بعد {retry_attempts} محاولات: {last_error}")
        return {'success': False, 'error': last_error, 'attempts': retry_attempts}
    
    def _send_email(self, subject: str, body: str) -> Dict[str, Any]:
        """إرسال إشعار بريد إلكتروني مع منطق إعادة المحاولة"""
        if not self.email_config.get('enabled'):
            self.logger.debug("إشعارات البريد الإلكتروني معطلة")
            return {'success': False, 'error': 'البريد الإلكتروني معطل'}
        
        smtp_server = str(self.email_config.get('smtp_server', ''))
        smtp_port = self.email_config.get('smtp_port', 587)
        sender_email = str(self.email_config.get('sender_email', ''))
        sender_password = str(self.email_config.get('sender_password', ''))
        recipient_emails = self.email_config.get('recipient_emails', [])
        use_tls = self.email_config.get('use_tls', True)
        timeout = self.email_config.get('timeout', 30)
        retry_attempts = self.email_config.get('retry_attempts', 3)
        
        if not smtp_server or not sender_email or not sender_password:
            return {'success': False, 'error': 'إعدادات البريد الإلكتروني غير مكتملة'}
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = ', '.join(recipient_emails)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        last_error = None
        for attempt in range(retry_attempts):
            try:
                with smtplib.SMTP(smtp_server, smtp_port, timeout=timeout) as server:
                    if use_tls:
                        server.starttls()
                    server.login(sender_email, sender_password)
                    server.send_message(msg)
                
                self.logger.info(f"تم إرسال البريد الإلكتروني إلى {len(recipient_emails)} مستلم (محاولة {attempt + 1})")
                return {'success': True, 'recipients': len(recipient_emails), 'attempt': attempt + 1}
                
            except Exception as e:
                last_error = str(e)
                self.logger.warning(f"فشل إرسال البريد الإلكتروني (محاولة {attempt + 1}): {e}")
            
            if attempt < retry_attempts - 1:
                backoff_time = 2 ** attempt
                self.logger.debug(f"إعادة المحاولة خلال {backoff_time} ثانية...")
                time.sleep(backoff_time)
        
        self.logger.error(f"فشل إرسال البريد الإلكتروني بعد {retry_attempts} محاولات: {last_error}")
        return {'success': False, 'error': last_error, 'attempts': retry_attempts}
    
    def send_alert(self, alert_type: str, message: str, details: Optional[str] = None) -> Dict[str, Any]:
        """إرسال إشعار تنبيه"""
        alert_message = f"🚨 تنبيه: {alert_type}\n\n{message}"
        
        if details:
            alert_message += f"\n\nالتفاصيل:\n{details}"
        
        return self.send_notification(alert_message, level='alert')
    
    def send_critical_alert(self, message: str, details: Optional[str] = None) -> Dict[str, Any]:
        """إرسال تنبيه حرج"""
        return self.send_alert('حرج', message, details)
    
    def send_warning_alert(self, message: str, details: Optional[str] = None) -> Dict[str, Any]:
        """إرسال تحذير"""
        return self.send_alert('تحذير', message, details)
    
    def send_info(self, message: str) -> Dict[str, Any]:
        """إرسال إشعار معلومات"""
        return self.send_notification(message, level='info')
    
    def send_telegram(self, message: str) -> Dict[str, Any]:
        """إرسال رسالة مباشرة عبر تيليجرام"""
        return self._send_telegram(message)
    
    def health_check(self, quick: bool = False) -> Dict[str, Any]:
        """فحص صحة قنوات الإشعارات
        
        Args:
            quick: إذا كانت True، استخدام مهلات زمنية أقصر (2 ثانية) لتجنب التعليق
        
        Returns:
            Dict مع حالة القنوات والتفاصيل
        """
        results = {
            'telegram': {'available': False, 'error': None},
            'email': {'available': False, 'error': None}
        }
        
        check_timeout = 2 if quick else 5
        
        if self.telegram_config.get('enabled'):
            try:
                bot_token = self.telegram_config.get('bot_token')
                api_url = self.telegram_config.get('api_url', 'https://api.telegram.org/bot')
                
                url = f"{api_url}{bot_token}/getMe"
                response = requests.get(url, timeout=check_timeout)
                
                if response.status_code == 200:
                    results['telegram']['available'] = True
                    bot_info = response.json().get('result', {})
                    results['telegram']['bot_name'] = bot_info.get('username')
                else:
                    results['telegram']['error'] = f"HTTP {response.status_code}"
                    
            except requests.Timeout:
                results['telegram']['error'] = 'انتهت المهلة'
            except Exception as e:
                results['telegram']['error'] = str(e)
        else:
            results['telegram']['error'] = 'معطل'
        
        if self.email_config.get('enabled'):
            try:
                smtp_server = str(self.email_config.get('smtp_server', ''))
                smtp_port = self.email_config.get('smtp_port', 587)
                
                if not smtp_server:
                    results['email']['error'] = 'خادم SMTP غير مُعد'
                    return results
                
                with smtplib.SMTP(smtp_server, smtp_port, timeout=check_timeout) as server:
                    server.ehlo()
                    if self.email_config.get('use_tls', True):
                        server.starttls()
                        server.ehlo()
                    results['email']['available'] = True
                    results['email']['server'] = smtp_server
                    
            except smtplib.SMTPException as e:
                results['email']['error'] = f'SMTP: {str(e)}'
            except Exception as e:
                results['email']['error'] = str(e)
        else:
            results['email']['error'] = 'معطل'
        
        return results
    
    def dispatch(self, message: str, level: str = 'info', channels: Optional[List[str]] = None) -> Dict[str, Any]:
        """واجهة موحدة لإرسال الإشعارات
        
        Args:
            message: الرسالة المراد إرسالها
            level: مستوى الخطورة (info, warning, alert, critical)
            channels: قائمة القنوات المراد استخدامها (telegram, email) أو None للكل
        
        Returns:
            Dict مع النتائج لكل قناة
        """
        return self.send_notification(message, level=level, channels=channels)


if __name__ == "__main__":
    notifier = NotificationSystem()
    print("✓ تم تهيئة نظام الإشعارات")
    print("ملاحظة: قم بتكوين توكن بوت تيليجرام وإعدادات البريد الإلكتروني في config.yaml لتفعيل الإشعارات")
