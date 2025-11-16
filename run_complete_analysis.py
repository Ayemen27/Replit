#!/usr/bin/env python3
"""
سكريبت التحليل الشامل - Complete Analysis Runner
يشغل جميع السكريبتات التحليلية ويولد التقارير الكاملة
"""

import os
import sys
import json
from pathlib import Path

sys.path.append('analysis')

from deep_system_analyzer import DeepSystemAnalyzer
from script_tag_extractor import ScriptTagExtractor
from bundled_data_extractor import BundledDataExtractor
from rebuild_plan_generator import RebuildPlanGenerator
from opensource_finder import OpenSourceFinder

def main():
    print("="*70)
    print("🚀 بدء التحليل الشامل للنظام الأصلي")
    print("="*70)
    print()
    
    os.makedirs('analysis', exist_ok=True)
    os.makedirs('docs', exist_ok=True)
    
    print("📊 المرحلة 1: تحليل الأنظمة المتقدم")
    print("-" * 70)
    analyzer = DeepSystemAnalyzer(static_dir='.')
    analyzer.analyze_all_files()
    systems_report = analyzer.save_report()
    print()
    
    print("📜 المرحلة 2: استخراج Script Tags")
    print("-" * 70)
    extractor = ScriptTagExtractor(static_dir='.')
    extractor.analyze_all_files()
    scripts_report = extractor.save_report()
    print()
    
    print("📦 المرحلة 3: استخراج البيانات المحزومة")
    print("-" * 70)
    bundled_extractor = BundledDataExtractor(root_dir='.')
    bundled_extractor.analyze_all_files()
    bundled_report = bundled_extractor.save_report()
    print()
    
    print("🔗 المرحلة 4: البحث عن المصادر المفتوحة")
    print("-" * 70)
    opensource = OpenSourceFinder()
    opensource.save_resources()
    opensource.save_markdown_guide()
    print()
    
    print("📋 المرحلة 5: توليد خطة إعادة البناء")
    print("-" * 70)
    planner = RebuildPlanGenerator()
    planner.generate_full_plan()
    planner.save_plan()
    planner.save_markdown_documentation()
    print()
    
    print("📊 المرحلة 6: توليد التقرير النهائي الموحد")
    print("-" * 70)
    
    final_report = {
        'analysis_summary': {
            'total_html_files': len(list(Path('.').glob('**/*.html'))),
            'total_js_files': len(list(Path('.').glob('**/*.js'))),
            'systems_detected': len(systems_report['systems']),
            'integrations_found': len(systems_report['integrations']),
            'external_scripts': scripts_report['summary']['total_external_scripts'],
            'inline_scripts': scripts_report['summary']['total_inline_scripts'],
            'next_data_instances': bundled_report['summary']['next_data_instances'],
            'apollo_states': bundled_report['summary']['apollo_states'],
            'firebase_configs': bundled_report['summary']['firebase_configs'],
            'api_endpoints_found': bundled_report['summary']['api_endpoints'],
            'environment_vars': bundled_report['summary']['environment_vars']
        },
        'detected_systems': list(systems_report['systems'].keys()),
        'key_findings': {
            'has_nextjs': 'Next.js' in systems_report['systems'],
            'has_apollo': 'Apollo GraphQL' in systems_report['systems'],
            'has_firebase': 'Firebase' in systems_report['systems'],
            'has_stripe': 'Stripe' in systems_report['systems'],
            'has_gtm': 'Google Tag Manager' in systems_report['systems'],
            'has_ga4': 'Google Analytics 4' in systems_report['systems']
        },
        'recommendations': {
            'primary_boilerplate': 'NJS-Firebase-SaaS-Boilerplate',
            'estimated_rebuild_time': '12-20 يوم عمل',
            'complexity_level': 'متوسط إلى عالي',
            'team_size_recommended': '2-3 مطورين'
        },
        'next_steps': [
            '1. مراجعة ملف analysis/verified_systems.json للأنظمة المكتشفة',
            '2. قراءة docs/rebuild_guide.md لخطة إعادة البناء',
            '3. مراجعة docs/opensource_rebuild_guide.md للمصادر المفتوحة',
            '4. استنساخ Boilerplate الموصى به من GitHub',
            '5. البدء بإعداد الخدمات الخارجية (Firebase, Stripe, etc)',
            '6. تخصيص الواجهات والمكونات بناءً على التصاميم الأصلية'
        ]
    }
    
    output_file = 'analysis/final_report.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_report, f, ensure_ascii=False, indent=2)
    
    print(f"✅ تم حفظ التقرير النهائي في: {output_file}")
    print()
    
    print("="*70)
    print("✨ اكتمل التحليل الشامل بنجاح!")
    print("="*70)
    print()
    print("📁 الملفات المنتجة:")
    print("  - analysis/verified_systems.json       (الأنظمة المكتشفة)")
    print("  - analysis/script_tags_report.json     (تقرير Script Tags)")
    print("  - analysis/bundled_data.json           (البيانات المحزومة)")
    print("  - analysis/rebuild_plan.json           (خطة إعادة البناء)")
    print("  - analysis/opensource_resources.json   (المصادر المفتوحة)")
    print("  - analysis/final_report.json           (التقرير النهائي)")
    print("  - docs/rebuild_guide.md                (دليل إعادة البناء)")
    print("  - docs/opensource_rebuild_guide.md     (دليل المصادر المفتوحة)")
    print()
    print("📊 ملخص النتائج:")
    print(f"  ✓ عدد الأنظمة المكتشفة: {final_report['analysis_summary']['systems_detected']}")
    print(f"  ✓ عدد التكاملات: {final_report['analysis_summary']['integrations_found']}")
    print(f"  ✓ ملفات HTML محللة: {final_report['analysis_summary']['total_html_files']}")
    print(f"  ✓ ملفات JS محللة: {final_report['analysis_summary']['total_js_files']}")
    print()
    print("🎯 الأنظمة الرئيسية:")
    for system in final_report['detected_systems'][:10]:
        print(f"  • {system}")
    print()
    print("🚀 الخطوات التالية:")
    for step in final_report['next_steps']:
        print(f"  {step}")
    print()

if __name__ == '__main__':
    main()
