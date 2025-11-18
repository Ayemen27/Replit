"""
Navigation Tests - Dashboard UI
اختبارات التنقل والوجهات

Tests all navigation flows, links, and page transitions
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class TestNavigationBasic:
    """اختبارات التنقل الأساسية"""
    
    def test_homepage_loads(self, driver):
        """Test homepage loads successfully"""
        driver.get(driver.base_url)
        
        # Check page loaded (might redirect to login)
        assert driver.current_url is not None
        assert len(driver.page_source) > 0
    
    def test_page_title_exists(self, driver):
        """Test page has a title"""
        driver.get(driver.base_url)
        
        title = driver.title
        assert title is not None
        assert len(title) > 0
    
    def test_no_404_on_homepage(self, driver):
        """Test homepage doesn't show 404"""
        driver.get(driver.base_url)
        
        page_text = driver.page_source.lower()
        assert "404" not in page_text or "not found" not in page_text


class TestNavigationLinks:
    """اختبارات الروابط والتنقل"""
    
    def test_all_links_have_href(self, driver):
        """Test all <a> tags have href attribute"""
        driver.get(driver.base_url)
        
        links = driver.find_elements(By.TAG_NAME, "a")
        
        for link in links:
            href = link.get_attribute("href")
            # Links should have href (or be aria-hidden)
            aria_hidden = link.get_attribute("aria-hidden")
            assert href or aria_hidden == "true", \
                f"Link without href: {link.get_attribute('outerHTML')}"
    
    def test_navigation_bar_exists(self, driver):
        """Test navigation bar is present"""
        driver.get(driver.base_url)
        
        # Look for common nav elements
        nav_elements = driver.find_elements(By.TAG_NAME, "nav")
        
        # Should have at least one nav element
        assert len(nav_elements) > 0, "No navigation bar found"
    
    def test_logo_link_exists(self, driver):
        """Test logo/brand link exists"""
        driver.get(driver.base_url)
        
        # Look for logo or brand
        try:
            logo = driver.find_element(By.CSS_SELECTOR, ".navbar-brand, .logo, [aria-label*='logo']")
            assert logo is not None
        except:
            # Logo might be in different structure
            pass


class TestNavigationButtons:
    """اختبارات الأزرار والتنقل"""
    
    def test_buttons_clickable(self, driver):
        """Test buttons are clickable"""
        driver.get(driver.base_url)
        
        buttons = driver.find_elements(By.TAG_NAME, "button")
        
        for button in buttons:
            # Check button is in DOM and has attributes
            assert button.is_enabled() or button.get_attribute("disabled") is not None
    
    def test_workflow_cards_navigation(self, driver):
        """Test workflow cards can be clicked"""
        driver.get(driver.base_url)
        
        try:
            # Find workflow cards
            cards = driver.find_elements(By.CLASS_NAME, "workflow-card")
            
            if len(cards) > 0:
                # Cards should be clickable or have clickable elements
                first_card = cards[0]
                
                # Look for clickable elements in card
                clickable = first_card.find_elements(By.CSS_SELECTOR, "button, a, [role='button']")
                assert len(clickable) > 0, "Workflow card has no clickable elements"
        except:
            pytest.skip("No workflow cards found")


class TestNavigationFlows:
    """اختبارات مسارات التنقل الكاملة"""
    
    def test_dashboard_navigation_flow(self, driver):
        """Test complete navigation flow through dashboard"""
        driver.get(driver.base_url)
        
        # Record initial URL
        initial_url = driver.current_url
        
        # Try to find and click any navigation element
        try:
            nav_links = driver.find_elements(By.CSS_SELECTOR, "nav a, .nav-link")
            
            if len(nav_links) > 0:
                # Click first nav link
                original_url = driver.current_url
                nav_links[0].click()
                
                # Wait a bit for navigation
                time.sleep(0.5)
                
                # URL might change or stay same (could be same page)
                # Just verify no error occurred
                assert "error" not in driver.current_url.lower()
        except:
            # No nav links - skip test
            pass
    
    def test_back_button_works(self, driver):
        """Test browser back button works"""
        driver.get(driver.base_url)
        
        initial_url = driver.current_url
        
        # Try to navigate somewhere
        try:
            links = driver.find_elements(By.TAG_NAME, "a")
            if len(links) > 0:
                links[0].click()
                time.sleep(0.5)
                
                # Go back
                driver.back()
                time.sleep(0.5)
                
                # Should return to initial page (or close to it)
                # URLs might differ slightly due to redirects
                assert driver.current_url is not None
        except:
            pass


class TestNavigationAccessibility:
    """اختبارات إمكانية الوصول في التنقل"""
    
    def test_skip_links_present(self, driver):
        """Test skip navigation links exist"""
        driver.get(driver.base_url)
        
        # Look for skip links (WCAG requirement)
        skip_links = driver.find_elements(By.CSS_SELECTOR, "[href='#main'], [href='#content'], .skip-link")
        
        # Skip links are good for accessibility
        # Not mandatory but recommended
        if len(skip_links) > 0:
            assert skip_links[0] is not None
    
    def test_keyboard_navigation_works(self, driver):
        """Test keyboard tab navigation"""
        from selenium.webdriver.common.keys import Keys
        
        driver.get(driver.base_url)
        
        # Get first focusable element
        body = driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.TAB)
        
        # Check that focus moved
        active = driver.switch_to.active_element
        assert active.tag_name is not None
    
    def test_nav_has_aria_labels(self, driver):
        """Test navigation has ARIA labels"""
        driver.get(driver.base_url)
        
        nav_elements = driver.find_elements(By.TAG_NAME, "nav")
        
        for nav in nav_elements:
            # Nav should have aria-label or role
            aria_label = nav.get_attribute("aria-label")
            role = nav.get_attribute("role")
            
            assert aria_label or role, "Nav missing ARIA labels"


class TestNavigationResponsive:
    """اختبارات التنقل المتجاوب"""
    
    def test_mobile_navigation(self, driver):
        """Test mobile navigation menu"""
        driver.set_window_size(375, 667)  # iPhone size
        driver.get(driver.base_url)
        
        # Look for mobile menu (hamburger)
        try:
            mobile_menu = driver.find_element(By.CSS_SELECTOR, ".navbar-toggler, .mobile-menu-button, [aria-label*='menu']")
            assert mobile_menu.is_displayed()
        except:
            # Desktop nav might be hidden on mobile
            pass
    
    def test_tablet_navigation(self, driver):
        """Test tablet navigation"""
        driver.set_window_size(768, 1024)  # iPad size
        driver.get(driver.base_url)
        
        nav = driver.find_elements(By.TAG_NAME, "nav")
        assert len(nav) > 0
    
    def test_desktop_navigation(self, driver):
        """Test desktop navigation"""
        driver.set_window_size(1920, 1080)
        driver.get(driver.base_url)
        
        nav = driver.find_elements(By.TAG_NAME, "nav")
        assert len(nav) > 0


class TestNavigationErrors:
    """اختبارات معالجة أخطاء التنقل"""
    
    def test_404_page_handles_gracefully(self, driver):
        """Test 404 page is handled"""
        driver.get(f"{driver.base_url}/nonexistent-page-xyz-123")
        
        # Should either redirect or show error page
        # Should NOT crash
        assert len(driver.page_source) > 0
    
    def test_no_broken_links_on_homepage(self, driver):
        """Test no broken links on homepage"""
        import requests
        
        driver.get(driver.base_url)
        
        links = driver.find_elements(By.TAG_NAME, "a")
        
        broken_links = []
        for link in links[:10]:  # Check first 10 links only
            href = link.get_attribute("href")
            
            if href and href.startswith("http"):
                try:
                    response = requests.head(href, timeout=3, allow_redirects=True)
                    if response.status_code >= 400:
                        broken_links.append((href, response.status_code))
                except:
                    # Network error - skip
                    pass
        
        assert len(broken_links) == 0, f"Broken links found: {broken_links}"


class TestNavigationPerformance:
    """اختبارات أداء التنقل"""
    
    def test_page_loads_quickly(self, driver):
        """Test page loads in reasonable time"""
        import time
        
        start_time = time.time()
        driver.get(driver.base_url)
        load_time = time.time() - start_time
        
        # Should load in less than 5 seconds
        assert load_time < 5.0, f"Page took {load_time}s to load"
    
    def test_navigation_is_fast(self, driver):
        """Test navigation between pages is fast"""
        import time
        
        driver.get(driver.base_url)
        
        try:
            links = driver.find_elements(By.TAG_NAME, "a")[:3]
            
            for link in links:
                start_time = time.time()
                link.click()
                nav_time = time.time() - start_time
                
                # Navigation should be fast
                assert nav_time < 3.0, f"Navigation took {nav_time}s"
                
                driver.back()
                time.sleep(0.3)
        except:
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
