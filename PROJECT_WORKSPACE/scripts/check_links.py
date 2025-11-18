#!/usr/bin/env python3
"""
سكريبت فحص صحة الروابط في ملفات Markdown

الاستخدام:
    python3 PROJECT_WORKSPACE/scripts/check_links.py

النتيجة:
    - يعرض عدد الروابط الكلي
    - يعرض عدد الروابط المكسورة
    - يعرض قائمة الروابط المكسورة مع موقعها
"""

import os
import re
import sys

def check_md_links(root_dir):
    """فحص جميع روابط Markdown في المجلد"""
    broken_links = []
    total_links = 0
    files_scanned = 0
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # تجاهل مجلدات node_modules و .git
        dirnames[:] = [d for d in dirnames if d not in ['node_modules', '.git', '__pycache__']]
        
        for filename in filenames:
            if filename.endswith('.md'):
                filepath = os.path.join(dirpath, filename)
                files_scanned += 1
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # البحث عن روابط نسبية تنتهي بـ .md
                    pattern = r'\]\((\.\./[^\)]+?\.md)\)'
                    matches = re.findall(pattern, content)
                    total_links += len(matches)
                    
                    for link in matches:
                        # تحويل المسار النسبي إلى مسار كامل
                        full_path = os.path.normpath(
                            os.path.join(os.path.dirname(filepath), link)
                        )
                        
                        # التحقق من وجود الملف
                        if not os.path.exists(full_path):
                            broken_links.append({
                                'file': filepath.replace(root_dir + '/', ''),
                                'link': link,
                                'expected_path': full_path
                            })
                except Exception as e:
                    print(f"⚠️  خطأ في قراءة {filepath}: {e}", file=sys.stderr)
    
    return broken_links, total_links, files_scanned

def main():
    """الدالة الرئيسية"""
    root_dir = 'PROJECT_WORKSPACE'
    
    if not os.path.exists(root_dir):
        print(f"❌ المجلد {root_dir} غير موجود!", file=sys.stderr)
        sys.exit(1)
    
    print("="*70)
    print("📊 تقرير فحص الروابط في PROJECT_WORKSPACE")
    print("="*70)
    print("\n🔍 جاري الفحص...")
    
    broken, total, files = check_md_links(root_dir)
    
    print(f"\n✅ الملفات المفحوصة: {files}")
    print(f"✅ إجمالي الروابط: {total}")
    print(f"❌ روابط مكسورة: {len(broken)}")
    print(f"✅ روابط صحيحة: {total - len(broken)}")
    
    if total > 0:
        success_rate = ((total - len(broken)) / total * 100)
        print(f"\n🎯 النسبة المئوية: {success_rate:.1f}% صحيح")
    
    if broken:
        print(f"\n⚠️  الروابط المكسورة ({len(broken)}):")
        print("="*70)
        for i, item in enumerate(broken, 1):
            print(f"\n{i}. الملف: {item['file']}")
            print(f"   الرابط: {item['link']}")
            print(f"   المسار المتوقع: {item['expected_path']}")
        print("\n" + "="*70)
        sys.exit(1)
    else:
        print("\n🎉 ممتاز! جميع الروابط صحيحة!")
        print("="*70)
        sys.exit(0)

if __name__ == "__main__":
    main()
