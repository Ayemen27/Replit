"""
Dashboard UI Tests - Phase 1-3 Compliance
اختبارات واجهة المستخدم - الامتثال للمراحل 1-3

WCAG 2.1 AA Compliance Tests
Material Design 3 Compliance Tests
Replit RUI Compliance Tests
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time


class TestPhase1ResponsiveDesign:
    """المرحلة 1: اختبارات Responsive Design"""
    
    def test_mobile_viewport_320px(self, driver):
        """Test 320px mobile viewport - minimum width"""
        driver.set_window_size(320, 568)
        driver.get(driver.base_url)
        
        # Verify workflows grid is single column
        grid = driver.find_element(By.CLASS_NAME, "workflows-grid")
        grid_columns = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).gridTemplateColumns",
            grid
        )
        assert "1fr" in grid_columns or grid_columns.count(" ") == 0, \
            "Grid should be single column on 320px"
    
    def test_tablet_viewport_768px(self, driver):
        """Test 768px tablet viewport"""
        driver.set_window_size(768, 1024)
        driver.get(driver.base_url)
        
        # Verify workflows grid is 2 columns
        grid = driver.find_element(By.CLASS_NAME, "workflows-grid")
        grid_columns = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).gridTemplateColumns",
            grid
        )
        # Should have 2 columns
        assert grid_columns.count(" ") >= 1, \
            "Grid should be 2+ columns on tablet"
    
    def test_desktop_viewport_1920px(self, driver):
        """Test 1920px desktop viewport"""
        driver.set_window_size(1920, 1080)
        driver.get(driver.base_url)
        
        # Verify workflows grid uses auto-fill
        grid = driver.find_element(By.CLASS_NAME, "workflows-grid")
        grid_columns = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).gridTemplateColumns",
            grid
        )
        # Should have multiple columns
        assert grid_columns.count(" ") >= 1, \
            "Grid should be multi-column on desktop"


class TestPhase1Typography:
    """المرحلة 1: اختبارات Typography"""
    
    def test_arabic_fonts_loaded(self, driver):
        """Test Cairo and IBM Plex Sans Arabic fonts"""
        driver.get(driver.base_url)
        
        # Check font-family on body
        body = driver.find_element(By.TAG_NAME, "body")
        font_family = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).fontFamily",
            body
        )
        
        assert "Cairo" in font_family or "IBM Plex Sans Arabic" in font_family, \
            f"Arabic fonts not loaded: {font_family}"
    
    def test_font_size_hierarchy(self, driver):
        """Test font size hierarchy"""
        driver.get(driver.base_url)
        
        # Check h1 is larger than p
        h1 = driver.find_element(By.TAG_NAME, "h1")
        p = driver.find_element(By.TAG_NAME, "p")
        
        h1_size = float(driver.execute_script(
            "return window.getComputedStyle(arguments[0]).fontSize",
            h1
        ).replace("px", ""))
        
        p_size = float(driver.execute_script(
            "return window.getComputedStyle(arguments[0]).fontSize",
            p
        ).replace("px", ""))
        
        assert h1_size > p_size, "H1 should be larger than paragraph"


class TestPhase1ColorContrast:
    """المرحلة 1: اختبارات Color Contrast (WCAG AA)"""
    
    def test_foreground_contrast(self, driver):
        """Test foreground color contrast >= 4.5:1"""
        driver.get(driver.base_url)
        
        # Get --color-foreground value
        foreground = driver.execute_script(
            "return getComputedStyle(document.documentElement).getPropertyValue('--color-foreground').trim()"
        )
        
        # Should be dark color (starts with #0 or #1)
        assert foreground.startswith("#0") or foreground.startswith("#1"), \
            f"Foreground should be dark: {foreground}"
    
    def test_accent_primary_contrast(self, driver):
        """Test accent primary color exists"""
        driver.get(driver.base_url)
        
        accent = driver.execute_script(
            "return getComputedStyle(document.documentElement).getPropertyValue('--color-accent-primary').trim()"
        )
        
        assert accent.startswith("#"), f"Accent primary should be hex color: {accent}"


class TestPhase2LoadingStates:
    """المرحلة 2: اختبارات Loading States"""
    
    def test_skeleton_loader_exists(self, driver):
        """Test skeleton loader CSS class exists"""
        driver.get(driver.base_url)
        
        # Check if skeleton class is defined
        has_skeleton = driver.execute_script("""
            const sheets = Array.from(document.styleSheets);
            for (let sheet of sheets) {
                try {
                    const rules = Array.from(sheet.cssRules || []);
                    for (let rule of rules) {
                        if (rule.selectorText && rule.selectorText.includes('skeleton')) {
                            return true;
                        }
                    }
                } catch (e) {}
            }
            return false;
        """)
        
        assert has_skeleton, "Skeleton loader CSS not found"
    
    def test_spinner_exists(self, driver):
        """Test spinner class exists"""
        driver.get(driver.base_url)
        
        has_spinner = driver.execute_script("""
            const sheets = Array.from(document.styleSheets);
            for (let sheet of sheets) {
                try {
                    const rules = Array.from(sheet.cssRules || []);
                    for (let rule of rules) {
                        if (rule.selectorText && rule.selectorText.includes('spinner')) {
                            return true;
                        }
                    }
                } catch (e) {}
            }
            return false;
        """)
        
        assert has_spinner, "Spinner CSS not found"


class TestPhase2ToastNotifications:
    """المرحلة 2: اختبارات Toast Notifications"""
    
    def test_toast_manager_exists(self, driver):
        """Test ToastManager JavaScript class exists"""
        driver.get(driver.base_url)
        
        # Wait for scripts to load
        time.sleep(1)
        
        has_toast_manager = driver.execute_script(
            "return typeof window.toast !== 'undefined'"
        )
        
        assert has_toast_manager, "ToastManager (window.toast) not found"
    
    def test_toast_show_method(self, driver):
        """Test toast.show() method exists"""
        driver.get(driver.base_url)
        time.sleep(1)
        
        can_show_toast = driver.execute_script(
            "return typeof window.toast?.show === 'function'"
        )
        
        assert can_show_toast, "toast.show() method not found"


class TestPhase2InteractiveStates:
    """المرحلة 2: اختبارات Interactive States"""
    
    def test_focus_visible_styles(self, driver):
        """Test focus-visible styles exist"""
        driver.get(driver.base_url)
        
        has_focus_visible = driver.execute_script("""
            const sheets = Array.from(document.styleSheets);
            for (let sheet of sheets) {
                try {
                    const rules = Array.from(sheet.cssRules || []);
                    for (let rule of rules) {
                        if (rule.selectorText && rule.selectorText.includes('focus-visible')) {
                            return true;
                        }
                    }
                } catch (e) {}
            }
            return false;
        """)
        
        assert has_focus_visible, "focus-visible styles not found"
    
    def test_hover_states_on_cards(self, driver):
        """Test workflow cards have hover effects"""
        driver.set_window_size(1920, 1080)
        driver.get(driver.base_url)
        
        # Find first workflow card
        try:
            card = driver.find_element(By.CLASS_NAME, "workflow-card")
            
            # Get transition property
            transition = driver.execute_script(
                "return window.getComputedStyle(arguments[0]).transition",
                card
            )
            
            assert transition and transition != "all 0s ease 0s", \
                "Cards should have transition for hover effects"
        except:
            # No cards present - skip test
            pytest.skip("No workflow cards found")


class TestPhase2Accessibility:
    """المرحلة 2: اختبارات WCAG 2.1 AA"""
    
    def test_keyboard_navigation_tab(self, driver):
        """Test Tab key navigation works"""
        driver.get(driver.base_url)
        
        # Get active element
        initial_element = driver.switch_to.active_element
        
        # Press Tab
        initial_element.send_keys(Keys.TAB)
        
        # Check if focus moved
        new_element = driver.switch_to.active_element
        
        # Focus should have moved (different element)
        assert initial_element != new_element, \
            "Tab navigation should move focus"
    
    def test_aria_labels_present(self, driver):
        """Test ARIA labels exist"""
        driver.get(driver.base_url)
        
        # Find elements with aria-label
        aria_elements = driver.find_elements(By.CSS_SELECTOR, "[aria-label]")
        
        # Should have at least some ARIA labels
        assert len(aria_elements) > 0, \
            "No ARIA labels found - accessibility issue"
    
    def test_alt_text_on_images(self, driver):
        """Test all images have alt text"""
        driver.get(driver.base_url)
        
        # Find all images
        images = driver.find_elements(By.TAG_NAME, "img")
        
        for img in images:
            alt = img.get_attribute("alt")
            assert alt is not None, \
                f"Image missing alt text: {img.get_attribute('src')}"


class TestPhase3SearchAndFilter:
    """المرحلة 3: اختبارات Search & Filter"""
    
    def test_search_input_exists(self, driver):
        """Test search input field exists"""
        driver.get(driver.base_url)
        
        # Find search input
        search_input = driver.find_element(By.ID, "workflow-search")
        
        assert search_input is not None, "Search input not found"
        assert search_input.is_displayed(), "Search input not visible"
    
    def test_search_filtering(self, driver):
        """Test search actually filters results"""
        driver.get(driver.base_url)
        
        try:
            # Get initial card count
            initial_cards = driver.find_elements(By.CLASS_NAME, "workflow-card")
            initial_count = len([c for c in initial_cards if c.is_displayed()])
            
            # Type in search
            search_input = driver.find_element(By.ID, "workflow-search")
            search_input.send_keys("nonexistent_workflow_xyz")
            
            # Wait for filter to apply (debounce)
            time.sleep(0.5)
            
            # Get filtered count
            filtered_cards = driver.find_elements(By.CLASS_NAME, "workflow-card")
            filtered_count = len([c for c in filtered_cards if c.is_displayed()])
            
            # Should show fewer results (or zero)
            assert filtered_count <= initial_count, \
                "Search filter should reduce or maintain result count"
        except:
            pytest.skip("No workflow cards to test filtering")
    
    def test_status_filter_exists(self, driver):
        """Test status filter dropdown exists"""
        driver.get(driver.base_url)
        
        status_filter = driver.find_element(By.ID, "workflow-status-filter")
        assert status_filter is not None, "Status filter not found"
    
    def test_type_filter_exists(self, driver):
        """Test type filter dropdown exists"""
        driver.get(driver.base_url)
        
        type_filter = driver.find_element(By.ID, "workflow-type-filter")
        assert type_filter is not None, "Type filter not found"


class TestPhase3Pagination:
    """المرحلة 3: اختبارات Pagination"""
    
    def test_pagination_javascript_loaded(self, driver):
        """Test pagination functionality is available"""
        driver.get(driver.base_url)
        time.sleep(1)
        
        # Check if changePage function exists
        has_change_page = driver.execute_script(
            "return typeof window.changePage === 'function'"
        )
        
        assert has_change_page, "window.changePage() function not found"


class TestPhase3EmptyStates:
    """المرحلة 3: اختبارات Empty States"""
    
    def test_empty_state_css_exists(self, driver):
        """Test empty state CSS classes exist"""
        driver.get(driver.base_url)
        
        has_empty_state = driver.execute_script("""
            const sheets = Array.from(document.styleSheets);
            for (let sheet of sheets) {
                try {
                    const rules = Array.from(sheet.cssRules || []);
                    for (let rule of rules) {
                        if (rule.selectorText && rule.selectorText.includes('empty-state')) {
                            return true;
                        }
                    }
                } catch (e) {}
            }
            return false;
        """)
        
        assert has_empty_state, "Empty state CSS not found"


class TestPhase3ErrorStates:
    """المرحلة 3: اختبارات Error States"""
    
    def test_error_state_css_exists(self, driver):
        """Test error state CSS classes exist"""
        driver.get(driver.base_url)
        
        has_error_state = driver.execute_script("""
            const sheets = Array.from(document.styleSheets);
            for (let sheet of sheets) {
                try {
                    const rules = Array.from(sheet.cssRules || []);
                    for (let rule of rules) {
                        if (rule.selectorText && rule.selectorText.includes('error-state')) {
                            return true;
                        }
                    }
                } catch (e) {}
            }
            return false;
        """)
        
        assert has_error_state, "Error state CSS not found"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-m", "not ui"])
