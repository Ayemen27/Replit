/**
 * Workflow Cards Controller - Swipe Actions
 * ============================================================================
 * Features:
 * - Touch swipe gestures on mobile
 * - Reveal action buttons on swipe left
 * - Auto-close on click outside
 * - RTL support
 * ============================================================================
 */

(function() {
  'use strict';
  
  // Configuration
  const SWIPE_THRESHOLD = 50; // Minimum distance to trigger swipe
  const SWIPE_VELOCITY = 0.3; // Minimum velocity
  
  // State
  let activeCard = null;
  let touchStartX = 0;
  let touchStartY = 0;
  let touchStartTime = 0;
  let isDragging = false;
  
  // Get all workflow cards
  const cards = document.querySelectorAll('.workflow-card');
  
  // -------------------------------------------------------------------------
  // Touch Event Handlers
  // -------------------------------------------------------------------------
  
  function handleTouchStart(e) {
    const card = e.currentTarget;
    const touch = e.touches[0];
    
    touchStartX = touch.clientX;
    touchStartY = touch.clientY;
    touchStartTime = Date.now();
    isDragging = false;
    
    // Close other open cards
    if (activeCard && activeCard !== card) {
      closeCard(activeCard);
    }
  }
  
  function handleTouchMove(e) {
    if (!touchStartX) return;
    
    const touch = e.touches[0];
    const deltaX = touch.clientX - touchStartX;
    const deltaY = touch.clientY - touchStartY;
    
    // Determine if horizontal swipe (not vertical scroll)
    if (!isDragging && Math.abs(deltaX) > Math.abs(deltaY)) {
      isDragging = true;
    }
    
    if (isDragging) {
      // Prevent vertical scroll when swiping horizontally
      e.preventDefault();
      
      const card = e.currentTarget;
      const swipeable = card.querySelector('.workflow-card__swipeable');
      
      // Only allow swipe left (reveal actions on right)
      // For RTL: swipe right
      const isRTL = document.dir === 'rtl';
      const maxSwipe = isRTL ? 80 : -80;
      
      if ((isRTL && deltaX > 0 && deltaX <= 80) || 
          (!isRTL && deltaX < 0 && deltaX >= -80)) {
        swipeable.style.transform = `translateX(${deltaX}px)`;
        swipeable.style.transition = 'none';
      }
    }
  }
  
  function handleTouchEnd(e) {
    if (!isDragging) {
      touchStartX = 0;
      touchStartY = 0;
      return;
    }
    
    const touch = e.changedTouches[0];
    const deltaX = touch.clientX - touchStartX;
    const deltaTime = Date.now() - touchStartTime;
    const velocity = Math.abs(deltaX) / deltaTime;
    
    const card = e.currentTarget;
    const swipeable = card.querySelector('.workflow-card__swipeable');
    const isRTL = document.dir === 'rtl';
    
    // Reset transition
    swipeable.style.transition = '';
    
    // Determine if swipe is complete
    const shouldOpen = isRTL 
      ? (deltaX > SWIPE_THRESHOLD || velocity > SWIPE_VELOCITY)
      : (deltaX < -SWIPE_THRESHOLD || velocity > SWIPE_VELOCITY);
    
    if (shouldOpen) {
      openCard(card);
    } else {
      closeCard(card);
    }
    
    // Reset state
    touchStartX = 0;
    touchStartY = 0;
    isDragging = false;
  }
  
  // -------------------------------------------------------------------------
  // Card State Management
  // -------------------------------------------------------------------------
  
  function openCard(card) {
    card.classList.add('is-swiped');
    card.setAttribute('aria-expanded', 'true');
    activeCard = card;
    
    // Reset transform
    const swipeable = card.querySelector('.workflow-card__swipeable');
    swipeable.style.transform = '';
  }
  
  function closeCard(card) {
    card.classList.remove('is-swiped');
    card.setAttribute('aria-expanded', 'false');
    
    if (activeCard === card) {
      activeCard = null;
    }
    
    // Reset transform
    const swipeable = card.querySelector('.workflow-card__swipeable');
    swipeable.style.transform = '';
  }
  
  function closeAllCards() {
    cards.forEach(card => {
      if (card.classList.contains('is-swiped')) {
        closeCard(card);
      }
    });
  }
  
  // -------------------------------------------------------------------------
  // Event Listeners
  // -------------------------------------------------------------------------
  
  // Attach touch events to each card
  cards.forEach(card => {
    // Only on touch devices
    if ('ontouchstart' in window) {
      card.addEventListener('touchstart', handleTouchStart, { passive: false });
      card.addEventListener('touchmove', handleTouchMove, { passive: false });
      card.addEventListener('touchend', handleTouchEnd, { passive: true });
    }
  });
  
  // Close cards when clicking outside
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.workflow-card') && activeCard) {
      closeAllCards();
    }
  });
  
  // Close cards on scroll
  let scrollTimeout;
  window.addEventListener('scroll', () => {
    clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(() => {
      if (activeCard) {
        closeAllCards();
      }
    }, 100);
  }, { passive: true });
  
  // -------------------------------------------------------------------------
  // Accessibility
  // -------------------------------------------------------------------------
  
  // Keyboard support for action buttons
  document.querySelectorAll('.action-btn').forEach(btn => {
    btn.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        const card = e.target.closest('.workflow-card');
        if (card) {
          closeCard(card);
        }
      }
    });
  });
  
  // -------------------------------------------------------------------------
  // Initialize
  // -------------------------------------------------------------------------
  
  console.log(`✓ Workflow cards initialized: ${cards.length} cards`);
  
  // Expose close function globally (for manual triggers)
  window.WorkflowCards = {
    closeAll: closeAllCards
  };
  
})();
