"""
اختبارات التكامل الشاملة لنظام الإشعارات
Integration tests for NotificationSystem (Telegram + Email)

يختبر:
- إرسال إشعارات Telegram (نجاح وفشل)
- إرسال إشعارات Email (نجاح وفشل)
- منطق إعادة المحاولة (retry logic)
- التكامل مع SecretsManager
- فحوصات الصحة (health checks)
- التعطيل التلقائي عند فشل بيانات الاعتماد
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from tools.notification_system import NotificationSystem


@pytest.fixture
def mock_secrets_manager_notifications():
    """Mock SecretsManager لاختبارات الإشعارات"""
    mock = MagicMock()
    
    # بيانات اعتماد Telegram صالحة
    mock.get.side_effect = lambda key, default=None: {
        'TELEGRAM_BOT_TOKEN': 'test-telegram-token-123',
        'TELEGRAM_CHAT_ID': 'test-chat-id-456',
        'EMAIL_HOST': 'smtp.gmail.com',
        'EMAIL_PORT': '587',
        'SMTP_USER': 'test@gmail.com',
        'SMTP_PASSWORD': 'test-password-123',
        'SUPPORT_EMAIL': 'support@test.com'
    }.get(key, default)
    
    return mock


@pytest.fixture
def notification_system_with_valid_config(mock_secrets_manager_notifications):
    """نظام إشعارات مع إعدادات صالحة"""
    # إنشاء نظام إشعارات مباشرة مع secrets manager mock
    notifier = NotificationSystem(secrets_manager=mock_secrets_manager_notifications)
    return notifier


class TestTelegramIntegration:
    """اختبارات تكامل Telegram"""
    
    def test_telegram_success_first_attempt(self, notification_system_with_valid_config):
        """اختبار إرسال ناجح من المحاولة الأولى"""
        notifier = notification_system_with_valid_config
        
        # تفعيل Telegram
        notifier.telegram_config['enabled'] = True
        
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'ok': True, 'result': {'message_id': 123}}
        
        with patch('requests.post', return_value=mock_response) as mock_post:
            result = notifier._send_telegram("رسالة اختبار")
            
            # التحقق من النجاح
            assert result['success'] is True
            assert result['attempt'] == 1
            assert 'response' in result
            
            # التحقق من استدعاء API مرة واحدة فقط
            assert mock_post.call_count == 1
            
            # التحقق من المعاملات
            call_args = mock_post.call_args
            assert 'sendMessage' in call_args[0][0]
            assert call_args[1]['json']['text'] == "رسالة اختبار"
    
    def test_telegram_retry_on_failure_then_success(self, notification_system_with_valid_config):
        """اختبار إعادة المحاولة بعد فشل ثم نجاح"""
        notifier = notification_system_with_valid_config
        notifier.telegram_config['enabled'] = True
        notifier.telegram_config['retry_attempts'] = 3
        
        # أول محاولتين تفشل، الثالثة تنجح
        attempt_count = 0
        
        def mock_post_with_retries(*args, **kwargs):
            nonlocal attempt_count
            attempt_count += 1
            
            if attempt_count < 3:
                # محاولات فاشلة
                raise Exception("Network error")
            else:
                # محاولة ناجحة
                response = MagicMock()
                response.status_code = 200
                response.json.return_value = {'ok': True}
                return response
        
        with patch('requests.post', side_effect=mock_post_with_retries):
            with patch('time.sleep'):  # تخطي الانتظار في الاختبارات
                result = notifier._send_telegram("اختبار إعادة المحاولة")
                
                # يجب أن ينجح في المحاولة الثالثة
                assert result['success'] is True
                assert result['attempt'] == 3
                assert attempt_count == 3
    
    def test_telegram_fails_after_all_retries(self, notification_system_with_valid_config):
        """اختبار الفشل بعد استنفاد جميع المحاولات"""
        notifier = notification_system_with_valid_config
        notifier.telegram_config['enabled'] = True
        notifier.telegram_config['retry_attempts'] = 3
        
        # كل المحاولات تفشل
        with patch('requests.post', side_effect=Exception("Persistent network error")):
            with patch('time.sleep'):
                result = notifier._send_telegram("اختبار الفشل الكامل")
                
                # يجب أن يفشل
                assert result['success'] is False
                assert 'error' in result
                assert result['attempts'] == 3
    
    def test_telegram_http_error_codes(self, notification_system_with_valid_config):
        """اختبار معالجة أكواد الخطأ HTTP المختلفة"""
        notifier = notification_system_with_valid_config
        notifier.telegram_config['enabled'] = True
        notifier.telegram_config['retry_attempts'] = 2
        
        # Mock 401 Unauthorized
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        
        with patch('requests.post', return_value=mock_response):
            with patch('time.sleep'):
                result = notifier._send_telegram("اختبار خطأ HTTP")
                
                # يجب أن يفشل
                assert result['success'] is False
                assert 'HTTP 401' in result['error']


class TestEmailIntegration:
    """اختبارات تكامل Email"""
    
    def test_email_success_first_attempt(self, notification_system_with_valid_config):
        """اختبار إرسال بريد ناجح من المحاولة الأولى"""
        notifier = notification_system_with_valid_config
        notifier.email_config['enabled'] = True
        notifier.email_config['recipient_emails'] = ['test@example.com']
        
        # Mock SMTP server
        mock_smtp = MagicMock()
        
        with patch('smtplib.SMTP', return_value=mock_smtp):
            result = notifier._send_email("موضوع الاختبار", "محتوى الاختبار")
            
            # التحقق من النجاح
            assert result['success'] is True
            assert result['attempt'] == 1
            assert result['recipients'] == 1
            
            # التحقق من استدعاء SMTP
            assert mock_smtp.__enter__.return_value.starttls.called
            assert mock_smtp.__enter__.return_value.login.called
            assert mock_smtp.__enter__.return_value.send_message.called
    
    def test_email_retry_on_smtp_exception(self, notification_system_with_valid_config):
        """اختبار إعادة المحاولة عند حدوث استثناء SMTP"""
        notifier = notification_system_with_valid_config
        notifier.email_config['enabled'] = True
        notifier.email_config['recipient_emails'] = ['test@example.com']
        notifier.email_config['retry_attempts'] = 3
        
        attempt_count = 0
        
        def mock_smtp_with_retries(*args, **kwargs):
            nonlocal attempt_count
            attempt_count += 1
            
            mock_smtp = MagicMock()
            smtp_context = mock_smtp.__enter__.return_value
            
            if attempt_count < 3:
                # محاولات فاشلة
                smtp_context.login.side_effect = Exception("SMTP authentication failed")
            else:
                # محاولة ناجحة
                smtp_context.login.side_effect = None
            
            return mock_smtp
        
        with patch('smtplib.SMTP', side_effect=mock_smtp_with_retries):
            with patch('time.sleep'):
                result = notifier._send_email("اختبار SMTP", "إعادة المحاولة")
                
                # يجب أن ينجح في المحاولة الثالثة
                assert result['success'] is True
                assert result['attempt'] == 3
    
    def test_email_fails_with_invalid_credentials(self, notification_system_with_valid_config):
        """اختبار الفشل مع بيانات اعتماد غير صالحة"""
        notifier = notification_system_with_valid_config
        notifier.email_config['enabled'] = True
        notifier.email_config['recipient_emails'] = ['test@example.com']
        notifier.email_config['retry_attempts'] = 2
        
        # Mock SMTP authentication failure
        mock_smtp = MagicMock()
        mock_smtp.__enter__.return_value.login.side_effect = Exception("Authentication failed")
        
        with patch('smtplib.SMTP', return_value=mock_smtp):
            with patch('time.sleep'):
                result = notifier._send_email("اختبار الفشل", "بيانات خاطئة")
                
                assert result['success'] is False
                assert 'error' in result


class TestSecretsManagerIntegration:
    """اختبارات التكامل مع SecretsManager"""
    
    def test_notification_system_loads_secrets_from_manager(self):
        """اختبار تحميل الأسرار من SecretsManager"""
        mock_secrets = MagicMock()
        mock_secrets.get.side_effect = lambda key, default=None: {
            'TELEGRAM_BOT_TOKEN': 'secret-token-from-manager',
            'TELEGRAM_CHAT_ID': 'secret-chat-id',
            'EMAIL_HOST': 'smtp.test.com',
            'SMTP_USER': 'secret-user@test.com',
            'SMTP_PASSWORD': 'secret-password'
        }.get(key, default)
        
        notifier = NotificationSystem(secrets_manager=mock_secrets)
        
        # التحقق من تحميل بيانات Telegram
        assert notifier.telegram_config['bot_token'] == 'secret-token-from-manager'
        assert notifier.telegram_config['chat_id'] == 'secret-chat-id'
        
        # التحقق من تحميل بيانات Email
        assert notifier.email_config['smtp_server'] == 'smtp.test.com'
        assert notifier.email_config['sender_email'] == 'secret-user@test.com'
        assert notifier.email_config['sender_password'] == 'secret-password'
    
    def test_auto_disable_on_invalid_telegram_credentials(self):
        """اختبار التعطيل التلقائي عند بيانات Telegram غير صالحة"""
        mock_secrets = MagicMock()
        mock_secrets.get.side_effect = lambda key, default=None: {
            'TELEGRAM_BOT_TOKEN': '${TELEGRAM_BOT_TOKEN}',  # غير محلول
            'TELEGRAM_CHAT_ID': 'YOUR_CHAT_ID_HERE'  # قيمة افتراضية
        }.get(key, default)
        
        # إنشاء config.yaml mock مع telegram enabled
        mock_config = {
            'notifications': {
                'telegram': {
                    'enabled': True,
                    'bot_token': '${TELEGRAM_BOT_TOKEN}',
                    'chat_id': 'YOUR_CHAT_ID_HERE'
                }
            }
        }
        
        with patch.object(NotificationSystem, '_load_config', return_value=mock_config):
            notifier = NotificationSystem(secrets_manager=mock_secrets)
            
            # يجب أن يتم تعطيل Telegram تلقائياً
            assert notifier.telegram_config['enabled'] is False
    
    def test_auto_disable_on_invalid_email_credentials(self):
        """اختبار التعطيل التلقائي عند بيانات Email غير صالحة"""
        mock_secrets = MagicMock()
        mock_secrets.get.side_effect = lambda key, default=None: {
            'EMAIL_HOST': '',  # فارغ
            'SMTP_USER': 'your-email@gmail.com',  # قيمة افتراضية
            'SMTP_PASSWORD': ''
        }.get(key, default)
        
        mock_config = {
            'notifications': {
                'email': {
                    'enabled': True,
                    'smtp_server': '',
                    'sender_email': 'your-email@gmail.com'
                }
            }
        }
        
        with patch.object(NotificationSystem, '_load_config', return_value=mock_config):
            notifier = NotificationSystem(secrets_manager=mock_secrets)
            
            # يجب أن يتم تعطيل Email تلقائياً
            assert notifier.email_config['enabled'] is False


class TestHealthChecks:
    """اختبارات فحوصات الصحة"""
    
    def test_health_check_telegram_available(self, notification_system_with_valid_config):
        """اختبار فحص صحة Telegram عندما يكون متاحاً"""
        notifier = notification_system_with_valid_config
        notifier.telegram_config['enabled'] = True
        
        # Mock successful getMe API call
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'ok': True,
            'result': {'username': 'test_bot'}
        }
        
        with patch('requests.get', return_value=mock_response):
            health = notifier.health_check(quick=True)
            
            assert health['telegram']['available'] is True
            assert health['telegram']['bot_name'] == 'test_bot'
            assert health['telegram']['error'] is None
    
    def test_health_check_telegram_timeout(self, notification_system_with_valid_config):
        """اختبار فحص صحة Telegram عند انتهاء المهلة"""
        notifier = notification_system_with_valid_config
        notifier.telegram_config['enabled'] = True
        
        import requests
        with patch('requests.get', side_effect=requests.Timeout("Request timeout")):
            health = notifier.health_check(quick=True)
            
            assert health['telegram']['available'] is False
            assert 'انتهت المهلة' in health['telegram']['error']
    
    def test_health_check_email_available(self, notification_system_with_valid_config):
        """اختبار فحص صحة Email عندما يكون متاحاً"""
        notifier = notification_system_with_valid_config
        notifier.email_config['enabled'] = True
        
        # Mock SMTP connection
        mock_smtp = MagicMock()
        
        with patch('smtplib.SMTP', return_value=mock_smtp):
            health = notifier.health_check(quick=True)
            
            assert health['email']['available'] is True
            assert 'server' in health['email']
            assert health['email']['error'] is None
    
    def test_health_check_disabled_channels(self):
        """اختبار فحص الصحة عندما تكون القنوات معطلة"""
        mock_secrets = MagicMock()
        mock_secrets.get.return_value = None
        
        mock_config = {
            'notifications': {
                'telegram': {'enabled': False},
                'email': {'enabled': False}
            }
        }
        
        with patch.object(NotificationSystem, '_load_config', return_value=mock_config):
            notifier = NotificationSystem(secrets_manager=mock_secrets)
            health = notifier.health_check(quick=True)
            
            assert health['telegram']['available'] is False
            assert health['telegram']['error'] == 'معطل'
            assert health['email']['available'] is False
            assert health['email']['error'] == 'معطل'


class TestDispatchInterface:
    """اختبارات واجهة Dispatch الموحدة"""
    
    def test_dispatch_to_specific_channels(self, notification_system_with_valid_config):
        """اختبار إرسال إشعار لقنوات محددة"""
        notifier = notification_system_with_valid_config
        notifier.telegram_config['enabled'] = True
        notifier.email_config['enabled'] = True
        
        # Mock Telegram success
        mock_telegram_response = MagicMock()
        mock_telegram_response.status_code = 200
        mock_telegram_response.json.return_value = {'ok': True}
        
        with patch('requests.post', return_value=mock_telegram_response):
            # إرسال فقط لـ Telegram
            result = notifier.dispatch("رسالة اختبار", level='info', channels=['telegram'])
            
            assert 'telegram' in result
            assert 'email' not in result
    
    def test_dispatch_to_all_channels(self, notification_system_with_valid_config):
        """اختبار إرسال إشعار لجميع القنوات"""
        notifier = notification_system_with_valid_config
        notifier.telegram_config['enabled'] = True
        notifier.email_config['enabled'] = True
        notifier.email_config['recipient_emails'] = ['test@example.com']
        
        # Mock successful responses
        mock_telegram = MagicMock()
        mock_telegram.status_code = 200
        mock_telegram.json.return_value = {'ok': True}
        
        mock_smtp = MagicMock()
        
        with patch('requests.post', return_value=mock_telegram):
            with patch('smtplib.SMTP', return_value=mock_smtp):
                # إرسال لجميع القنوات (None = all)
                result = notifier.dispatch("رسالة شاملة", level='alert', channels=None)
                
                assert 'telegram' in result
                assert 'email' in result


class TestAlertMethods:
    """اختبارات طرق التنبيهات المختلفة"""
    
    def test_send_critical_alert(self, notification_system_with_valid_config):
        """اختبار إرسال تنبيه حرج"""
        notifier = notification_system_with_valid_config
        notifier.telegram_config['enabled'] = True
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'ok': True}
        
        with patch('requests.post', return_value=mock_response) as mock_post:
            result = notifier.send_critical_alert("خطأ حرج في النظام", details="فشل الاتصال بقاعدة البيانات")
            
            # التحقق من إرسال الرسالة
            assert mock_post.called
            
            # التحقق من محتوى الرسالة
            call_args = mock_post.call_args
            message_text = call_args[1]['json']['text']
            assert 'حرج' in message_text
            assert 'خطأ حرج في النظام' in message_text
            assert 'فشل الاتصال بقاعدة البيانات' in message_text
    
    def test_send_warning_alert(self, notification_system_with_valid_config):
        """اختبار إرسال تحذير"""
        notifier = notification_system_with_valid_config
        notifier.telegram_config['enabled'] = True
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'ok': True}
        
        with patch('requests.post', return_value=mock_response) as mock_post:
            result = notifier.send_warning_alert("استخدام عالٍ للذاكرة")
            
            assert mock_post.called
            call_args = mock_post.call_args
            message_text = call_args[1]['json']['text']
            assert 'تحذير' in message_text
            assert 'استخدام عالٍ للذاكرة' in message_text
    
    def test_send_info(self, notification_system_with_valid_config):
        """اختبار إرسال معلومات"""
        notifier = notification_system_with_valid_config
        notifier.telegram_config['enabled'] = True
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'ok': True}
        
        with patch('requests.post', return_value=mock_response):
            result = notifier.send_info("النظام يعمل بشكل طبيعي")
            
            assert 'telegram' in result


class TestExponentialBackoff:
    """اختبارات خاصية التأخير الأسي (exponential backoff)"""
    
    def test_exponential_backoff_delays(self, notification_system_with_valid_config):
        """اختبار أوقات التأخير الأسية بين المحاولات"""
        notifier = notification_system_with_valid_config
        notifier.telegram_config['enabled'] = True
        notifier.telegram_config['retry_attempts'] = 4
        
        sleep_times = []
        
        def mock_sleep(seconds):
            sleep_times.append(seconds)
        
        # كل المحاولات تفشل
        with patch('requests.post', side_effect=Exception("Network error")):
            with patch('time.sleep', side_effect=mock_sleep):
                result = notifier._send_telegram("اختبار التأخير")
                
                # التحقق من أوقات التأخير: 1s, 2s, 4s (2^0, 2^1, 2^2)
                assert len(sleep_times) == 3  # 4 محاولات = 3 فترات انتظار
                assert sleep_times[0] == 1  # 2^0
                assert sleep_times[1] == 2  # 2^1
                assert sleep_times[2] == 4  # 2^2


class TestEdgeCases:
    """اختبارات الحالات الحدية"""
    
    def test_notification_with_empty_message(self, notification_system_with_valid_config):
        """اختبار إرسال رسالة فارغة"""
        notifier = notification_system_with_valid_config
        notifier.telegram_config['enabled'] = True
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'ok': True}
        
        with patch('requests.post', return_value=mock_response):
            # يجب أن يعمل حتى مع رسالة فارغة
            result = notifier.send_notification("", level='info')
            # Telegram API قد يرفض الرسائل الفارغة، لكن يجب أن يتعامل النظام بدون crash
    
    def test_notification_with_very_long_message(self, notification_system_with_valid_config):
        """اختبار إرسال رسالة طويلة جداً"""
        notifier = notification_system_with_valid_config
        notifier.telegram_config['enabled'] = True
        
        # رسالة طويلة (Telegram limit is 4096 characters)
        long_message = "اختبار " * 1000  # ~7000 حرف
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'ok': True}
        
        with patch('requests.post', return_value=mock_response):
            result = notifier._send_telegram(long_message)
            # يجب أن يرسل الرسالة (Telegram API سيتعامل مع الطول)
    
    def test_notification_with_special_characters(self, notification_system_with_valid_config):
        """اختبار إرسال رسالة مع أحرف خاصة"""
        notifier = notification_system_with_valid_config
        notifier.telegram_config['enabled'] = True
        
        special_message = "اختبار <html> & \"quotes\" 'single' \n\t special chars: 🚀 ✅ ⚠️"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'ok': True}
        
        with patch('requests.post', return_value=mock_response) as mock_post:
            result = notifier._send_telegram(special_message)
            
            # التحقق من إرسال الرسالة كما هي
            assert result['success'] is True
