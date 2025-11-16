
#!/usr/bin/env python3
"""
نظام تحويل الصفحات الثابتة إلى صفحات ديناميكية
يقوم بإضافة علامات البيانات الديناميكية للصفحات الموجودة
"""

import os
import re
from pathlib import Path

class StaticToDynamicConverter:
    def __init__(self):
        self.static_pages = []
        self.conversion_patterns = {
            'gallery': {
                'marker': '<div class="projects-grid">',
                'replacement': '<div class="projects-grid" data-all-projects></div>',
                'needs_categories': True
            },
            'index': {
                'marker': '<div class="featured-projects">',
                'replacement': '<div class="featured-projects" data-featured-projects></div>',
                'needs_categories': True
            }
        }
    
    def scan_static_pages(self):
        """فحص جميع الصفحات الثابتة"""
        print("🔍 جاري فحص الصفحات الثابتة...")
        
        html_files = list(Path('.').rglob('*.html'))
        # استبعاد ملفات templates
        self.static_pages = [
            f for f in html_files 
            if not str(f).startswith('templates/')
        ]
        
        print(f"✅ تم العثور على {len(self.static_pages)} صفحة ثابتة")
        return self.static_pages
    
    def analyze_page(self, file_path):
        """تحليل صفحة لمعرفة ما تحتاجه من أنظمة"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        needs = {
            'projects': False,
            'categories': False,
            'authentication': False,
            'forms': False
        }
        
        # فحص المحتوى
        if 'project' in content.lower():
            needs['projects'] = True
        if 'category' in content.lower() or 'categories' in content.lower():
            needs['categories'] = True
        if 'login' in content.lower() or 'signup' in content.lower():
            needs['authentication'] = True
        if '<form' in content.lower():
            needs['forms'] = True
        
        return needs
    
    def inject_dynamic_loader(self, file_path):
        """حقن السكربت الديناميكي في الصفحة"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # تحقق إذا كان السكربت موجود بالفعل
        if 'dynamic-content.js' in content:
            return False
        
        # ابحث عن </body>
        if '</body>' not in content:
            return False
        
        # أضف السكربت قبل </body>
        script_tag = '\n    <script src="/static/js/dynamic-content.js"></script>\n'
        content = content.replace('</body>', f'{script_tag}</body>')
        
        # احفظ التغييرات
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    
    def add_data_attributes(self, file_path, page_type='general'):
        """إضافة علامات البيانات للعناصر"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        modified = False
        
        # أنماط مختلفة حسب نوع الصفحة
        if 'gallery' in str(file_path).lower():
            # أضف data-all-projects لعرض المشاريع
            if '<div class="projects' in content and 'data-all-projects' not in content:
                content = re.sub(
                    r'<div class="projects([^>]*?)>',
                    r'<div class="projects\1 data-all-projects">',
                    content,
                    count=1
                )
                modified = True
        
        elif file_path.name == 'index.html':
            # أضف data-featured-projects للصفحة الرئيسية
            if '<div class="featured' in content and 'data-featured-projects' not in content:
                content = re.sub(
                    r'<div class="featured([^>]*?)>',
                    r'<div class="featured\1 data-featured-projects">',
                    content,
                    count=1
                )
                modified = True
        
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return modified
    
    def generate_conversion_report(self):
        """توليد تقرير شامل عن التحويل"""
        report = {
            'total_pages': 0,
            'pages_by_type': {},
            'pages_needing_systems': {
                'projects': [],
                'categories': [],
                'authentication': [],
                'forms': []
            }
        }
        
        for page in self.static_pages:
            report['total_pages'] += 1
            
            # تحليل الصفحة
            needs = self.analyze_page(page)
            
            # تصنيف حسب المجلد
            folder = str(page.parent)
            if folder not in report['pages_by_type']:
                report['pages_by_type'][folder] = []
            report['pages_by_type'][folder].append(str(page.name))
            
            # تسجيل الأنظمة المطلوبة
            for system, needed in needs.items():
                if needed:
                    report['pages_needing_systems'][system].append(str(page))
        
        return report
    
    def convert_all(self):
        """تحويل جميع الصفحات"""
        print("\n" + "="*60)
        print("🔄 بدء عملية التحويل الشاملة")
        print("="*60 + "\n")
        
        self.scan_static_pages()
        
        converted_count = 0
        enhanced_count = 0
        
        for page in self.static_pages:
            print(f"\n📄 معالجة: {page}")
            
            # حقن السكربت الديناميكي
            if self.inject_dynamic_loader(page):
                print(f"  ✅ تم حقن السكربت الديناميكي")
                converted_count += 1
            else:
                print(f"  ⏭️  السكربت موجود مسبقاً")
            
            # إضافة علامات البيانات
            if self.add_data_attributes(page):
                print(f"  ✅ تم إضافة علامات البيانات")
                enhanced_count += 1
        
        # توليد التقرير
        report = self.generate_conversion_report()
        
        print("\n" + "="*60)
        print("📊 ملخص التحويل")
        print("="*60)
        print(f"\n✅ إجمالي الصفحات: {report['total_pages']}")
        print(f"✅ صفحات تم تحويلها: {converted_count}")
        print(f"✅ صفحات تم تحسينها: {enhanced_count}")
        
        print("\n📁 التصنيف حسب المجلدات:")
        for folder, pages in report['pages_by_type'].items():
            print(f"  - {folder}: {len(pages)} صفحة")
        
        print("\n🔧 الأنظمة المطلوبة:")
        for system, pages in report['pages_needing_systems'].items():
            if pages:
                print(f"  - {system}: {len(pages)} صفحة")
        
        return report

if __name__ == '__main__':
    converter = StaticToDynamicConverter()
    report = converter.convert_all()
    
    # حفظ التقرير
    import json
    with open('conversion_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\n💾 تم حفظ التقرير في: conversion_report.json")
