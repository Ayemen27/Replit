# 📋 تفاصيل المهام - الوكيل رقم 7 (تكملة)

> هذا الملف يكمل `WEB_MONITOR_AGENT_7_IMPLEMENTATION_PLAN.md`

---

## المرحلة 2: مراقبة المعاملات الصناعية (Synthetic Monitoring) - 4 مهام (800,000 توكن)

### المهمة 2.1: إعداد Playwright للمراقبة
**المدة:** نصف يوم  
**الميزانية:** 200,000 توكن  
**الأولوية:** Critical

**الخطوات:**
```bash
# على Replit - إعداد البيئة
pip install playwright pytest-playwright
python -m playwright install chromium

# إنشاء ملف الإعدادات
cat > agents/web_monitor/playwright_config.py << 'EOF'
from playwright.sync_api import sync_playwright, Browser, Page
from typing import Dict, Optional
import asyncio

class PlaywrightManager:
    """إدارة متصفحات Playwright"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.playwright = None
    
    def start(self):
        """بدء Playwright"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
    
    def new_page(self) -> Page:
        """صفحة جديدة"""
        if not self.browser:
            self.start()
        return self.browser.new_page()
    
    def close(self):
        """إغلاق المتصفح"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
EOF
```

---

### المهمة 2.2: مراقبة صفحة تسجيل الدخول
**المدة:** يوم واحد  
**الميزانية:** 200,000 توكن  
**الأولوية:** Critical

```python
# الملف: agents/web_monitor/core/session_inspector.py

from playwright.sync_api import Page, sync_playwright
from typing import Dict, Any
from datetime import datetime
import time

class SessionInspector:
    """مراقبة جلسات المستخدمين وصفحات الدخول"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    async def check_login_page(self) -> Dict[str, Any]:
        """
        فحص صفحة تسجيل الدخول
        
        السيناريوهات:
        1. الصفحة تفتح بنجاح
        2. جميع العناصر موجودة (username, password, button)
        3. التحقق من CSRF token
        4. زمن التحميل معقول
        """
        result = {
            "check": "login_page",
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "load_time_ms": 0,
            "issues": []
        }
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                # قياس وقت التحميل
                start_time = time.time()
                page.goto(f"{self.base_url}/login", wait_until="networkidle")
                load_time = (time.time() - start_time) * 1000
                result["load_time_ms"] = load_time
                
                # فحص العناصر الأساسية
                username_field = page.locator('input[name="username"], input[type="email"]')
                password_field = page.locator('input[name="password"], input[type="password"]')
                submit_button = page.locator('button[type="submit"], input[type="submit"]')
                
                if not username_field.is_visible():
                    result["issues"].append("Username field not found")
                
                if not password_field.is_visible():
                    result["issues"].append("Password field not found")
                
                if not submit_button.is_visible():
                    result["issues"].append("Submit button not found")
                
                # فحص زمن التحميل
                if load_time > 3000:
                    result["issues"].append(f"Slow page load: {load_time:.0f}ms")
                
                # فحص HTTPS
                if not page.url.startswith("https://"):
                    result["issues"].append("Login page not using HTTPS")
                
                # أخذ لقطة شاشة للتوثيق
                screenshot_path = f"/tmp/login_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                page.screenshot(path=screenshot_path)
                result["screenshot"] = screenshot_path
                
                result["success"] = len(result["issues"]) == 0
                
            except Exception as e:
                result["issues"].append(f"Error: {str(e)}")
                result["success"] = False
            finally:
                browser.close()
        
        return result
    
    async def test_login_flow(
        self, 
        username: str = "test@example.com",
        password: str = "test_password_invalid"
    ) -> Dict[str, Any]:
        """
        اختبار مسار تسجيل الدخول (بدون بيانات حقيقية)
        
        السيناريو:
        1. فتح صفحة Login
        2. ملء البيانات
        3. محاولة الدخول
        4. التحقق من رسالة الخطأ المناسبة
        """
        result = {
            "check": "login_flow_test",
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "steps_completed": [],
            "issues": []
        }
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                # الخطوة 1: فتح الصفحة
                page.goto(f"{self.base_url}/login")
                result["steps_completed"].append("Page loaded")
                
                # الخطوة 2: ملء النموذج
                page.fill('input[name="username"], input[type="email"]', username)
                page.fill('input[name="password"], input[type="password"]', password)
                result["steps_completed"].append("Form filled")
                
                # الخطوة 3: محاولة الدخول
                page.click('button[type="submit"], input[type="submit"]')
                page.wait_for_load_state("networkidle")
                result["steps_completed"].append("Submit clicked")
                
                # الخطوة 4: التحقق من الرد
                # يجب أن تظهر رسالة خطأ لأن البيانات غير صحيحة
                error_message = page.locator('.error, .alert-danger, [role="alert"]')
                
                if error_message.is_visible():
                    result["steps_completed"].append("Error message displayed")
                    result["success"] = True
                else:
                    result["issues"].append("No error message for invalid credentials")
                
                # التحقق من عدم الدخول فعلياً
                if "/dashboard" in page.url or "/home" in page.url:
                    result["issues"].append("SECURITY ISSUE: Invalid login succeeded!")
                    result["success"] = False
                
            except Exception as e:
                result["issues"].append(f"Error: {str(e)}")
            finally:
                browser.close()
        
        return result
```

**معايير القبول:**
- [ ] الكود يعمل على السيرفر
- [ ] يكتشف صفحة Login بنجاح
- [ ] يلتقط لقطات شاشة
- [ ] يرصد الأخطاء بدقة
- [ ] يرسل التقارير للوكيل الأب

---

### المهمة 2.3: فحص صفحات الدفع (Payment Pages)
**المدة:** يوم واحد  
**الميزانية:** 200,000 توكن  
**الأولوية:** Critical

```python
# الملف: agents/web_monitor/core/payment_page_checker.py

class PaymentPageChecker:
    """فحص صفحات الدفع والاشتراكات"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    async def check_payment_page_accessibility(self) -> Dict[str, Any]:
        """
        التحقق من إمكانية الوصول لصفحة الدفع
        
        ملاحظة: لا نقوم بعمليات دفع فعلية!
        فقط نتحقق من:
        - الصفحة تفتح
        - العناصر موجودة
        - HTTPS
        - No console errors
        """
        result = {
            "check": "payment_page_accessibility",
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "issues": []
        }
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # جمع console errors
            console_errors = []
            page.on("console", lambda msg: 
                console_errors.append(msg.text) if msg.type == "error" else None
            )
            
            try:
                # محاولة الوصول لصفحة الاشتراكات/الدفع
                possible_urls = [
                    f"{self.base_url}/pricing",
                    f"{self.base_url}/subscribe",
                    f"{self.base_url}/payment",
                    f"{self.base_url}/checkout"
                ]
                
                page_found = False
                for url in possible_urls:
                    try:
                        response = page.goto(url, wait_until="networkidle")
                        if response and response.status == 200:
                            page_found = True
                            result["payment_page_url"] = url
                            break
                    except:
                        continue
                
                if not page_found:
                    result["issues"].append("Payment page not found")
                    result["success"] = False
                    return result
                
                # التحقق من HTTPS
                if not page.url.startswith("https://"):
                    result["issues"].append("CRITICAL: Payment page not using HTTPS!")
                
                # التحقق من وجود أخطاء في Console
                if console_errors:
                    result["issues"].append(f"Console errors: {len(console_errors)}")
                    result["console_errors"] = console_errors[:5]  # أول 5 فقط
                
                # البحث عن عناصر الدفع
                payment_form = page.locator('form[action*="payment"], form[action*="checkout"]')
                if not payment_form.count() > 0:
                    result["issues"].append("Payment form not found")
                
                # التحقق من Mixed Content
                mixed_content = page.evaluate("""
                    () => {
                        const scripts = Array.from(document.querySelectorAll('script[src]'));
                        const http_scripts = scripts.filter(s => s.src.startsWith('http://'));
                        return http_scripts.map(s => s.src);
                    }
                """)
                
                if mixed_content:
                    result["issues"].append(f"Mixed content detected: {len(mixed_content)} HTTP resources")
                
                result["success"] = len(result["issues"]) == 0
                
            except Exception as e:
                result["issues"].append(f"Error: {str(e)}")
            finally:
                browser.close()
        
        return result
```

---

### المهمة 2.4: تجميع نتائج Synthetic Monitoring
**المدة:** نصف يوم  
**الميزانية:** 200,000 توكن  

```python
# الملف: agents/web_monitor/core/synthetic_flow_monitor.py

from typing import List, Dict, Any
from .session_inspector import SessionInspector
from .payment_page_checker import PaymentPageChecker

class SyntheticFlowMonitor:
    """منسق Synthetic Monitoring - يدير جميع الفحوصات"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.base_url = config['target_app']['url']
        
        # تهيئة الفاحصين
        self.session_inspector = SessionInspector(self.base_url)
        self.payment_checker = PaymentPageChecker(self.base_url)
    
    async def run_all_synthetic_checks(self) -> List[Dict[str, Any]]:
        """تنفيذ جميع الفحوصات الصناعية"""
        results = []
        
        # 1. فحص صفحة Login
        if self.config.get('checks', {}).get('session_monitoring', True):
            login_result = await self.session_inspector.check_login_page()
            results.append(login_result)
            
            login_flow = await self.session_inspector.test_login_flow()
            results.append(login_flow)
        
        # 2. فحص صفحات الدفع
        payment_result = await self.payment_checker.check_payment_page_accessibility()
        results.append(payment_result)
        
        return results
    
    def analyze_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """تحليل النتائج وتحديد الخطورة"""
        analysis = {
            "total_checks": len(results),
            "passed": 0,
            "failed": 0,
            "critical_issues": [],
            "high_issues": [],
            "medium_issues": [],
            "low_issues": []
        }
        
        for result in results:
            if result.get("success"):
                analysis["passed"] += 1
            else:
                analysis["failed"] += 1
                
                # تصنيف المشاكل حسب الخطورة
                for issue in result.get("issues", []):
                    if "CRITICAL" in issue or "SECURITY" in issue:
                        analysis["critical_issues"].append({
                            "check": result.get("check"),
                            "issue": issue
                        })
                    elif "Slow" in issue or "not found" in issue:
                        analysis["high_issues"].append({
                            "check": result.get("check"),
                            "issue": issue
                        })
                    else:
                        analysis["medium_issues"].append({
                            "check": result.get("check"),
                            "issue": issue
                        })
        
        return analysis
```

---

## المرحلة 3: فحوصات المحتوى والـ API (6 مهام - 1,200,000 توكن)

### المهمة 3.1: فحص الروابط المكسورة (Link Checker)
**المدة:** يوم واحد  
**الميزانية:** 200,000 توكن  

```python
# الملف: agents/web_monitor/core/link_integrity_scanner.py

import requests
from bs4 import BeautifulSoup
from typing import Set, List, Dict
from urllib.parse import urljoin, urlparse

class LinkIntegrityScanner:
    """فحص جميع الروابط في التطبيق"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.visited_urls: Set[str] = set()
        self.broken_links: List[Dict] = []
    
    def is_valid_url(self, url: str) -> bool:
        """التحقق من صحة الرابط"""
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)
    
    def get_all_links(self, url: str) -> Set[str]:
        """استخراج جميع الروابط من صفحة"""
        links = set()
        
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                
                # فقط الروابط الداخلية
                if self.base_url in full_url:
                    links.add(full_url)
        
        except Exception as e:
            print(f"Error getting links from {url}: {e}")
        
        return links
    
    async def scan_link(self, url: str, source_page: str = None) -> Dict:
        """فحص رابط واحد"""
        result = {
            "url": url,
            "source_page": source_page,
            "status": None,
            "broken": False,
            "error": None
        }
        
        try:
            response = requests.head(url, timeout=10, allow_redirects=True)
            result["status"] = response.status_code
            
            if response.status_code >= 400:
                result["broken"] = True
                result["error"] = f"HTTP {response.status_code}"
                self.broken_links.append(result)
        
        except requests.RequestException as e:
            result["broken"] = True
            result["error"] = str(e)
            self.broken_links.append(result)
        
        return result
    
    async def crawl_and_check(self, start_url: str = None, max_pages: int = 100) -> Dict:
        """الزحف وفحص جميع الروابط"""
        if not start_url:
            start_url = self.base_url
        
        to_visit = {start_url}
        
        while to_visit and len(self.visited_urls) < max_pages:
            url = to_visit.pop()
            
            if url in self.visited_urls:
                continue
            
            self.visited_urls.add(url)
            
            # فحص الرابط
            await self.scan_link(url)
            
            # استخراج روابط جديدة
            new_links = self.get_all_links(url)
            to_visit.update(new_links - self.visited_urls)
        
        return {
            "total_links_checked": len(self.visited_urls),
            "broken_links": len(self.broken_links),
            "broken_links_details": self.broken_links
        }
```

---

### المهمة 3.2: فحص النصوص غير المترجمة (i18n Scanner)
**المدة:** يوم واحد  
**الميزانية:** 200,000 توكن  
**الأولوية:** Critical (التطبيق يدعم 3 لغات)

```python
# الملف: agents/web_monitor/core/i18n_scanner.py

from playwright.sync_api import sync_playwright
from typing import Dict, List, Set
import re

class LocalizationInspector:
    """فحص اكتمال الترجمة (i18n)"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.supported_languages = ['ar', 'en', 'hi']  # من التطبيق
    
    async def scan_page_for_missing_translations(
        self, 
        page_url: str,
        language: str = 'ar'
    ) -> Dict[str, Any]:
        """
        فحص صفحة للنصوص غير المترجمة
        
        الطريقة:
        1. فتح الصفحة باللغة المحددة
        2. البحث عن أنماط نصوص غير مترجمة:
           - نصوص إنجليزية في الصفحة العربية
           - مفاتيح ترجمة ظاهرة (translation.key)
           - نصوص hardcoded
        """
        result = {
            "page_url": page_url,
            "language": language,
            "missing_translations": [],
            "hardcoded_texts": [],
            "translation_keys_exposed": []
        }
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                # تعيين اللغة (عبر localStorage أو cookie)
                page.goto(self.base_url)
                page.evaluate(f"localStorage.setItem('language', '{language}')")
                
                # فتح الصفحة المراد فحصها
                page.goto(page_url, wait_until="networkidle")
                
                # استخراج كل النصوص المرئية
                all_text = page.evaluate("""
                    () => {
                        return Array.from(document.body.querySelectorAll('*'))
                            .filter(el => el.childNodes.length === 1 && el.childNodes[0].nodeType === 3)
                            .map(el => el.textContent.trim())
                            .filter(text => text.length > 0);
                    }
                """)
                
                # البحث عن أنماط المشاكل
                for text in all_text:
                    # مفاتيح ترجمة ظاهرة (مثل: translation.welcome)
                    if re.match(r'^[a-z_]+\.[a-z_\.]+$', text.lower()):
                        result["translation_keys_exposed"].append(text)
                    
                    # نصوص إنجليزية في صفحة عربية
                    if language == 'ar':
                        if re.search(r'[a-zA-Z]{4,}', text):  # 4 أحرف إنجليزية متتالية
                            result["missing_translations"].append(text)
                    
                    # بحث عن علامات hardcoding
                    if "TODO" in text or "FIXME" in text:
                        result["hardcoded_texts"].append(text)
                
                # فحص محتوى نماذج الإدخال
                placeholders = page.evaluate("""
                    () => {
                        return Array.from(document.querySelectorAll('input[placeholder], textarea[placeholder]'))
                            .map(el => el.getAttribute('placeholder'));
                    }
                """)
                
                for placeholder in placeholders:
                    if language == 'ar' and re.search(r'[a-zA-Z]{4,}', placeholder):
                        result["missing_translations"].append(f"Placeholder: {placeholder}")
                
            except Exception as e:
                result["error"] = str(e)
            finally:
                browser.close()
        
        return result
    
    async def scan_all_languages(self, pages: List[str]) -> Dict:
        """فحص جميع اللغات لكل الصفحات"""
        results = []
        
        for language in self.supported_languages:
            for page_url in pages:
                page_result = await self.scan_page_for_missing_translations(
                    page_url, 
                    language
                )
                results.append(page_result)
        
        # تجميع النتائج
        summary = {
            "total_pages_checked": len(pages) * len(self.supported_languages),
            "pages_with_issues": 0,
            "total_missing_translations": 0,
            "critical_pages": []
        }
        
        for result in results:
            if result.get("missing_translations") or result.get("translation_keys_exposed"):
                summary["pages_with_issues"] += 1
                summary["total_missing_translations"] += len(result.get("missing_translations", []))
                
                if len(result.get("missing_translations", [])) > 5:
                    summary["critical_pages"].append(result)
        
        return summary
```

---

### المهمة 3.3: فحص APIs غير المستخدمة
**المدة:** يوم واحد  
**الميزانية:** 200,000 توكن  

```python
# الملف: agents/web_monitor/core/api_usage_diff.py

import requests
import re
from typing import Set, Dict, List

class APIUsageAuditor:
    """تحليل استخدام APIs وكشف الـ endpoints الميتة"""
    
    def __init__(self, base_url: str, server_path: str):
        self.base_url = base_url
        self.server_path = server_path  # /home/administrator/Bot.v4/server
    
    def discover_defined_endpoints(self) -> Set[str]:
        """
        استكشاف جميع الـ endpoints المعرفة في الكود
        
        الطريقة:
        1. قراءة ملفات routes في server/routes/
        2. استخراج كل app.get, app.post, router.get, etc
        """
        endpoints = set()
        
        # قراءة ملف routes الرئيسي
        # ملاحظة: هذا سيتم تنفيذه على السيرفر عبر Bridge Tool
        try:
            with open(f"{self.server_path}/routes.ts", 'r') as f:
                content = f.read()
                
                # استخراج المسارات
                # Patterns: app.get("/api/users", ...), router.post("/login", ...)
                patterns = [
                    r'\.get\(["\']([^"\']+)["\']',
                    r'\.post\(["\']([^"\']+)["\']',
                    r'\.put\(["\']([^"\']+)["\']',
                    r'\.delete\(["\']([^"\']+)["\']',
                    r'\.patch\(["\']([^"\']+)["\']'
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    endpoints.update(matches)
        
        except Exception as e:
            print(f"Error reading routes: {e}")
        
        return endpoints
    
    def test_endpoint_accessibility(self, endpoint: str) -> Dict:
        """اختبار الوصول لـ endpoint"""
        result = {
            "endpoint": endpoint,
            "accessible": False,
            "status_code": None,
            "response_time_ms": 0,
            "error": None
        }
        
        try:
            import time
            start = time.time()
            
            response = requests.get(
                f"{self.base_url}{endpoint}",
                timeout=10
            )
            
            response_time = (time.time() - start) * 1000
            
            result["accessible"] = True
            result["status_code"] = response.status_code
            result["response_time_ms"] = response_time
        
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    async def audit_all_endpoints(self) -> Dict:
        """تدقيق جميع الـ endpoints"""
        defined_endpoints = self.discover_defined_endpoints()
        
        results = {
            "total_endpoints": len(defined_endpoints),
            "accessible": 0,
            "dead_endpoints": [],
            "slow_endpoints": [],
            "error_endpoints": []
        }
        
        for endpoint in defined_endpoints:
            test_result = self.test_endpoint_accessibility(endpoint)
            
            if test_result["accessible"]:
                results["accessible"] += 1
                
                # فحص البطء
                if test_result["response_time_ms"] > 1000:
                    results["slow_endpoints"].append(test_result)
            else:
                results["dead_endpoints"].append(test_result)
                
                # تصنيف الأخطاء
                if test_result["error"]:
                    results["error_endpoints"].append(test_result)
        
        return results
```

---

(يتبع...)

---

## 📝 ملخص الـ 33 مهمة

### توزيع المهام حسب المراحل

| المرحلة | عدد المهام | الميزانية (توكن) | المدة |
|---------|-----------|------------------|-------|
| 0. الإعداد والبحث | 5 | 1,000,000 | 3 أيام |
| 1. البنية الأساسية | 3 | 600,000 | 2 أيام |
| 2. Synthetic Monitoring | 4 | 800,000 | 3 أيام |
| 3. فحوصات المحتوى والـ API | 6 | 1,200,000 | 4 أيام |
| 4. الأداء والأمان | 5 | 1,000,000 | 3 أيام |
| 5. التقارير واللوحات | 4 | 800,000 | 2 أيام |
| 6. التعزيز والتسليم | 6 | 1,200,000 | 5 أيام |
| **المجموع** | **33** | **6,600,000** | **22 يوم** |

---

## 🚀 دليل النشر على السيرفر

### الخطوة 1: التطوير على Replit

```bash
# تطوير الكود محلياً
cd agents/web_monitor/
# ... تطوير الملفات

# اختبار محلي
python web_monitor_agent.py
```

### الخطوة 2: النشر عبر Bridge Tool

```bash
# 1. النسخ الاحتياطي
python3 bridge_tool/cli.py exec "python /srv/ai_system/agents/backup_recovery.py"

# 2. النشر
python3 bridge_tool/cli.py push

# 3. التحقق
python3 bridge_tool/cli.py status --detailed
```

### الخطوة 3: تشغيل الوكيل على السيرفر

```bash
# إضافة إلى systemd
python3 bridge_tool/cli.py exec "systemctl restart ai_agents.service"

# التحقق من السجلات
python3 bridge_tool/cli.py exec "tail -f /srv/ai_system/logs/web_monitor.log"
```

---

## ✅ معايير الإنجاز النهائية

**الوكيل يعتبر مكتمل عندما:**

- [ ] جميع الـ 33 مهمة مكتملة
- [ ] جميع الوظائف الـ 40 تعمل
- [ ] التكامل مع الوكلاء 1-6 يعمل
- [ ] قاعدة البيانات SQLite تعمل
- [ ] التقارير تُرسل للوكيل الأب
- [ ] الوكيل يعمل 24/7 على السيرفر
- [ ] التوثيق الكامل منجز
- [ ] الاختبارات تمر 100%
- [ ] لا أخطاء LSP
- [ ] النسخة الاحتياطية منشأة

---

**نهاية الملف التكميلي**
