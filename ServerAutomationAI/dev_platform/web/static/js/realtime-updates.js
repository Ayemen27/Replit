/**
 * Real-time Updates Manager
 * إدارة التحديثات الفورية
 * 
 * Handles HTMX polling status, connection monitoring, and update notifications
 */

(function() {
  'use strict';
  
  let isOnline = true;
  let lastUpdateTime = Date.now();
  let connectionCheckInterval;
  
  function init() {
    setupConnectionMonitor();
    setupHTMXEventListeners();
    createConnectionIndicator();
  }
  
  function setupConnectionMonitor() {
    // Check connection every 30 seconds
    connectionCheckInterval = setInterval(checkConnection, 30000);
    
    // Listen to online/offline events
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
  }
  
  function checkConnection() {
    const now = Date.now();
    const timeSinceLastUpdate = now - lastUpdateTime;
    
    // If no update in 60 seconds, show warning
    if (timeSinceLastUpdate > 60000 && isOnline) {
      showConnectionWarning();
    }
  }
  
  function handleOnline() {
    isOnline = true;
    updateConnectionStatus('online');
    
    // Trigger manual refresh of all HTMX elements
    document.querySelectorAll('[hx-get]').forEach(el => {
      htmx.trigger(el, 'load');
    });
  }
  
  function handleOffline() {
    isOnline = false;
    updateConnectionStatus('offline');
  }
  
  function setupHTMXEventListeners() {
    // Before request
    document.body.addEventListener('htmx:beforeRequest', function(evt) {
      const target = evt.detail.target;
      if (target) {
        target.classList.add('htmx-loading');
      }
    });
    
    // After successful request
    document.body.addEventListener('htmx:afterSwap', function(evt) {
      const target = evt.detail.target;
      if (target) {
        target.classList.remove('htmx-loading');
        target.classList.add('htmx-updated');
        setTimeout(() => target.classList.remove('htmx-updated'), 1000);
      }
      
      lastUpdateTime = Date.now();
      updateConnectionStatus('online');
    });
    
    // On error
    document.body.addEventListener('htmx:responseError', function(evt) {
      console.error('HTMX Error:', evt.detail);
      updateConnectionStatus('error');
      
      // Retry after 5 seconds
      const target = evt.detail.target;
      if (target && target.hasAttribute('hx-get')) {
        setTimeout(() => htmx.trigger(target, 'load'), 5000);
      }
    });
    
    // On timeout
    document.body.addEventListener('htmx:timeout', function(evt) {
      console.warn('HTMX Timeout:', evt.detail);
      updateConnectionStatus('warning');
    });
  }
  
  function createConnectionIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'connection-indicator';
    indicator.className = 'connection-indicator';
    indicator.innerHTML = `
      <div class="connection-dot"></div>
      <span class="connection-text">متصل</span>
    `;
    indicator.setAttribute('role', 'status');
    indicator.setAttribute('aria-live', 'polite');
    
    document.body.appendChild(indicator);
  }
  
  function updateConnectionStatus(status) {
    const indicator = document.getElementById('connection-indicator');
    if (!indicator) return;
    
    const dot = indicator.querySelector('.connection-dot');
    const text = indicator.querySelector('.connection-text');
    
    // Remove all status classes
    indicator.className = 'connection-indicator';
    
    switch(status) {
      case 'online':
        indicator.classList.add('status-online');
        text.textContent = 'متصل';
        indicator.setAttribute('aria-label', 'متصل بالخادم');
        break;
      case 'offline':
        indicator.classList.add('status-offline');
        text.textContent = 'غير متصل';
        indicator.setAttribute('aria-label', 'غير متصل بالخادم');
        showToast('تم قطع الاتصال بالخادم', 'error');
        break;
      case 'error':
        indicator.classList.add('status-error');
        text.textContent = 'خطأ';
        indicator.setAttribute('aria-label', 'خطأ في الاتصال');
        break;
      case 'warning':
        indicator.classList.add('status-warning');
        text.textContent = 'بطيء';
        indicator.setAttribute('aria-label', 'الاتصال بطيء');
        break;
    }
  }
  
  function showConnectionWarning() {
    const indicator = document.getElementById('connection-indicator');
    if (indicator) {
      updateConnectionStatus('warning');
      setTimeout(() => {
        if (isOnline) updateConnectionStatus('online');
      }, 5000);
    }
  }
  
  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
  
  // Cleanup on page unload
  window.addEventListener('beforeunload', function() {
    clearInterval(connectionCheckInterval);
  });
  
})();
