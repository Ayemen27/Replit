#!/usr/bin/env python3
"""
مولد خطة إعادة البناء - Rebuild Plan Generator
يولد خطة تفصيلية لإعادة بناء النظام الأصلي بالضبط
"""

import json
import os
from pathlib import Path

class RebuildPlanGenerator:
    def __init__(self):
        self.systems = {}
        self.integrations = []
        self.rebuild_plan = {
            'phases': [],
            'dependencies': {},
            'implementation_steps': {},
            'configuration_requirements': {},
            'api_integrations': {}
        }
        
        # خريطة إعادة البناء لكل نظام
        self.system_rebuild_map = {
            'Next.js': {
                'priority': 1,
                'category': 'Frontend Framework',
                'install_command': 'npx create-next-app@latest',
                'dependencies': ['react', 'react-dom', 'next'],
                'configuration_files': [
                    'next.config.js',
                    'tsconfig.json',
                    'package.json'
                ],
                'setup_steps': [
                    'تثبيت Next.js مع TypeScript',
                    'إعداد routing structure',
                    'إعداد API routes',
                    'تكوين SSR/SSG',
                    'إعداد _app.js و _document.js'
                ],
                'code_structure': {
                    'pages/': 'صفحات التطبيق',
                    'components/': 'مكونات React',
                    'public/': 'الملفات الثابتة',
                    'styles/': 'ملفات CSS',
                    'lib/': 'مكتبات مساعدة'
                }
            },
            'Apollo GraphQL': {
                'priority': 2,
                'category': 'Data Layer',
                'install_command': 'npm install @apollo/client graphql',
                'dependencies': ['@apollo/client', 'graphql'],
                'configuration_files': ['apollo-client.js', 'schema.graphql'],
                'setup_steps': [
                    'تثبيت Apollo Client',
                    'إنشاء Apollo Client instance',
                    'تكوين cache',
                    'ربط مع Next.js',
                    'إعداد queries و mutations'
                ],
                'code_examples': {
                    'client_setup': '''
import { ApolloClient, InMemoryCache, HttpLink } from '@apollo/client';

const client = new ApolloClient({
  link: new HttpLink({
    uri: process.env.NEXT_PUBLIC_GRAPHQL_ENDPOINT,
  }),
  cache: new InMemoryCache()
});
'''
                }
            },
            'Firebase': {
                'priority': 3,
                'category': 'Authentication & Database',
                'install_command': 'npm install firebase',
                'dependencies': ['firebase'],
                'configuration_files': ['firebase.config.js', '.env.local'],
                'setup_steps': [
                    'إنشاء مشروع Firebase',
                    'تفعيل Authentication (Email, Google, GitHub)',
                    'إعداد Firestore Database',
                    'تكوين Security Rules',
                    'ربط مع Next.js'
                ],
                'environment_variables': [
                    'NEXT_PUBLIC_FIREBASE_API_KEY',
                    'NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN',
                    'NEXT_PUBLIC_FIREBASE_PROJECT_ID',
                    'NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET',
                    'NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID',
                    'NEXT_PUBLIC_FIREBASE_APP_ID'
                ]
            },
            'Google Tag Manager': {
                'priority': 4,
                'category': 'Analytics & Tracking',
                'install_command': 'تثبيت عبر script tag',
                'dependencies': [],
                'configuration_files': ['_app.js', '_document.js'],
                'setup_steps': [
                    'إنشاء حساب GTM',
                    'الحصول على GTM ID (GTM-XXXXXX)',
                    'إضافة GTM script في _document.js',
                    'إعداد dataLayer',
                    'تكوين tags و triggers'
                ],
                'code_examples': {
                    'gtm_script': '''
<script
  dangerouslySetInnerHTML={{
    __html: `
      (function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
      new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
      j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
      'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
      })(window,document,'script','dataLayer','GTM-XXXXXX');
    `,
  }}
/>
'''
                }
            },
            'Google Analytics 4': {
                'priority': 5,
                'category': 'Analytics',
                'install_command': 'إعداد عبر GTM أو script مباشر',
                'dependencies': [],
                'setup_steps': [
                    'إنشاء خاصية GA4',
                    'الحصول على Measurement ID (G-XXXXXXXXXX)',
                    'إعداد عبر GTM أو script مباشر',
                    'تكوين events',
                    'ربط مع Firebase (اختياري)'
                ]
            },
            'Segment': {
                'priority': 6,
                'category': 'Customer Data Platform',
                'install_command': 'npm install @segment/analytics-next',
                'dependencies': ['@segment/analytics-next'],
                'setup_steps': [
                    'إنشاء حساب Segment',
                    'الحصول على Write Key',
                    'تثبيت Segment SDK',
                    'إعداد destinations (GA, Amplitude, etc)',
                    'تنفيذ tracking events'
                ],
                'environment_variables': ['NEXT_PUBLIC_SEGMENT_WRITE_KEY']
            },
            'Amplitude': {
                'priority': 7,
                'category': 'Product Analytics',
                'install_command': 'npm install @amplitude/analytics-browser',
                'dependencies': ['@amplitude/analytics-browser'],
                'setup_steps': [
                    'إنشاء مشروع Amplitude',
                    'الحصول على API Key',
                    'تثبيت SDK',
                    'تكوين user identification',
                    'تتبع events'
                ],
                'environment_variables': ['NEXT_PUBLIC_AMPLITUDE_API_KEY']
            },
            'Stripe': {
                'priority': 8,
                'category': 'Payments',
                'install_command': 'npm install @stripe/stripe-js stripe',
                'dependencies': ['@stripe/stripe-js', 'stripe'],
                'setup_steps': [
                    'إنشاء حساب Stripe',
                    'الحصول على API keys (publishable & secret)',
                    'تثبيت Stripe.js',
                    'إنشاء Products و Prices',
                    'إعداد Checkout Session',
                    'معالجة Webhooks'
                ],
                'environment_variables': [
                    'NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY',
                    'STRIPE_SECRET_KEY',
                    'STRIPE_WEBHOOK_SECRET'
                ]
            },
            'Datadog': {
                'priority': 9,
                'category': 'Monitoring',
                'install_command': 'npm install @datadog/browser-rum',
                'dependencies': ['@datadog/browser-rum'],
                'setup_steps': [
                    'إنشاء حساب Datadog',
                    'إنشاء RUM Application',
                    'الحصول على Client Token و Application ID',
                    'تثبيت RUM SDK',
                    'تكوين tracking'
                ],
                'environment_variables': [
                    'NEXT_PUBLIC_DATADOG_CLIENT_TOKEN',
                    'NEXT_PUBLIC_DATADOG_APPLICATION_ID'
                ]
            },
            'Sanity CMS': {
                'priority': 10,
                'category': 'Content Management',
                'install_command': 'npm install @sanity/client next-sanity',
                'dependencies': ['@sanity/client', 'next-sanity'],
                'setup_steps': [
                    'إنشاء مشروع Sanity',
                    'إعداد schemas',
                    'الحصول على Project ID و Dataset',
                    'تكوين Sanity Client',
                    'إعداد GROQ queries'
                ],
                'environment_variables': [
                    'NEXT_PUBLIC_SANITY_PROJECT_ID',
                    'NEXT_PUBLIC_SANITY_DATASET',
                    'SANITY_API_TOKEN'
                ]
            },
            'Cloudflare': {
                'priority': 11,
                'category': 'CDN & Security',
                'install_command': 'إعداد على مستوى DNS/Hosting',
                'dependencies': [],
                'setup_steps': [
                    'إنشاء حساب Cloudflare',
                    'إضافة النطاق',
                    'تحديث nameservers',
                    'تفعيل Proxy',
                    'تكوين caching rules',
                    'إعداد SSL/TLS'
                ]
            },
            'LaunchDarkly': {
                'priority': 12,
                'category': 'Feature Flags',
                'install_command': 'npm install launchdarkly-react-client-sdk',
                'dependencies': ['launchdarkly-react-client-sdk'],
                'setup_steps': [
                    'إنشاء حساب LaunchDarkly',
                    'إنشاء project و environment',
                    'الحصول على Client-side ID',
                    'تثبيت SDK',
                    'إعداد feature flags'
                ],
                'environment_variables': ['NEXT_PUBLIC_LAUNCHDARKLY_CLIENT_ID']
            },
            'reCAPTCHA': {
                'priority': 13,
                'category': 'Security',
                'install_command': 'npm install react-google-recaptcha',
                'dependencies': ['react-google-recaptcha'],
                'setup_steps': [
                    'التسجيل في Google reCAPTCHA',
                    'الحصول على Site Key و Secret Key',
                    'إضافة reCAPTCHA component',
                    'التحقق من token في backend'
                ],
                'environment_variables': [
                    'NEXT_PUBLIC_RECAPTCHA_SITE_KEY',
                    'RECAPTCHA_SECRET_KEY'
                ]
            }
        }
    
    def load_analysis_results(self):
        """تحميل نتائج التحليل"""
        try:
            with open('analysis/verified_systems.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.systems = data.get('systems', {})
                self.integrations = data.get('integrations', [])
        except FileNotFoundError:
            print("⚠️ لم يتم العثور على ملف verified_systems.json")
    
    def generate_phases(self):
        """توليد مراحل إعادة البناء"""
        phases = [
            {
                'phase': 1,
                'name': 'إعداد البنية التحتية الأساسية',
                'duration': '1-2 أيام',
                'systems': ['Next.js', 'Cloudflare'],
                'description': 'إنشاء المشروع الأساسي وإعداد CDN'
            },
            {
                'phase': 2,
                'name': 'إعداد طبقة البيانات',
                'duration': '2-3 أيام',
                'systems': ['Apollo GraphQL', 'Firebase'],
                'description': 'إعداد GraphQL وقاعدة البيانات والمصادقة'
            },
            {
                'phase': 3,
                'name': 'إدارة المحتوى',
                'duration': '1-2 أيام',
                'systems': ['Sanity CMS'],
                'description': 'إعداد نظام إدارة المحتوى'
            },
            {
                'phase': 4,
                'name': 'Analytics والتتبع',
                'duration': '2-3 أيام',
                'systems': ['Google Tag Manager', 'Google Analytics 4', 'Segment', 'Amplitude'],
                'description': 'إعداد جميع أدوات التحليل والتتبع'
            },
            {
                'phase': 5,
                'name': 'المدفوعات والأمان',
                'duration': '2-3 أيام',
                'systems': ['Stripe', 'reCAPTCHA'],
                'description': 'إعداد نظام المدفوعات والحماية'
            },
            {
                'phase': 6,
                'name': 'المراقبة وإدارة الميزات',
                'duration': '1-2 أيام',
                'systems': ['Datadog', 'LaunchDarkly'],
                'description': 'إعداد المراقبة وإدارة الميزات'
            },
            {
                'phase': 7,
                'name': 'الاختبار والتحسين',
                'duration': '3-5 أيام',
                'systems': 'جميع الأنظمة',
                'description': 'اختبار شامل وتحسين الأداء'
            }
        ]
        
        self.rebuild_plan['phases'] = phases
    
    def generate_implementation_steps(self):
        """توليد خطوات التنفيذ التفصيلية"""
        for system_name in self.systems.keys():
            if system_name in self.system_rebuild_map:
                self.rebuild_plan['implementation_steps'][system_name] = self.system_rebuild_map[system_name]
    
    def generate_dependencies_graph(self):
        """توليد مخطط التبعيات"""
        dependencies = {
            'Next.js': [],
            'Apollo GraphQL': ['Next.js'],
            'Firebase': ['Next.js'],
            'Google Tag Manager': ['Next.js'],
            'Google Analytics 4': ['Google Tag Manager'],
            'Segment': ['Next.js'],
            'Amplitude': ['Segment'],
            'Stripe': ['Next.js', 'Firebase'],
            'Sanity CMS': ['Next.js'],
            'Datadog': ['Next.js'],
            'LaunchDarkly': ['Next.js'],
            'reCAPTCHA': ['Next.js']
        }
        
        self.rebuild_plan['dependencies'] = dependencies
    
    def generate_environment_config(self):
        """توليد متطلبات التكوين"""
        all_env_vars = {}
        
        for system_name, system_info in self.system_rebuild_map.items():
            if 'environment_variables' in system_info:
                all_env_vars[system_name] = system_info['environment_variables']
        
        self.rebuild_plan['configuration_requirements'] = all_env_vars
    
    def generate_api_integrations_guide(self):
        """توليد دليل التكاملات"""
        integrations_guide = {}
        
        for integration in self.integrations:
            key = f"{integration['from']} → {integration['to']}"
            integrations_guide[key] = {
                'type': integration['type'],
                'description': integration['description'],
                'implementation': self._get_integration_implementation(integration)
            }
        
        self.rebuild_plan['api_integrations'] = integrations_guide
    
    def _get_integration_implementation(self, integration):
        """الحصول على تفاصيل تنفيذ التكامل"""
        implementations = {
            'Tag Management': 'إعداد tags في GTM Dashboard وربطها بـ dataLayer events',
            'Data Pipeline': 'تكوين destination في Segment Dashboard',
            'Data Fetching': 'استخدام Apollo hooks في Next.js components',
            'Authentication': 'استخدام Firebase Auth مع Next.js API routes'
        }
        
        return implementations.get(integration['type'], 'راجع الوثائق الرسمية')
    
    def generate_full_plan(self):
        """توليد الخطة الكاملة"""
        print("📋 توليد خطة إعادة البناء الكاملة...")
        
        self.load_analysis_results()
        self.generate_phases()
        self.generate_implementation_steps()
        self.generate_dependencies_graph()
        self.generate_environment_config()
        self.generate_api_integrations_guide()
        
        # إضافة ملخص
        self.rebuild_plan['summary'] = {
            'total_systems': len(self.systems),
            'total_phases': len(self.rebuild_plan['phases']),
            'estimated_duration': '12-20 يوم عمل',
            'team_size': '2-3 مطورين',
            'complexity': 'متوسط إلى عالي'
        }
    
    def save_plan(self, output_file='analysis/rebuild_plan.json'):
        """حفظ الخطة"""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.rebuild_plan, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ تم حفظ خطة إعادة البناء في: {output_file}")
        print(f"📊 عدد الأنظمة: {self.rebuild_plan['summary']['total_systems']}")
        print(f"📅 المدة المقدرة: {self.rebuild_plan['summary']['estimated_duration']}")
        print(f"👥 حجم الفريق: {self.rebuild_plan['summary']['team_size']}")
    
    def generate_markdown_documentation(self):
        """توليد وثائق Markdown"""
        md_content = f"""# 📘 خطة إعادة بناء النظام الأصلي

## 📊 ملخص المشروع

- **عدد الأنظمة**: {self.rebuild_plan['summary']['total_systems']}
- **عدد المراحل**: {self.rebuild_plan['summary']['total_phases']}
- **المدة المقدرة**: {self.rebuild_plan['summary']['estimated_duration']}
- **حجم الفريق**: {self.rebuild_plan['summary']['team_size']}
- **مستوى التعقيد**: {self.rebuild_plan['summary']['complexity']}

---

## 🎯 المراحل

"""
        
        for phase in self.rebuild_plan['phases']:
            md_content += f"""
### المرحلة {phase['phase']}: {phase['name']}

- **المدة**: {phase['duration']}
- **الأنظمة**: {', '.join(phase['systems']) if isinstance(phase['systems'], list) else phase['systems']}
- **الوصف**: {phase['description']}

"""
        
        md_content += "\n---\n\n## 🔧 خطوات التنفيذ التفصيلية\n\n"
        
        for system_name, steps in self.rebuild_plan['implementation_steps'].items():
            md_content += f"""
### {system_name}

**الفئة**: {steps['category']}  
**الأولوية**: {steps['priority']}

**أمر التثبيت**:
```bash
{steps['install_command']}
```

**خطوات الإعداد**:
"""
            for i, step in enumerate(steps['setup_steps'], 1):
                md_content += f"{i}. {step}\n"
            
            if 'environment_variables' in steps:
                md_content += "\n**متغيرات البيئة المطلوبة**:\n"
                for var in steps['environment_variables']:
                    md_content += f"- `{var}`\n"
            
            md_content += "\n---\n"
        
        return md_content
    
    def save_markdown_documentation(self, output_file='docs/rebuild_guide.md'):
        """حفظ وثائق Markdown"""
        md_content = self.generate_markdown_documentation()
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"📄 تم حفظ دليل إعادة البناء في: {output_file}")

def main():
    generator = RebuildPlanGenerator()
    generator.generate_full_plan()
    generator.save_plan()
    generator.save_markdown_documentation()
    
    print("\n" + "="*60)
    print("✅ تم توليد خطة إعادة البناء الكاملة بنجاح!")
    print("="*60)

if __name__ == '__main__':
    main()
