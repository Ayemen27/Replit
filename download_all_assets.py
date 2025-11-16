
import os
import re
import requests
from pathlib import Path
from urllib.parse import urlparse, unquote
import time

def download_file(url, save_path):
    """تحميل ملف من URL وحفظه"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=30, headers=headers)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"✓ تم تحميل: {save_path}")
        return True
    except Exception as e:
        print(f"✗ خطأ في تحميل {url}: {e}")
        return False

def get_local_path(url, resource_type):
    """تحويل URL إلى مسار محلي"""
    parsed = urlparse(url)
    
    # CDN images من Replit
    if 'cdnimg.replit.com' in url or 'storage.googleapis.com' in url:
        match = re.search(r'/images/(.+)', url)
        if match:
            image_path = match.group(1).split('?')[0]
            return f"static/images/{image_path}"
    
    # ملفات JavaScript الخارجية
    if resource_type == 'js':
        filename = os.path.basename(parsed.path).split('?')[0]
        if not filename:
            filename = 'script.js'
        return f"static/js/external/{filename}"
    
    # ملفات CSS الخارجية
    if resource_type == 'css':
        filename = os.path.basename(parsed.path).split('?')[0]
        if not filename:
            filename = 'style.css'
        return f"static/css/external/{filename}"
    
    # الخطوط
    if resource_type == 'font':
        filename = os.path.basename(parsed.path).split('?')[0]
        return f"static/fonts/{filename}"
    
    # صور أخرى
    if resource_type == 'image':
        filename = os.path.basename(parsed.path).split('?')[0]
        ext = os.path.splitext(filename)[1]
        if not ext:
            ext = '.png'
            filename = filename + ext
        return f"static/images/external/{filename}"
    
    return None

def extract_resources(html_content):
    """استخراج جميع الموارد من HTML"""
    resources = {
        'images': set(),
        'css': set(),
        'js': set(),
        'fonts': set()
    }
    
    # الصور
    img_patterns = [
        r'src=["\'](https?://[^"\']+\.(?:png|jpg|jpeg|gif|webp|svg|ico)(?:\?[^"\']*)?)["\']',
        r'srcset=["\'](https?://[^"\']+)["\']',
        r'url\(["\']?(https?://[^"\')\s]+\.(?:png|jpg|jpeg|gif|webp|svg)(?:\?[^"\')\s]*)?)["\']?\)',
        r'https://cdnimg\.replit\.com/images/[^"\'>\s]+',
        r'https://storage\.googleapis\.com/replit/images/[^"\'>\s]+'
    ]
    
    for pattern in img_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        resources['images'].update(matches)
    
    # ملفات CSS
    css_patterns = [
        r'<link[^>]+href=["\'](https?://[^"\']+\.css(?:\?[^"\']*)?)["\']',
        r'@import\s+["\']?(https?://[^"\')\s]+\.css(?:\?[^"\')\s]*)?)["\']?'
    ]
    
    for pattern in css_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        resources['css'].update(matches)
    
    # ملفات JavaScript
    js_patterns = [
        r'<script[^>]+src=["\'](https?://[^"\']+\.js(?:\?[^"\']*)?)["\']',
        r'src=["\'](https?://[^"\']+\.js(?:\?[^"\']*)?)["\']'
    ]
    
    for pattern in js_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        resources['js'].update(matches)
    
    # الخطوط
    font_patterns = [
        r'url\(["\']?(https?://[^"\')\s]+\.(?:woff2?|ttf|eot|otf)(?:\?[^"\')\s]*)?)["\']?\)',
        r'src=["\'](https?://[^"\']+\.(?:woff2?|ttf|eot|otf)(?:\?[^"\']*)?)["\']'
    ]
    
    for pattern in font_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        resources['fonts'].update(matches)
    
    return resources

def scan_all_files(directory='.'):
    """فحص جميع ملفات HTML و CSS"""
    all_resources = {
        'images': set(),
        'css': set(),
        'js': set(),
        'fonts': set()
    }
    
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ['instance', '__pycache__', '.git', 'node_modules', 'static']]
        
        for file in files:
            if file.endswith(('.html', '.css')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        resources = extract_resources(content)
                        for key in all_resources:
                            all_resources[key].update(resources[key])
                except Exception as e:
                    print(f"خطأ في قراءة {file_path}: {e}")
    
    return all_resources

def replace_urls_in_file(file_path, url_mapping):
    """استبدال الروابط في ملف"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        for old_url, new_path in url_mapping.items():
            # استبدال الروابط مع مراعاة الحالات المختلفة
            content = content.replace(old_url, f'/{new_path}')
            content = content.replace(old_url.replace('https://', 'http://'), f'/{new_path}')
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ تم تحديث: {file_path}")
            return True
    except Exception as e:
        print(f"✗ خطأ في تحديث {file_path}: {e}")
    return False

def main():
    print("=" * 60)
    print("تحميل جميع الموارد الخارجية")
    print("=" * 60)
    
    print("\n1️⃣ جاري فحص الملفات...")
    all_resources = scan_all_files()
    
    total = sum(len(v) for v in all_resources.values())
    print(f"\n📊 تم العثور على {total} مورد:")
    print(f"   - صور: {len(all_resources['images'])}")
    print(f"   - CSS: {len(all_resources['css'])}")
    print(f"   - JavaScript: {len(all_resources['js'])}")
    print(f"   - خطوط: {len(all_resources['fonts'])}")
    
    if total == 0:
        print("\n✓ لا توجد موارد خارجية للتحميل")
        return
    
    print("\n2️⃣ جاري التحميل...")
    url_mapping = {}
    downloaded = 0
    failed = 0
    
    for resource_type, urls in all_resources.items():
        for url in urls:
            local_path = get_local_path(url, resource_type)
            if local_path and not os.path.exists(local_path):
                if download_file(url, local_path):
                    url_mapping[url] = local_path
                    downloaded += 1
                    time.sleep(0.2)  # تأخير بسيط لتجنب الحظر
                else:
                    failed += 1
            elif local_path:
                url_mapping[url] = local_path
    
    print(f"\n📥 النتائج:")
    print(f"   - تم التحميل: {downloaded}")
    print(f"   - فشل: {failed}")
    
    print("\n3️⃣ جاري تحديث الملفات...")
    updated_files = 0
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ['instance', '__pycache__', '.git', 'node_modules', 'static']]
        
        for file in files:
            if file.endswith(('.html', '.css')):
                file_path = os.path.join(root, file)
                if replace_urls_in_file(file_path, url_mapping):
                    updated_files += 1
    
    print(f"\n✅ تم الانتهاء!")
    print(f"   - ملفات تم تحديثها: {updated_files}")
    print(f"   - موارد تم تحميلها: {downloaded}")

if __name__ == '__main__':
    main()
