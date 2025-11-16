
import os
import re
import requests

def download_google_fonts():
    """تحميل خطوط Google المستخدمة في الموقع"""
    
    # الخطوط المستخدمة في الموقع
    fonts_to_download = [
        {
            'url': 'https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500&display=swap',
            'name': 'ibm-plex-sans'
        }
    ]
    
    os.makedirs('static/fonts', exist_ok=True)
    
    for font_info in fonts_to_download:
        try:
            # تحميل ملف CSS
            response = requests.get(font_info['url'])
            response.raise_for_status()
            css_content = response.text
            
            # استخراج روابط الخطوط
            font_urls = re.findall(r'url\((https?://[^)]+)\)', css_content)
            
            local_css = css_content
            for font_url in font_urls:
                # تحميل ملف الخط
                font_response = requests.get(font_url)
                font_response.raise_for_status()
                
                # تحديد اسم الملف
                font_filename = os.path.basename(font_url.split('?')[0])
                font_path = f'static/fonts/{font_filename}'
                
                with open(font_path, 'wb') as f:
                    f.write(font_response.content)
                
                print(f"✓ تم تحميل الخط: {font_filename}")
                
                # تحديث CSS
                local_css = local_css.replace(font_url, f'/static/fonts/{font_filename}')
            
            # حفظ ملف CSS المحلي
            css_path = f'static/fonts/{font_info["name"]}.css'
            with open(css_path, 'w', encoding='utf-8') as f:
                f.write(local_css)
            
            print(f"✓ تم حفظ CSS: {css_path}")
            
        except Exception as e:
            print(f"✗ خطأ في تحميل {font_info['name']}: {e}")

if __name__ == '__main__':
    download_google_fonts()
