#!/usr/bin/env python3
"""
محلل متقدم للأنظمة - Deep System Analyzer
يقوم بفحص دقيق لملفات HTML/JS لاستخراج جميع الأنظمة والتكاملات
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict
from bs4 import BeautifulSoup

class DeepSystemAnalyzer:
    def __init__(self, static_dir='.'):
        self.static_dir = static_dir
        self.systems = defaultdict(lambda: {
            'evidence': [],
            'script_tags': [],
            'api_calls': [],
            'configurations': [],
            'integrations': []
        })
        
        # قاموس شامل للأنظمة المعروفة مع patterns للكشف عنها
        self.known_systems = {
            'Google Tag Manager': {
                'patterns': [r'googletagmanager\.com/gtm\.js', r'GTM-[A-Z0-9]+', r'dataLayer'],
                'script_domains': ['googletagmanager.com'],
                'type': 'Analytics & Tag Management'
            },
            'Google Analytics 4': {
                'patterns': [r'google-analytics\.com/analytics\.js', r'gtag\(', r'G-[A-Z0-9]+', r'GA_MEASUREMENT_ID'],
                'script_domains': ['google-analytics.com', 'googletagmanager.com'],
                'type': 'Analytics'
            },
            'Amplitude': {
                'patterns': [r'amplitude\.com', r'amplitude\.getInstance', r'amplitude\.init'],
                'script_domains': ['amplitude.com', 'cdn.amplitude.com'],
                'type': 'Product Analytics'
            },
            'Segment': {
                'patterns': [r'segment\.com', r'analytics\.js', r'analytics\.identify', r'analytics\.track'],
                'script_domains': ['segment.com', 'cdn.segment.com'],
                'type': 'Customer Data Platform'
            },
            'reCAPTCHA': {
                'patterns': [r'recaptcha', r'google\.com/recaptcha', r'grecaptcha'],
                'script_domains': ['google.com/recaptcha', 'gstatic.com/recaptcha'],
                'type': 'Security & Bot Protection'
            },
            'Datadog RUM': {
                'patterns': [r'datadoghq\.com', r'DD_RUM', r'datadogRum'],
                'script_domains': ['datadoghq.com', 'datadoghq-browser-agent'],
                'type': 'Real User Monitoring'
            },
            'Firebase': {
                'patterns': [r'firebase', r'firebaseapp\.com', r'firestore', r'__firebase'],
                'script_domains': ['firebase.google.com', 'firebaseapp.com'],
                'type': 'Backend as a Service'
            },
            'Stripe': {
                'patterns': [r'stripe\.com/v3', r'Stripe\(', r'stripe\.js'],
                'script_domains': ['js.stripe.com'],
                'type': 'Payment Processing'
            },
            'Apollo GraphQL': {
                'patterns': [r'apolloState', r'__APOLLO_STATE__', r'apollo-client'],
                'script_domains': [],
                'type': 'GraphQL Client'
            },
            'Next.js': {
                'patterns': [r'__NEXT_DATA__', r'_next/static', r'nextjs'],
                'script_domains': [],
                'type': 'React Framework'
            },
            'Sanity CMS': {
                'patterns': [r'cdn\.sanity\.io', r'sanity\.io', r'sanityClient'],
                'script_domains': ['cdn.sanity.io'],
                'type': 'Headless CMS'
            },
            'Cloudflare': {
                'patterns': [r'cloudflare', r'cdn-cgi', r'__cflb', r'cf-ray'],
                'script_domains': ['cloudflare.com'],
                'type': 'CDN & Security'
            },
            'LaunchDarkly': {
                'patterns': [r'launchdarkly', r'ldclient', r'ld-client'],
                'script_domains': ['launchdarkly.com'],
                'type': 'Feature Flags'
            },
            'Statsig': {
                'patterns': [r'statsig', r'statsigSDK'],
                'script_domains': ['statsig.com'],
                'type': 'Experimentation Platform'
            },
            'Coframe': {
                'patterns': [r'coframe', r'Coframe watcher'],
                'script_domains': ['coframe.ai'],
                'type': 'AI Optimization'
            },
            'Webflow': {
                'patterns': [r'data-wf-', r'webflow\.js', r'webflow\.io'],
                'script_domains': ['webflow.com', 'webflow.io'],
                'type': 'Website Builder'
            },
            'AppsFlyer': {
                'patterns': [r'appsflyer', r'AF_SMART_SCRIPT'],
                'script_domains': ['appsflyer.com'],
                'type': 'Mobile Attribution'
            },
            'Hotjar': {
                'patterns': [r'hotjar', r'hj\(', r'_hjSettings'],
                'script_domains': ['hotjar.com'],
                'type': 'User Behavior Analytics'
            },
            'Intercom': {
                'patterns': [r'intercom', r'Intercom\(', r'intercomSettings'],
                'script_domains': ['intercom.io'],
                'type': 'Customer Messaging'
            },
            'Sentry': {
                'patterns': [r'sentry\.io', r'Sentry\.init', r'@sentry'],
                'script_domains': ['sentry.io'],
                'type': 'Error Tracking'
            },
            'Mixpanel': {
                'patterns': [r'mixpanel', r'mixpanel\.init', r'mixpanel\.track'],
                'script_domains': ['mixpanel.com'],
                'type': 'Product Analytics'
            },
            'Facebook Pixel': {
                'patterns': [r'fbq\(', r'facebook\.net', r'connect\.facebook'],
                'script_domains': ['facebook.net', 'connect.facebook.net'],
                'type': 'Marketing Analytics'
            },
            'LinkedIn Insight': {
                'patterns': [r'linkedin\.com/px', r'_linkedin_partner_id'],
                'script_domains': ['linkedin.com'],
                'type': 'Marketing Analytics'
            },
            'Twitter Pixel': {
                'patterns': [r'twitter\.com/i/adsct', r'twq\('],
                'script_domains': ['twitter.com'],
                'type': 'Marketing Analytics'
            }
        }
    
    def analyze_html_file(self, filepath):
        """تحليل ملف HTML واستخراج المعلومات"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                soup = BeautifulSoup(content, 'html.parser')
                
                # استخراج جميع script tags
                scripts = soup.find_all('script')
                for script in scripts:
                    src = script.get('src', '')
                    script_content = script.string or ''
                    
                    # فحص كل نظام معروف
                    for system_name, system_info in self.known_systems.items():
                        # فحص script src
                        if src:
                            for domain in system_info['script_domains']:
                                if domain in src:
                                    self.systems[system_name]['script_tags'].append({
                                        'file': os.path.basename(filepath),
                                        'src': src,
                                        'type': 'external'
                                    })
                        
                        # فحص محتوى السكريبت
                        if script_content:
                            for pattern in system_info['patterns']:
                                if re.search(pattern, script_content, re.IGNORECASE):
                                    self.systems[system_name]['evidence'].append({
                                        'file': os.path.basename(filepath),
                                        'pattern': pattern,
                                        'context': self._extract_context(script_content, pattern)
                                    })
                
                # فحص محتوى HTML الكامل
                for system_name, system_info in self.known_systems.items():
                    for pattern in system_info['patterns']:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            self.systems[system_name]['configurations'].append({
                                'file': os.path.basename(filepath),
                                'pattern': pattern,
                                'match': match.group(0),
                                'context': self._extract_context(content, pattern, match.start())
                            })
        
        except Exception as e:
            print(f"خطأ في تحليل {filepath}: {e}")
    
    def _extract_context(self, content, pattern, pos=None, context_length=200):
        """استخراج السياق المحيط بالنمط"""
        if pos is None:
            match = re.search(pattern, content, re.IGNORECASE)
            if not match:
                return ""
            pos = match.start()
        
        start = max(0, pos - context_length)
        end = min(len(content), pos + context_length)
        context = content[start:end]
        
        # تنظيف السياق
        context = ' '.join(context.split())
        return context[:500]
    
    def analyze_js_file(self, filepath):
        """تحليل ملف JavaScript"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # البحث عن API calls
                api_patterns = [
                    r'fetch\([\'"]([^\'"]+)[\'"]',
                    r'axios\.[a-z]+\([\'"]([^\'"]+)[\'"]',
                    r'\.get\([\'"]([^\'"]+)[\'"]',
                    r'\.post\([\'"]([^\'"]+)[\'"]',
                ]
                
                for pattern in api_patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        url = match.group(1)
                        # تحديد النظام بناءً على URL
                        for system_name, system_info in self.known_systems.items():
                            for domain in system_info['script_domains']:
                                if domain in url:
                                    self.systems[system_name]['api_calls'].append({
                                        'file': os.path.basename(filepath),
                                        'url': url,
                                        'method': self._extract_http_method(pattern)
                                    })
        
        except Exception as e:
            print(f"خطأ في تحليل {filepath}: {e}")
    
    def _extract_http_method(self, pattern):
        """استخراج HTTP method من النمط"""
        if 'post' in pattern.lower():
            return 'POST'
        elif 'get' in pattern.lower():
            return 'GET'
        else:
            return 'FETCH'
    
    def analyze_all_files(self):
        """تحليل جميع الملفات في المجلد"""
        print("🔍 بدء التحليل المتقدم للأنظمة...")
        
        static_path = Path(self.static_dir)
        
        # تحليل ملفات HTML
        html_files = list(static_path.glob('**/*.html'))
        print(f"📄 تحليل {len(html_files)} ملف HTML...")
        for html_file in html_files:
            self.analyze_html_file(html_file)
        
        # تحليل ملفات JS
        js_files = list(static_path.glob('**/*.js'))
        print(f"📜 تحليل {len(js_files)} ملف JavaScript...")
        for js_file in js_files:
            self.analyze_js_file(js_file)
    
    def identify_integrations(self):
        """تحديد التكاملات بين الأنظمة"""
        print("\n🔗 تحديد التكاملات بين الأنظمة...")
        
        integrations = []
        
        # GTM يتكامل مع معظم أدوات Analytics
        if 'Google Tag Manager' in self.systems and self.systems['Google Tag Manager']['evidence']:
            for system in ['Google Analytics 4', 'Facebook Pixel', 'LinkedIn Insight', 'Twitter Pixel']:
                if system in self.systems and self.systems[system]['evidence']:
                    integrations.append({
                        'from': 'Google Tag Manager',
                        'to': system,
                        'type': 'Tag Management',
                        'description': f'GTM يدير tags لـ {system}'
                    })
        
        # Segment يوزع البيانات على أدوات Analytics
        if 'Segment' in self.systems and self.systems['Segment']['evidence']:
            for system in ['Amplitude', 'Mixpanel', 'Google Analytics 4']:
                if system in self.systems and self.systems[system]['evidence']:
                    integrations.append({
                        'from': 'Segment',
                        'to': system,
                        'type': 'Data Pipeline',
                        'description': f'Segment يرسل بيانات إلى {system}'
                    })
        
        # Next.js يتكامل مع Apollo GraphQL
        if 'Next.js' in self.systems and 'Apollo GraphQL' in self.systems:
            if self.systems['Next.js']['evidence'] and self.systems['Apollo GraphQL']['evidence']:
                integrations.append({
                    'from': 'Next.js',
                    'to': 'Apollo GraphQL',
                    'type': 'Data Fetching',
                    'description': 'Next.js يستخدم Apollo لجلب البيانات'
                })
        
        # Firebase للمصادقة
        if 'Firebase' in self.systems and 'Next.js' in self.systems:
            if self.systems['Firebase']['evidence'] and self.systems['Next.js']['evidence']:
                integrations.append({
                    'from': 'Next.js',
                    'to': 'Firebase',
                    'type': 'Authentication',
                    'description': 'Next.js يستخدم Firebase للمصادقة'
                })
        
        return integrations
    
    def generate_report(self):
        """توليد تقرير شامل"""
        print("\n📊 توليد التقرير...")
        
        # تنظيف البيانات - إزالة الأنظمة التي لا توجد أدلة عليها
        verified_systems = {}
        for system_name, system_data in self.systems.items():
            total_evidence = (
                len(system_data['evidence']) +
                len(system_data['script_tags']) +
                len(system_data['api_calls']) +
                len(system_data['configurations'])
            )
            
            if total_evidence > 0:
                verified_systems[system_name] = {
                    'type': self.known_systems[system_name]['type'],
                    'evidence_count': total_evidence,
                    'script_tags': system_data['script_tags'],
                    'evidence': system_data['evidence'][:5],  # أول 5 أدلة
                    'api_calls': system_data['api_calls'][:5],
                    'configurations': system_data['configurations'][:5]
                }
        
        integrations = self.identify_integrations()
        
        report = {
            'summary': {
                'total_systems_detected': len(verified_systems),
                'total_integrations': len(integrations),
                'analysis_date': '2025-11-16'
            },
            'systems': verified_systems,
            'integrations': integrations
        }
        
        return report
    
    def save_report(self, output_file='analysis/verified_systems.json'):
        """حفظ التقرير"""
        report = self.generate_report()
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ تم حفظ التقرير في: {output_file}")
        print(f"📈 عدد الأنظمة المكتشفة: {report['summary']['total_systems_detected']}")
        print(f"🔗 عدد التكاملات: {report['summary']['total_integrations']}")
        
        return report

def main():
    analyzer = DeepSystemAnalyzer()
    analyzer.analyze_all_files()
    report = analyzer.save_report()
    
    # طباعة ملخص
    print("\n" + "="*60)
    print("📋 ملخص الأنظمة المكتشفة:")
    print("="*60)
    for system_name, system_data in report['systems'].items():
        print(f"✓ {system_name} ({system_data['type']}) - {system_data['evidence_count']} دليل")
    
    print("\n" + "="*60)
    print("🔗 التكاملات المكتشفة:")
    print("="*60)
    for integration in report['integrations']:
        print(f"• {integration['from']} → {integration['to']} ({integration['type']})")

if __name__ == '__main__':
    main()
