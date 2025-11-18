/**
 * Error Handler
 * معالج الأخطاء
 * 
 * Provides consistent error handling and user-friendly error messages
 */

(function() {
  'use strict';
  
  const ERROR_MESSAGES = {
    'network': 'فشل الاتصال بالخادم. يرجى التحقق من اتصالك بالإنترنت.',
    'timeout': 'انتهت مهلة الطلب. يرجى المحاولة مرة أخرى.',
    'unauthorized': 'انتهت جلستك. يرجى تسجيل الدخول مرة أخرى.',
    'forbidden': 'ليس لديك صلاحية للوصول إلى هذا المورد.',
    'not_found': 'المورد المطلوب غير موجود.',
    'server_error': 'حدث خطأ في الخادم. يرجى المحاولة لاحقاً.',
    'validation': 'البيانات المدخلة غير صحيحة. يرجى مراجعتها.',
    'unknown': 'حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى.'
  };
  
  function init() {
    setupGlobalErrorHandlers();
    setupHTMXErrorHandlers();
  }
  
  function setupGlobalErrorHandlers() {
    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', function(event) {
      console.error('Unhandled promise rejection:', event.reason);
      showError('unknown', event.reason);
    });
    
    // Handle global errors
    window.addEventListener('error', function(event) {
      console.error('Global error:', event.error);
      // Don't show toast for script loading errors
      if (!event.filename) return;
    });
  }
  
  function setupHTMXErrorHandlers() {
    // Handle HTMX errors
    document.body.addEventListener('htmx:responseError', function(evt) {
      const xhr = evt.detail.xhr;
      const statusCode = xhr.status;
      
      handleHTTPError(statusCode, xhr.responseText, evt.detail.target);
    });
    
    // Handle HTMX send errors
    document.body.addEventListener('htmx:sendError', function(evt) {
      showError('network');
      showErrorState(evt.detail.target);
    });
    
    // Handle HTMX timeouts
    document.body.addEventListener('htmx:timeout', function(evt) {
      showError('timeout');
      showErrorState(evt.detail.target);
    });
  }
  
  function handleHTTPError(statusCode, responseText, target) {
    let errorType = 'unknown';
    
    switch(statusCode) {
      case 0:
        errorType = 'network';
        break;
      case 401:
        errorType = 'unauthorized';
        handleUnauthorized();
        return;
      case 403:
        errorType = 'forbidden';
        break;
      case 404:
        errorType = 'not_found';
        break;
      case 422:
        errorType = 'validation';
        break;
      case 500:
      case 502:
      case 503:
        errorType = 'server_error';
        break;
    }
    
    showError(errorType, responseText);
    showErrorState(target);
  }
  
  function handleUnauthorized() {
    // Redirect to login after showing message
    showError('unauthorized');
    setTimeout(() => {
      window.location.href = '/';
    }, 2000);
  }
  
  function showError(type, details) {
    const message = ERROR_MESSAGES[type] || ERROR_MESSAGES.unknown;
    
    if (typeof showToast === 'function') {
      showToast(message, 'error');
    } else {
      console.error(message, details);
    }
  }
  
  function showErrorState(element) {
    if (!element) return;
    
    // Add error class
    element.classList.add('error-state');
    
    // Create error message if container
    if (element.classList.contains('card-body') || element.id.includes('container')) {
      const errorHTML = `
        <div class="error-placeholder" role="alert">
          <div class="error-icon">
            <i class="bi bi-exclamation-triangle-fill"></i>
          </div>
          <h5 class="error-title">حدث خطأ</h5>
          <p class="error-message">تعذر تحميل البيانات. يرجى المحاولة مرة أخرى.</p>
          <button class="btn btn-primary btn-sm" onclick="location.reload()">
            <i class="bi bi-arrow-clockwise"></i> إعادة المحاولة
          </button>
        </div>
      `;
      element.innerHTML = errorHTML;
    }
    
    // Remove error state after 5 seconds
    setTimeout(() => {
      element.classList.remove('error-state');
    }, 5000);
  }
  
  // Public API
  window.ErrorHandler = {
    show: showError,
    showState: showErrorState,
    handleHTTP: handleHTTPError
  };
  
  // Initialize
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
  
})();
