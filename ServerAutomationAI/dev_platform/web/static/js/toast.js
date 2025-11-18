/**
 * Toast Notification System
 * نظام الإشعارات
 */

class ToastManager {
  constructor() {
    this.container = this.createContainer();
    this.toasts = new Map();
  }

  createContainer() {
    let container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      container.setAttribute('role', 'region');
      container.setAttribute('aria-label', 'الإشعارات');
      container.setAttribute('aria-live', 'polite');
      document.body.appendChild(container);
    }
    return container;
  }

  show(message, options = {}) {
    const {
      type = 'info',
      title = '',
      duration = 5000,
      icon = this.getDefaultIcon(type)
    } = options;

    const id = Date.now() + Math.random();
    const toast = this.createToast(id, title, message, type, icon);
    
    this.container.appendChild(toast);
    this.toasts.set(id, toast);

    if (duration > 0) {
      setTimeout(() => this.hide(id), duration);
    }

    return id;
  }

  createToast(id, title, message, type, icon) {
    const toast = document.createElement('div');
    toast.className = `toast toast--${type}`;
    toast.setAttribute('role', 'alert');
    toast.dataset.toastId = id;

    toast.innerHTML = `
      <i class="toast__icon bi ${icon}"></i>
      <div class="toast__content">
        ${title ? `<div class="toast__title">${this.escapeHtml(title)}</div>` : ''}
        <div class="toast__message">${this.escapeHtml(message)}</div>
      </div>
      <button class="toast__close" aria-label="إغلاق الإشعار">
        <i class="bi bi-x"></i>
      </button>
    `;

    toast.querySelector('.toast__close').addEventListener('click', () => {
      this.hide(id);
    });

    return toast;
  }

  hide(id) {
    const toast = this.toasts.get(id);
    if (!toast) return;

    toast.classList.add('closing');
    setTimeout(() => {
      toast.remove();
      this.toasts.delete(id);
    }, 300);
  }

  getDefaultIcon(type) {
    const icons = {
      success: 'bi-check-circle-fill',
      error: 'bi-x-circle-fill',
      warning: 'bi-exclamation-triangle-fill',
      info: 'bi-info-circle-fill'
    };
    return icons[type] || icons.info;
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  success(message, options = {}) {
    return this.show(message, { ...options, type: 'success' });
  }

  error(message, options = {}) {
    return this.show(message, { ...options, type: 'error' });
  }

  warning(message, options = {}) {
    return this.show(message, { ...options, type: 'warning' });
  }

  info(message, options = {}) {
    return this.show(message, { ...options, type: 'info' });
  }
}

// Global instance
window.toast = new ToastManager();
