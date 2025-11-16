#!/usr/bin/env python3
"""
مستخرج script tags - Script Tag Extractor
يستخرج جميع script tags ويحلل تكويناتها بدقة
"""

import os
import re
import json
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from collections import defaultdict

class ScriptTagExtractor:
    def __init__(self, static_dir='.'):
        self.static_dir = static_dir
        self.script_data = {
            'external_scripts': [],
            'inline_scripts': [],
            'config_objects': [],
            'api_endpoints': [],
            'third_party_services': defaultdict(list)
        }
    
    def extract_from_html(self, filepath):
        """استخراج جميع scripts من HTML"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                
                # استخراج external scripts
                for script in soup.find_all('script', src=True):
                    self._process_external_script(script, filepath)
                
                # استخراج inline scripts
                for script in soup.find_all('script', src=False):
                    self._process_inline_script(script, filepath)
                
                # استخراج config objects من صفحة
                self._extract_config_objects(soup, filepath)
        
        except Exception as e:
            print(f"خطأ في معالجة {filepath}: {e}")
    
    def _process_external_script(self, script, filepath):
        """معالجة external script tag"""
        src = script.get('src', '')
        if not src:
            return
        
        # تحليل URL
        parsed = urlparse(src)
        domain = parsed.netloc or 'local'
        
        script_info = {
            'file': os.path.basename(filepath),
            'src': src,
            'domain': domain,
            'path': parsed.path,
            'async': script.has_attr('async'),
            'defer': script.has_attr('defer'),
            'type': script.get('type', 'text/javascript'),
            'integrity': script.get('integrity', ''),
            'crossorigin': script.get('crossorigin', '')
        }
        
        self.script_data['external_scripts'].append(script_info)
        
        # تصنيف الخدمة
        service = self._identify_service(domain, src)
        if service:
            self.script_data['third_party_services'][service].append(script_info)
    
    def _process_inline_script(self, script, filepath):
        """معالجة inline script"""
        content = script.string or ''
        if not content.strip():
            return
        
        script_info = {
            'file': os.path.basename(filepath),
            'length': len(content),
            'type': script.get('type', 'text/javascript'),
            'has_config': self._contains_configuration(content),
            'snippet': content[:500].strip()
        }
        
        # استخراج API calls
        api_calls = self._extract_api_calls(content)
        if api_calls:
            script_info['api_calls'] = api_calls
            self.script_data['api_endpoints'].extend(api_calls)
        
        # استخراج configurations
        configs = self._extract_configurations(content)
        if configs:
            script_info['configurations'] = configs
        
        self.script_data['inline_scripts'].append(script_info)
    
    def _extract_config_objects(self, soup, filepath):
        """استخراج configuration objects"""
        # البحث عن __NEXT_DATA__
        next_data_scripts = soup.find_all('script', id='__NEXT_DATA__')
        for script in next_data_scripts:
            try:
                data = json.loads(script.string or '{}')
                self.script_data['config_objects'].append({
                    'file': os.path.basename(filepath),
                    'type': 'Next.js Data',
                    'has_props': 'props' in data,
                    'has_apollo_state': 'apolloState' in str(data),
                    'build_id': data.get('buildId', ''),
                    'page': data.get('page', '')
                })
            except json.JSONDecodeError:
                pass
        
        # البحث عن dataLayer (GTM)
        for script in soup.find_all('script'):
            content = script.string or ''
            if 'dataLayer' in content:
                self.script_data['config_objects'].append({
                    'file': os.path.basename(filepath),
                    'type': 'Google Tag Manager DataLayer',
                    'snippet': self._extract_datalayer_config(content)
                })
    
    def _extract_datalayer_config(self, content):
        """استخراج تكوين dataLayer"""
        match = re.search(r'dataLayer\s*=\s*(\[.*?\])', content, re.DOTALL)
        if match:
            return match.group(1)[:500]
        return ''
    
    def _contains_configuration(self, content):
        """فحص إذا كان السكريبت يحتوي على تكوينات"""
        config_patterns = [
            r'config\s*=\s*{',
            r'settings\s*=\s*{',
            r'options\s*=\s*{',
            r'init\(',
            r'configure\(',
            r'apiKey\s*:',
            r'projectId\s*:'
        ]
        
        for pattern in config_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False
    
    def _extract_api_calls(self, content):
        """استخراج API calls من السكريبت"""
        api_calls = []
        
        # patterns لـ API calls
        patterns = [
            r'fetch\([\'"]([^\'"]+)[\'"]',
            r'axios\.[a-z]+\([\'"]([^\'"]+)[\'"]',
            r'\.get\([\'"]([^\'"]+)[\'"]',
            r'\.post\([\'"]([^\'"]+)[\'"]',
            r'XMLHttpRequest.*?open\([\'"][A-Z]+[\'"],\s*[\'"]([^\'"]+)[\'"]'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                url = match.group(1)
                if url.startswith('http') or url.startswith('//'):
                    api_calls.append(url)
        
        return list(set(api_calls))
    
    def _extract_configurations(self, content):
        """استخراج تكوينات من السكريبت"""
        configs = []
        
        # استخراج API keys (مخفية)
        api_key_patterns = [
            r'apiKey\s*:\s*[\'"]([^\'"]+)[\'"]',
            r'api_key\s*=\s*[\'"]([^\'"]+)[\'"]',
            r'key\s*:\s*[\'"]([^\'"]+)[\'"]'
        ]
        
        for pattern in api_key_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                key = match.group(1)
                # إخفاء المفتاح
                configs.append({
                    'type': 'API Key',
                    'value': key[:10] + '...' if len(key) > 10 else key
                })
        
        # استخراج project IDs
        project_patterns = [
            r'projectId\s*:\s*[\'"]([^\'"]+)[\'"]',
            r'project_id\s*=\s*[\'"]([^\'"]+)[\'"]'
        ]
        
        for pattern in project_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                configs.append({
                    'type': 'Project ID',
                    'value': match.group(1)
                })
        
        return configs
    
    def _identify_service(self, domain, src):
        """تحديد الخدمة من domain"""
        services = {
            'googletagmanager.com': 'Google Tag Manager',
            'google-analytics.com': 'Google Analytics',
            'amplitude.com': 'Amplitude',
            'segment.com': 'Segment',
            'cdn.segment.com': 'Segment',
            'stripe.com': 'Stripe',
            'js.stripe.com': 'Stripe',
            'firebase.google.com': 'Firebase',
            'firebaseapp.com': 'Firebase',
            'cdn.sanity.io': 'Sanity CMS',
            'launchdarkly.com': 'LaunchDarkly',
            'statsig.com': 'Statsig',
            'datadoghq.com': 'Datadog',
            'coframe.ai': 'Coframe',
            'hotjar.com': 'Hotjar',
            'intercom.io': 'Intercom',
            'sentry.io': 'Sentry',
            'mixpanel.com': 'Mixpanel',
            'facebook.net': 'Facebook Pixel',
            'connect.facebook.net': 'Facebook Pixel',
            'appsflyer.com': 'AppsFlyer',
            'recaptcha': 'reCAPTCHA',
            'gstatic.com': 'Google Static Assets'
        }
        
        for key, service in services.items():
            if key in domain or key in src:
                return service
        
        return None
    
    def analyze_all_files(self):
        """تحليل جميع ملفات HTML"""
        print("🔍 استخراج script tags من جميع الملفات...")
        
        html_files = list(Path(self.static_dir).glob('**/*.html'))
        print(f"📄 معالجة {len(html_files)} ملف HTML...")
        
        for html_file in html_files:
            self.extract_from_html(html_file)
    
    def generate_report(self):
        """توليد تقرير مفصل"""
        report = {
            'summary': {
                'total_external_scripts': len(self.script_data['external_scripts']),
                'total_inline_scripts': len(self.script_data['inline_scripts']),
                'total_config_objects': len(self.script_data['config_objects']),
                'total_api_endpoints': len(self.script_data['api_endpoints']),
                'total_services': len(self.script_data['third_party_services'])
            },
            'external_scripts': self.script_data['external_scripts'],
            'inline_scripts': self.script_data['inline_scripts'],
            'config_objects': self.script_data['config_objects'],
            'api_endpoints': list(set(self.script_data['api_endpoints'])),
            'third_party_services': dict(self.script_data['third_party_services'])
        }
        
        return report
    
    def save_report(self, output_file='analysis/script_tags_report.json'):
        """حفظ التقرير"""
        report = self.generate_report()
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ تم حفظ تقرير script tags في: {output_file}")
        print(f"📊 External Scripts: {report['summary']['total_external_scripts']}")
        print(f"📜 Inline Scripts: {report['summary']['total_inline_scripts']}")
        print(f"⚙️ Config Objects: {report['summary']['total_config_objects']}")
        print(f"🌐 API Endpoints: {report['summary']['total_api_endpoints']}")
        print(f"🔌 Third Party Services: {report['summary']['total_services']}")
        
        return report

def main():
    extractor = ScriptTagExtractor()
    extractor.analyze_all_files()
    report = extractor.save_report()
    
    print("\n" + "="*60)
    print("🔌 الخدمات الخارجية المكتشفة:")
    print("="*60)
    for service, scripts in report['third_party_services'].items():
        print(f"✓ {service}: {len(scripts)} script(s)")

if __name__ == '__main__':
    main()
