/**
 * Navigation Controller - Mobile Menu & Bottom Nav
 * ============================================================================
 * Compliance: WCAG 2.1 §1.2.1 (Keyboard), §2.4.3 (Focus Order)
 * Features:
 * - Toggle hamburger menu
 * - Keyboard navigation (Tab, Shift+Tab, Enter, Escape)
 * - Focus management
 * - Active tab synchronization
 * ============================================================================
 */

(function() {
  'use strict';
  
  // DOM Elements
  const hamburger = document.querySelector('.navbar__hamburger');
  const menu = document.querySelector('.navbar__menu');
  const overlay = document.querySelector('.navbar__overlay');
  const menuButtons = document.querySelectorAll('.navbar__menu-button');
  const bottomNavButtons = document.querySelectorAll('.bottom-nav__button');
  const tabButtons = document.querySelectorAll('.navbar__tab-button');
  
  // State
  let isMenuOpen = false;
  
  // -------------------------------------------------------------------------
  // 1. Menu Toggle Functions
  // -------------------------------------------------------------------------
  
  function openMenu() {
    isMenuOpen = true;
    hamburger.setAttribute('aria-expanded', 'true');
    menu.classList.add('is-open');
    overlay.classList.add('is-visible');
    
    // Focus first menu item
    const firstMenuItem = menu.querySelector('.navbar__menu-button');
    if (firstMenuItem) {
      firstMenuItem.focus();
    }
    
    // Trap focus in menu
    document.addEventListener('keydown', handleMenuKeydown);
  }
  
  function closeMenu() {
    isMenuOpen = false;
    hamburger.setAttribute('aria-expanded', 'false');
    menu.classList.remove('is-open');
    overlay.classList.remove('is-visible');
    
    // Return focus to hamburger
    hamburger.focus();
    
    // Remove focus trap
    document.removeEventListener('keydown', handleMenuKeydown);
  }
  
  function toggleMenu() {
    if (isMenuOpen) {
      closeMenu();
    } else {
      openMenu();
    }
  }
  
  // -------------------------------------------------------------------------
  // 2. Keyboard Navigation
  // -------------------------------------------------------------------------
  
  function handleMenuKeydown(e) {
    // ESC - Close menu
    if (e.key === 'Escape') {
      closeMenu();
      return;
    }
    
    // Tab / Shift+Tab - Focus trap
    if (e.key === 'Tab') {
      const focusableElements = menu.querySelectorAll(
        '.navbar__menu-button:not([disabled])'
      );
      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];
      
      if (e.shiftKey) {
        // Shift+Tab - Move backwards
        if (document.activeElement === firstElement) {
          lastElement.focus();
          e.preventDefault();
        }
      } else {
        // Tab - Move forwards
        if (document.activeElement === lastElement) {
          firstElement.focus();
          e.preventDefault();
        }
      }
    }
  }
  
  // -------------------------------------------------------------------------
  // 3. Tab Selection & Synchronization
  // -------------------------------------------------------------------------
  
  function setActiveTab(tabId) {
    // Remove active from all buttons
    [...menuButtons, ...bottomNavButtons, ...tabButtons].forEach(btn => {
      btn.classList.remove('active');
      btn.setAttribute('aria-selected', 'false');
    });
    
    // Add active to selected tab (all instances)
    const selector = `[data-tab-target="${tabId}"]`;
    document.querySelectorAll(selector).forEach(btn => {
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');
    });
    
    // Close mobile menu after selection
    if (isMenuOpen) {
      closeMenu();
    }
    
    // Save to localStorage
    localStorage.setItem('activeTab', tabId);
  }
  
  // -------------------------------------------------------------------------
  // 4. Event Listeners
  // -------------------------------------------------------------------------
  
  // Hamburger click
  if (hamburger) {
    hamburger.addEventListener('click', toggleMenu);
  }
  
  // Overlay click - close menu
  if (overlay) {
    overlay.addEventListener('click', closeMenu);
  }
  
  // Menu buttons
  menuButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const tabId = btn.getAttribute('data-tab-target');
      if (tabId) {
        setActiveTab(tabId);
      }
    });
  });
  
  // Bottom nav buttons
  bottomNavButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const tabId = btn.getAttribute('data-tab-target');
      if (tabId) {
        setActiveTab(tabId);
      }
    });
  });
  
  // Desktop tab buttons
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const tabId = btn.getAttribute('data-tab-target');
      if (tabId) {
        setActiveTab(tabId);
      }
    });
  });
  
  // -------------------------------------------------------------------------
  // 5. Window Resize - Close menu on desktop
  // -------------------------------------------------------------------------
  
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      if (window.innerWidth >= 992 && isMenuOpen) {
        closeMenu();
      }
    }, 250);
  });
  
  // -------------------------------------------------------------------------
  // 6. Initialize - Restore active tab
  // -------------------------------------------------------------------------
  
  function init() {
    const savedTab = localStorage.getItem('activeTab');
    if (savedTab) {
      setActiveTab(savedTab);
    } else {
      // Set first tab as active
      setActiveTab('dashboard');
    }
  }
  
  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
  
})();
