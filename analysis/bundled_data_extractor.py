#!/usr/bin/env python3
"""
مستخرج البيانات المحزومة - Bundled Data Extractor
يستخرج البيانات من ملفات JS المحزومة والمخفية
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

class BundledDataExtractor:
    def __init__(self, root_dir='.'):
        self.root_dir = root_dir
        self.extracted_data = {
            'next_data': [],
            'apollo_state': [],
            'firebase_configs': [],
            'stripe_configs': [],
            'gtm_configs': [],
            'api_endpoints': set(),
            'environment_vars': set(),
            'build_info': {}
        }
    
    def extract_next_data(self, content, filepath):
        """استخراج __NEXT_DATA__ من HTML"""
        patterns = [
            r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',
            r'__NEXT_DATA__\s*=\s*({.*?})\s*;',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                try:
                    data_str = match.group(1)
                    data = json.loads(data_str)
                    self.extracted_data['next_data'].append({
                        'file': os.path.basename(filepath),
                        'buildId': data.get('buildId', ''),
                        'page': data.get('page', ''),
                        'has_props': 'props' in data,
                        'has_apollo': 'apolloState' in str(data),
                        'keys': list(data.keys())
                    })
                    
                    # استخراج Apollo state إذا كان موجود
                    if 'props' in data and 'pageProps' in data['props']:
                        page_props = data['props']['pageProps']
                        if '__APOLLO_STATE__' in page_props:
                            self._extract_apollo_state(page_props['__APOLLO_STATE__'], filepath)
                
                except json.JSONDecodeError:
                    pass
    
    def _extract_apollo_state(self, apollo_state, filepath):
        """استخراج حالة Apollo"""
        if isinstance(apollo_state, dict):
            self.extracted_data['apollo_state'].append({
                'file': os.path.basename(filepath),
                'keys': list(apollo_state.keys())[:10],
                'size': len(str(apollo_state))
            })
    
    def extract_firebase_config(self, content, filepath):
        """استخراج تكوينات Firebase"""
        patterns = [
            r'apiKey\s*:\s*["\']([^"\']+)["\']',
            r'authDomain\s*:\s*["\']([^"\']+)["\']',
            r'projectId\s*:\s*["\']([^"\']+)["\']',
            r'storageBucket\s*:\s*["\']([^"\']+)["\']',
            r'messagingSenderId\s*:\s*["\']([^"\']+)["\']',
            r'appId\s*:\s*["\']([^"\']+)["\']'
        ]
        
        firebase_found = False
        config = {}
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                key = pattern.split(r'\s*:')[0].replace('\\', '')
                config[key] = match.group(1)[:20] + '...'
                firebase_found = True
        
        if firebase_found:
            self.extracted_data['firebase_configs'].append({
                'file': os.path.basename(filepath),
                'config': config
            })
    
    def extract_stripe_config(self, content, filepath):
        """استخراج تكوينات Stripe"""
        patterns = [
            r'pk_test_[a-zA-Z0-9]+',
            r'pk_live_[a-zA-Z0-9]+',
            r'Stripe\(["\']([^"\']+)["\']\)',
            r'stripePublicKey\s*[:=]\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                self.extracted_data['stripe_configs'].append({
                    'file': os.path.basename(filepath),
                    'key_type': 'publishable' if 'pk_' in match.group(0) else 'reference',
                    'value': match.group(0)[:20] + '...'
                })
    
    def extract_gtm_config(self, content, filepath):
        """استخراج تكوينات Google Tag Manager"""
        patterns = [
            r'GTM-[A-Z0-9]+',
            r'dataLayer\s*=\s*\[(.*?)\]',
            r'gtm\.start.*?GTM-[A-Z0-9]+'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                self.extracted_data['gtm_configs'].append({
                    'file': os.path.basename(filepath),
                    'match': match.group(0)[:100]
                })
    
    def extract_api_endpoints(self, content):
        """استخراج API endpoints"""
        patterns = [
            r'https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}[/a-zA-Z0-9._-]*',
            r'/api/[a-zA-Z0-9/_-]+',
            r'graphql',
            r'/v\d+/[a-zA-Z0-9/_-]+'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                url = match.group(0)
                if not any(x in url for x in ['.js', '.css', '.png', '.jpg', '.svg']):
                    self.extracted_data['api_endpoints'].add(url)
    
    def extract_environment_vars(self, content):
        """استخراج متغيرات البيئة المستخدمة"""
        patterns = [
            r'process\.env\.([A-Z_][A-Z0-9_]*)',
            r'NEXT_PUBLIC_([A-Z_][A-Z0-9_]*)',
            r'REACT_APP_([A-Z_][A-Z0-9_]*)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                self.extracted_data['environment_vars'].add(match.group(0))
    
    def extract_build_info(self, content, filepath):
        """استخراج معلومات البناء"""
        patterns = {
            'buildId': r'buildId["\']?\s*:\s*["\']([^"\']+)["\']',
            'version': r'version["\']?\s*:\s*["\']([^"\']+)["\']',
            'environment': r'NODE_ENV["\']?\s*:\s*["\']([^"\']+)["\']'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, content)
            if match:
                if key not in self.extracted_data['build_info']:
                    self.extracted_data['build_info'][key] = []
                self.extracted_data['build_info'][key].append({
                    'file': os.path.basename(filepath),
                    'value': match.group(1)
                })
    
    def analyze_file(self, filepath):
        """تحليل ملف واحد"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # استخراج جميع البيانات
                self.extract_next_data(content, filepath)
                self.extract_firebase_config(content, filepath)
                self.extract_stripe_config(content, filepath)
                self.extract_gtm_config(content, filepath)
                self.extract_api_endpoints(content)
                self.extract_environment_vars(content)
                self.extract_build_info(content, filepath)
        
        except Exception as e:
            print(f"خطأ في تحليل {filepath}: {e}")
    
    def analyze_all_files(self):
        """تحليل جميع الملفات"""
        print("🔍 استخراج البيانات المحزومة...")
        
        # تحليل ملفات HTML
        html_files = list(Path(self.root_dir).glob('**/*.html'))
        print(f"📄 تحليل {len(html_files)} ملف HTML...")
        for html_file in html_files:
            self.analyze_file(html_file)
        
        # تحليل ملفات JS
        js_files = list(Path(self.root_dir).glob('**/*.js'))
        print(f"📜 تحليل {len(js_files)} ملف JavaScript...")
        for js_file in js_files:
            self.analyze_file(js_file)
    
    def generate_report(self):
        """توليد تقرير"""
        report = {
            'summary': {
                'next_data_instances': len(self.extracted_data['next_data']),
                'apollo_states': len(self.extracted_data['apollo_state']),
                'firebase_configs': len(self.extracted_data['firebase_configs']),
                'stripe_configs': len(self.extracted_data['stripe_configs']),
                'gtm_configs': len(self.extracted_data['gtm_configs']),
                'api_endpoints': len(self.extracted_data['api_endpoints']),
                'environment_vars': len(self.extracted_data['environment_vars'])
            },
            'next_data': self.extracted_data['next_data'],
            'apollo_state': self.extracted_data['apollo_state'],
            'firebase_configs': self.extracted_data['firebase_configs'],
            'stripe_configs': self.extracted_data['stripe_configs'],
            'gtm_configs': self.extracted_data['gtm_configs'],
            'api_endpoints': sorted(list(self.extracted_data['api_endpoints']))[:50],
            'environment_vars': sorted(list(self.extracted_data['environment_vars'])),
            'build_info': self.extracted_data['build_info']
        }
        
        return report
    
    def save_report(self, output_file='analysis/bundled_data.json'):
        """حفظ التقرير"""
        report = self.generate_report()
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ تم حفظ تقرير البيانات المحزومة في: {output_file}")
        print(f"📊 Next.js Data: {report['summary']['next_data_instances']}")
        print(f"🔷 Apollo States: {report['summary']['apollo_states']}")
        print(f"🔥 Firebase Configs: {report['summary']['firebase_configs']}")
        print(f"💳 Stripe Configs: {report['summary']['stripe_configs']}")
        print(f"📊 GTM Configs: {report['summary']['gtm_configs']}")
        print(f"🌐 API Endpoints: {report['summary']['api_endpoints']}")
        print(f"⚙️ Environment Vars: {report['summary']['environment_vars']}")
        
        return report

def main():
    extractor = BundledDataExtractor()
    extractor.analyze_all_files()
    extractor.save_report()

if __name__ == '__main__':
    main()
