/**
 * Workflow Cards - Touch & Keyboard Interactions
 * تفاعلات بطاقات سير العمل
 * 
 * Features:
 * - Swipe left/right to reveal/hide action buttons
 * - Keyboard navigation support
 * - Snap-back animation
 * - RTL support
 * 
 * Compliance:
 * - WCAG 2.1 AA (Keyboard accessible)
 * - Touch-optimized for mobile devices
 * 
 * Version: 1.0.0
 * Last Updated: 2025-11-16
 */

(function() {
  'use strict';
  
  // Configuration
  const SWIPE_THRESHOLD = 50; // Minimum distance to trigger swipe (px)
  const SNAP_BACK_DELAY = 3000; // Auto close after 3 seconds
  
  // State
  let currentSwipedCard = null;
  let snapBackTimer = null;
  
  /**
   * Initialize workflow cards interactions
   */
  function initWorkflowCards() {
    const cards = document.querySelectorAll('.workflow-card');
    
    if (cards.length === 0) {
      return; // No cards on page
    }
    
    cards.forEach(card => {
      initTouchSwipe(card);
      initKeyboardActions(card);
    });
    
    // Close swiped card when clicking outside
    document.addEventListener('click', handleOutsideClick);
  }
  
  /**
   * Initialize touch/pointer swipe for a card
   */
  function initTouchSwipe(card) {
    const swipeable = card.querySelector('.workflow-card__swipeable');
    if (!swipeable) return;
    
    let startX = 0;
    let currentX = 0;
    let isDragging = false;
    let isRTL = document.documentElement.getAttribute('dir') === 'rtl';
    
    // Use pointer events for better cross-device support
    swipeable.addEventListener('pointerdown', (e) => {
      // Only handle primary pointer (no multi-touch)
      if (!e.isPrimary) return;
      
      isDragging = true;
      startX = e.clientX;
      currentX = e.clientX;
      
      // Disable transitions during drag
      swipeable.style.transition = 'none';
      
      // Capture pointer to continue tracking even if it leaves element
      swipeable.setPointerCapture(e.pointerId);
    });
    
    swipeable.addEventListener('pointermove', (e) => {
      if (!isDragging) return;
      
      currentX = e.clientX;
      const deltaX = currentX - startX;
      
      // Apply transform based on drag
      // Limit drag distance to prevent excessive movement
      const maxDrag = 100;
      const limitedDelta = Math.max(-maxDrag, Math.min(maxDrag, deltaX));
      
      // Reverse for RTL
      const transformDelta = isRTL ? -limitedDelta : limitedDelta;
      swipeable.style.transform = `translateX(${transformDelta}px)`;
    });
    
    swipeable.addEventListener('pointerup', (e) => {
      if (!isDragging) return;
      
      isDragging = false;
      const deltaX = currentX - startX;
      
      // Re-enable transitions
      swipeable.style.transition = '';
      swipeable.style.transform = '';
      
      // Determine if swipe threshold was met
      const absDistance = Math.abs(deltaX);
      
      if (absDistance >= SWIPE_THRESHOLD) {
        // Swipe left (or right in RTL) = reveal actions
        if ((deltaX < 0 && !isRTL) || (deltaX > 0 && isRTL)) {
          openCard(card);
        } else {
          // Swipe right (or left in RTL) = close actions
          closeCard(card);
        }
      }
    });
    
    swipeable.addEventListener('pointercancel', () => {
      isDragging = false;
      swipeable.style.transition = '';
      swipeable.style.transform = '';
    });
  }
  
  /**
   * Initialize keyboard actions for card
   */
  function initKeyboardActions(card) {
    const actionsContainer = card.querySelector('.workflow-card__actions');
    if (!actionsContainer) return;
    
    const actionButtons = actionsContainer.querySelectorAll('.action-btn');
    
    actionButtons.forEach(btn => {
      // Make buttons keyboard accessible
      btn.setAttribute('tabindex', '0');
      
      // Handle Enter/Space key
      btn.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          btn.click();
        }
      });
      
      // Show actions when button receives focus (keyboard navigation)
      btn.addEventListener('focus', () => {
        openCard(card, false); // Don't auto-close on focus
      });
    });
  }
  
  /**
   * Open card actions
   */
  function openCard(card, autoClose = true) {
    // Close any previously opened card
    if (currentSwipedCard && currentSwipedCard !== card) {
      closeCard(currentSwipedCard);
    }
    
    // Add class to both card and swipeable for proper styling
    const swipeable = card.querySelector('.workflow-card__swipeable');
    card.classList.add('is-swiped');
    if (swipeable) {
      swipeable.classList.add('is-swiped');
    }
    currentSwipedCard = card;
    
    // Clear existing timer
    if (snapBackTimer) {
      clearTimeout(snapBackTimer);
      snapBackTimer = null;
    }
    
    // Auto-close after delay (unless keyboard focus)
    if (autoClose) {
      snapBackTimer = setTimeout(() => {
        closeCard(card);
      }, SNAP_BACK_DELAY);
    }
    
    // Update ARIA
    card.setAttribute('aria-expanded', 'true');
  }
  
  /**
   * Close card actions
   */
  function closeCard(card) {
    const swipeable = card.querySelector('.workflow-card__swipeable');
    card.classList.remove('is-swiped');
    if (swipeable) {
      swipeable.classList.remove('is-swiped');
    }
    
    if (currentSwipedCard === card) {
      currentSwipedCard = null;
    }
    
    if (snapBackTimer) {
      clearTimeout(snapBackTimer);
      snapBackTimer = null;
    }
    
    // Update ARIA
    card.setAttribute('aria-expanded', 'false');
  }
  
  /**
   * Handle clicks outside cards to close them
   */
  function handleOutsideClick(e) {
    if (!currentSwipedCard) return;
    
    // Check if click was outside the current card
    if (!currentSwipedCard.contains(e.target)) {
      closeCard(currentSwipedCard);
    }
  }
  
  /**
   * Cleanup function
   */
  function cleanup() {
    document.removeEventListener('click', handleOutsideClick);
    
    if (snapBackTimer) {
      clearTimeout(snapBackTimer);
      snapBackTimer = null;
    }
  }
  
  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initWorkflowCards);
  } else {
    initWorkflowCards();
  }
  
  // Re-initialize when HTMX swaps content
  if (typeof htmx !== 'undefined') {
    document.body.addEventListener('htmx:afterSwap', function(event) {
      // Only re-init if workflows were updated
      if (event.detail.target.id === 'workflows-pane') {
        // Small delay to ensure DOM is ready
        setTimeout(initWorkflowCards, 100);
      }
    });
  }
  
  // Cleanup on page unload
  window.addEventListener('beforeunload', cleanup);
  
  // Expose for debugging (development only)
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    window.WorkflowCards = {
      openCard,
      closeCard,
      getCurrentCard: () => currentSwipedCard
    };
  }
})();
