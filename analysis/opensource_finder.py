#!/usr/bin/env python3
"""
مكتشف المصادر المفتوحة - Open Source Finder
يوفر روابط ومعلومات عن المصادر المفتوحة المشابهة للنظام الأصلي
"""

import json
import os

class OpenSourceFinder:
    def __init__(self):
        self.resources = {
            'complete_boilerplates': [],
            'framework_specific': {},
            'component_libraries': {},
            'deployment_guides': []
        }
        
        self._load_resources()
    
    def _load_resources(self):
        """تحميل قائمة المصادر المفتوحة"""
        
        self.resources['complete_boilerplates'] = [
            {
                'name': 'NJS-Firebase-SaaS-Boilerplate',
                'description': 'Next.js + Firebase + Stripe SaaS Boilerplate',
                'github': 'https://github.com/WHEREISDAN/NJS-Firebase-SaaS-Boilerplate',
                'technologies': ['Next.js', 'Firebase Auth', 'Firestore', 'Stripe', 'Tailwind CSS'],
                'similarity': 'عالية جداً - يحتوي على معظم التقنيات',
                'features': [
                    'Firebase Authentication (Email, Google)',
                    'Cloud Firestore Database',
                    'Stripe Subscription Payments',
                    'Tailwind CSS Styling',
                    'TypeScript Support'
                ],
                'setup_steps': [
                    'git clone https://github.com/WHEREISDAN/NJS-Firebase-SaaS-Boilerplate',
                    'npm install',
                    'إعداد .env مع Firebase و Stripe credentials',
                    'npm run dev'
                ]
            },
            {
                'name': 'graphql-nextjs-apollo-boilerplate',
                'description': 'Next.js + Apollo GraphQL + Firebase',
                'github': 'https://github.com/nateq314/graphql-nextjs-apollo-boilerplate',
                'technologies': ['Next.js', 'Apollo Client', 'Apollo Server', 'Firebase', 'TypeScript'],
                'similarity': 'عالية - يطابق البنية الأساسية',
                'features': [
                    'GraphQL API on Firebase Functions',
                    'Apollo Server & Client',
                    'Cookie-based Authentication',
                    'Styled Components',
                    'TypeScript'
                ],
                'setup_steps': [
                    'git clone https://github.com/nateq314/graphql-nextjs-apollo-boilerplate',
                    'npm install',
                    'إعداد Firebase Project',
                    'npm run dev'
                ]
            },
            {
                'name': 'next-react-graphql-apollo-hooks',
                'description': 'Next.js + Apollo + GraphQL مع React Hooks',
                'github': 'https://github.com/atherosai/next-react-graphql-apollo-hooks',
                'technologies': ['Next.js', 'Apollo', 'GraphQL', 'TypeScript', 'React Hooks'],
                'similarity': 'متوسطة إلى عالية',
                'features': [
                    'React Hooks Pattern',
                    'Automatic Type Generation',
                    'High-Performance SSR',
                    'Production Ready'
                ],
                'setup_steps': [
                    'git clone https://github.com/atherosai/next-react-graphql-apollo-hooks',
                    'npm install',
                    'npm run dev'
                ]
            }
        ]
        
        self.resources['framework_specific'] = {
            'Next.js': [
                {
                    'name': 'Next.js Official Examples',
                    'url': 'https://github.com/vercel/next.js/tree/canary/examples',
                    'description': 'مجموعة ضخمة من الأمثلة الرسمية'
                },
                {
                    'name': 'Next.js + Apollo Example',
                    'url': 'https://github.com/vercel/next.js/tree/canary/examples/with-apollo',
                    'description': 'مثال رسمي لدمج Apollo مع Next.js'
                }
            ],
            'Apollo GraphQL': [
                {
                    'name': 'Apollo Client Documentation',
                    'url': 'https://www.apollographql.com/docs/react/',
                    'description': 'الوثائق الرسمية لـ Apollo Client'
                },
                {
                    'name': 'Apollo Server Examples',
                    'url': 'https://github.com/apollographql/apollo-server',
                    'description': 'أمثلة Apollo Server'
                }
            ],
            'Firebase': [
                {
                    'name': 'Firebase Web Samples',
                    'url': 'https://github.com/firebase/quickstart-js',
                    'description': 'أمثلة Firebase الرسمية للويب'
                },
                {
                    'name': 'Firebase + Next.js Template',
                    'url': 'https://divjoy.com/boilerplate/next-firebase-stripe',
                    'description': 'قالب متكامل مع Next.js و Firebase'
                }
            ],
            'Stripe': [
                {
                    'name': 'Stripe Samples',
                    'url': 'https://github.com/stripe-samples',
                    'description': 'أمثلة Stripe الرسمية'
                },
                {
                    'name': 'Next.js Stripe Integration',
                    'url': 'https://github.com/vercel/nextjs-subscription-payments',
                    'description': 'نظام اشتراكات كامل مع Stripe'
                }
            ]
        }
        
        self.resources['component_libraries'] = {
            'UI Components': [
                {
                    'name': 'shadcn/ui',
                    'url': 'https://ui.shadcn.com/',
                    'description': 'مكونات UI جاهزة للنسخ واللصق',
                    'compatible_with': ['Next.js', 'React', 'Tailwind CSS']
                },
                {
                    'name': 'Chakra UI',
                    'url': 'https://chakra-ui.com/',
                    'description': 'مكتبة مكونات React كاملة',
                    'compatible_with': ['Next.js', 'React']
                },
                {
                    'name': 'Material-UI (MUI)',
                    'url': 'https://mui.com/',
                    'description': 'مكونات Material Design',
                    'compatible_with': ['Next.js', 'React']
                }
            ],
            'Analytics Integration': [
                {
                    'name': 'react-ga4',
                    'url': 'https://github.com/PriceRunner/react-ga4',
                    'description': 'Google Analytics 4 for React'
                },
                {
                    'name': 'Segment Analytics.js',
                    'url': 'https://github.com/segmentio/analytics-next',
                    'description': 'Segment SDK الرسمي'
                }
            ]
        }
        
        self.resources['deployment_guides'] = [
            {
                'platform': 'Vercel',
                'guide_url': 'https://vercel.com/docs',
                'description': 'أفضل منصة لنشر Next.js',
                'features': ['Automatic deployments', 'Edge Functions', 'Analytics']
            },
            {
                'platform': 'Netlify',
                'guide_url': 'https://docs.netlify.com/',
                'description': 'منصة نشر مع CI/CD مدمج',
                'features': ['Serverless Functions', 'Form Handling', 'Split Testing']
            },
            {
                'platform': 'AWS Amplify',
                'guide_url': 'https://docs.amplify.aws/',
                'description': 'منصة AWS للتطبيقات Full-Stack',
                'features': ['Hosting', 'Authentication', 'APIs', 'Storage']
            }
        ]
    
    def get_recommended_stack(self):
        """الحصول على التقنيات الموصى بها لإعادة البناء"""
        return {
            'core_framework': {
                'name': 'Next.js 14+',
                'reason': 'إطار العمل الأساسي المستخدم في النظام الأصلي',
                'installation': 'npx create-next-app@latest',
                'documentation': 'https://nextjs.org/docs'
            },
            'data_layer': {
                'name': 'Apollo Client + GraphQL',
                'reason': 'لإدارة البيانات والاستعلامات',
                'installation': 'npm install @apollo/client graphql',
                'documentation': 'https://www.apollographql.com/docs/'
            },
            'authentication': {
                'name': 'Firebase Authentication',
                'reason': 'نظام مصادقة شامل وسهل الاستخدام',
                'installation': 'npm install firebase',
                'documentation': 'https://firebase.google.com/docs/auth'
            },
            'database': {
                'name': 'Cloud Firestore',
                'reason': 'قاعدة بيانات NoSQL مع تحديثات فورية',
                'installation': 'مضمن مع Firebase',
                'documentation': 'https://firebase.google.com/docs/firestore'
            },
            'payments': {
                'name': 'Stripe',
                'reason': 'نظام مدفوعات آمن ومتكامل',
                'installation': 'npm install @stripe/stripe-js stripe',
                'documentation': 'https://stripe.com/docs'
            },
            'analytics': {
                'name': 'Google Tag Manager + GA4',
                'reason': 'إدارة Tags وتحليلات شاملة',
                'installation': 'عبر script tags',
                'documentation': 'https://tagmanager.google.com/'
            },
            'styling': {
                'name': 'Tailwind CSS',
                'reason': 'Framework CSS سريع وفعال',
                'installation': 'npm install tailwindcss',
                'documentation': 'https://tailwindcss.com/docs'
            },
            'monitoring': {
                'name': 'Datadog RUM',
                'reason': 'مراقبة الأداء والأخطاء',
                'installation': 'npm install @datadog/browser-rum',
                'documentation': 'https://docs.datadoghq.com/'
            }
        }
    
    def generate_setup_guide(self):
        """توليد دليل الإعداد الكامل"""
        guide = {
            'step_1_clone_boilerplate': {
                'title': 'الخطوة 1: استنساخ Boilerplate مشابه',
                'recommended': self.resources['complete_boilerplates'][0],
                'alternatives': self.resources['complete_boilerplates'][1:],
                'commands': [
                    'git clone https://github.com/WHEREISDAN/NJS-Firebase-SaaS-Boilerplate',
                    'cd NJS-Firebase-SaaS-Boilerplate',
                    'npm install'
                ]
            },
            'step_2_configure_services': {
                'title': 'الخطوة 2: إعداد الخدمات الخارجية',
                'services': {
                    'Firebase': {
                        'steps': [
                            'إنشاء مشروع في https://console.firebase.google.com',
                            'تفعيل Authentication',
                            'إنشاء Firestore Database',
                            'نسخ credentials إلى .env'
                        ],
                        'env_vars': [
                            'NEXT_PUBLIC_FIREBASE_API_KEY',
                            'NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN',
                            'NEXT_PUBLIC_FIREBASE_PROJECT_ID'
                        ]
                    },
                    'Stripe': {
                        'steps': [
                            'إنشاء حساب في https://stripe.com',
                            'الحصول على API keys من Dashboard',
                            'إعداد Products و Prices',
                            'تكوين Webhooks'
                        ],
                        'env_vars': [
                            'NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY',
                            'STRIPE_SECRET_KEY'
                        ]
                    }
                }
            },
            'step_3_add_apollo': {
                'title': 'الخطوة 3: إضافة Apollo GraphQL',
                'commands': [
                    'npm install @apollo/client graphql',
                    'إنشاء lib/apollo-client.js',
                    'إعداد Apollo Provider في _app.js'
                ],
                'example_code': '''
import { ApolloClient, InMemoryCache, HttpLink } from '@apollo/client';

const client = new ApolloClient({
  link: new HttpLink({
    uri: process.env.NEXT_PUBLIC_GRAPHQL_ENDPOINT,
  }),
  cache: new InMemoryCache()
});

export default client;
'''
            },
            'step_4_add_analytics': {
                'title': 'الخطوة 4: إضافة Analytics',
                'gtm_setup': [
                    'إنشاء حساب Google Tag Manager',
                    'الحصول على GTM Container ID',
                    'إضافة GTM script في _document.js',
                    'إعداد dataLayer events'
                ],
                'segment_setup': [
                    'npm install @segment/analytics-next',
                    'إعداد Segment Write Key',
                    'تكوين destinations'
                ]
            },
            'step_5_customize': {
                'title': 'الخطوة 5: تخصيص التطبيق',
                'tasks': [
                    'تعديل الواجهات بناءً على التصاميم الأصلية',
                    'إضافة المكونات المخصصة',
                    'تكوين routing',
                    'إعداد SEO metadata',
                    'إضافة المحتوى'
                ]
            },
            'step_6_deploy': {
                'title': 'الخطوة 6: النشر',
                'platforms': self.resources['deployment_guides'],
                'recommended': 'Vercel',
                'steps': [
                    'ربط repository مع Vercel',
                    'تكوين Environment Variables',
                    'تفعيل Automatic Deployments',
                    'إعداد Custom Domain (اختياري)'
                ]
            }
        }
        
        return guide
    
    def save_resources(self, output_file='analysis/opensource_resources.json'):
        """حفظ قائمة المصادر"""
        data = {
            'resources': self.resources,
            'recommended_stack': self.get_recommended_stack(),
            'setup_guide': self.generate_setup_guide()
        }
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ تم حفظ قائمة المصادر المفتوحة في: {output_file}")
        return data
    
    def generate_markdown_guide(self):
        """توليد دليل Markdown"""
        guide = self.generate_setup_guide()
        recommended = self.get_recommended_stack()
        
        md = "# 🚀 دليل إعادة البناء باستخدام المصادر المفتوحة\n\n"
        
        md += "## 📚 التقنيات الموصى بها\n\n"
        for key, tech in recommended.items():
            md += f"### {tech['name']}\n"
            md += f"- **السبب**: {tech['reason']}\n"
            md += f"- **التثبيت**: `{tech['installation']}`\n"
            md += f"- **الوثائق**: {tech['documentation']}\n\n"
        
        md += "## 🎯 خطوات الإعداد\n\n"
        for step_key, step_data in guide.items():
            md += f"### {step_data['title']}\n\n"
            
            if 'commands' in step_data:
                md += "```bash\n"
                for cmd in step_data['commands']:
                    md += f"{cmd}\n"
                md += "```\n\n"
            
            if 'example_code' in step_data:
                md += "**مثال على الكود:**\n```javascript\n"
                md += step_data['example_code'].strip()
                md += "\n```\n\n"
        
        md += "## 🔗 مصادر مفتوحة موصى بها\n\n"
        for boilerplate in self.resources['complete_boilerplates']:
            md += f"### {boilerplate['name']}\n"
            md += f"- **الوصف**: {boilerplate['description']}\n"
            md += f"- **GitHub**: {boilerplate['github']}\n"
            md += f"- **درجة التشابه**: {boilerplate['similarity']}\n"
            md += f"- **التقنيات**: {', '.join(boilerplate['technologies'])}\n\n"
        
        return md
    
    def save_markdown_guide(self, output_file='docs/opensource_rebuild_guide.md'):
        """حفظ دليل Markdown"""
        md = self.generate_markdown_guide()
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md)
        
        print(f"📄 تم حفظ دليل المصادر المفتوحة في: {output_file}")

def main():
    finder = OpenSourceFinder()
    finder.save_resources()
    finder.save_markdown_guide()
    
    print("\n" + "="*60)
    print("✅ تم توليد قائمة المصادر المفتوحة بنجاح!")
    print("="*60)

if __name__ == '__main__':
    main()
