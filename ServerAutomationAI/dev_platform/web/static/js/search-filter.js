/**
 * Search and Filter for Workflows
 * البحث والفلترة لسير العمل
 * 
 * WCAG 2.1 §1.3.1 - Info and Relationships
 * OWASP A03 - Input validation
 * 
 * Version: 1.0.0
 */

(function() {
  'use strict';
  
  let searchInput, statusFilter, typeFilter, sortSelect;
  let allWorkflows = [];
  let currentPage = 1;
  const itemsPerPage = 9; // 3x3 grid
  
  function init() {
    searchInput = document.getElementById('workflow-search');
    statusFilter = document.getElementById('workflow-status-filter');
    typeFilter = document.getElementById('workflow-type-filter');
    sortSelect = document.getElementById('workflow-sort');
    
    if (!searchInput || !statusFilter || !typeFilter || !sortSelect) {
      return; // Elements not on page
    }
    
    // Add event listeners
    searchInput.addEventListener('input', debounce(filterWorkflows, 300));
    statusFilter.addEventListener('change', filterWorkflows);
    typeFilter.addEventListener('change', filterWorkflows);
    sortSelect.addEventListener('change', sortWorkflows);
    
    // Initial load
    updateWorkflowsList();
    
    // Listen for HTMX updates
    document.body.addEventListener('htmx:afterSwap', function(event) {
      if (event.detail.target.id === 'all-workflows') {
        updateWorkflowsList();
        filterWorkflows();
      }
    });
  }
  
  function updateWorkflowsList() {
    const container = document.getElementById('all-workflows');
    if (!container) return;
    
    const cards = container.querySelectorAll('.workflow-card');
    allWorkflows = Array.from(cards).map(card => {
      const timeElement = card.querySelector('.info-item .bi-clock')?.parentElement?.textContent || '';
      return {
        element: card,
        name: card.querySelector('.workflow-card__title')?.textContent.toLowerCase() || '',
        status: card.dataset.status?.toLowerCase() || '',
        type: card.dataset.type?.toLowerCase() || '',
        timestamp: timeElement.trim()
      };
    });
  }
  
  function sortWorkflows() {
    if (!sortSelect) return;
    
    const sortValue = sortSelect.value;
    const container = document.getElementById('all-workflows');
    const grid = container?.querySelector('.workflows-grid');
    
    if (!grid || allWorkflows.length === 0) return;
    
    // Sort array
    const sorted = [...allWorkflows].sort((a, b) => {
      switch(sortValue) {
        case 'newest':
          return b.timestamp.localeCompare(a.timestamp);
        case 'oldest':
          return a.timestamp.localeCompare(b.timestamp);
        case 'name-asc':
          return a.name.localeCompare(b.name, 'ar');
        case 'name-desc':
          return b.name.localeCompare(a.name, 'ar');
        case 'status':
          const statusOrder = { running: 0, pending: 1, completed: 2, failed: 3 };
          return (statusOrder[a.status] || 999) - (statusOrder[b.status] || 999);
        default:
          return 0;
      }
    });
    
    // Re-append elements in sorted order
    sorted.forEach(workflow => {
      grid.appendChild(workflow.element);
    });
    
    // Re-apply filters
    filterWorkflows();
  }
  
  function filterWorkflows() {
    const searchTerm = searchInput.value.toLowerCase().trim();
    const statusValue = statusFilter.value.toLowerCase();
    const typeValue = typeFilter.value.toLowerCase();
    
    // Sanitize inputs (OWASP A03)
    const sanitizedSearch = sanitizeInput(searchTerm);
    
    let visibleCount = 0;
    
    allWorkflows.forEach(workflow => {
      let visible = true;
      
      // Search filter
      if (sanitizedSearch && !workflow.name.includes(sanitizedSearch)) {
        visible = false;
      }
      
      // Status filter
      if (statusValue && workflow.status !== statusValue) {
        visible = false;
      }
      
      // Type filter
      if (typeValue && workflow.type !== typeValue) {
        visible = false;
      }
      
      // Apply visibility
      if (visible) {
        workflow.element.style.display = '';
        visibleCount++;
      } else {
        workflow.element.style.display = 'none';
      }
    });
    
    // Show "no results" message if needed
    showNoResultsMessage(visibleCount === 0);
    
    // Apply pagination
    paginateWorkflows();
    
    // Announce to screen readers (WCAG)
    announceResults(visibleCount);
  }
  
  function paginateWorkflows() {
    const visibleWorkflows = allWorkflows.filter(w => w.element.style.display !== 'none');
    const totalPages = Math.ceil(visibleWorkflows.length / itemsPerPage);
    
    // Adjust current page if needed
    if (currentPage > totalPages) {
      currentPage = Math.max(1, totalPages);
    }
    
    // Show/hide based on page
    const start = (currentPage - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    
    visibleWorkflows.forEach((workflow, index) => {
      if (index >= start && index < end) {
        workflow.element.classList.remove('pagination-hidden');
      } else {
        workflow.element.classList.add('pagination-hidden');
      }
    });
    
    // Update pagination controls
    updatePaginationControls(totalPages, visibleWorkflows.length);
  }
  
  function updatePaginationControls(totalPages, totalItems) {
    let paginationContainer = document.getElementById('workflow-pagination');
    
    if (!paginationContainer) {
      const container = document.getElementById('all-workflows');
      if (!container) return;
      
      paginationContainer = document.createElement('div');
      paginationContainer.id = 'workflow-pagination';
      paginationContainer.className = 'pagination-controls mt-4';
      container.parentElement.appendChild(paginationContainer);
    }
    
    if (totalPages <= 1) {
      paginationContainer.innerHTML = '';
      return;
    }
    
    const start = (currentPage - 1) * itemsPerPage + 1;
    const end = Math.min(currentPage * itemsPerPage, totalItems);
    
    paginationContainer.innerHTML = `
      <div class="d-flex justify-content-between align-items-center">
        <div class="pagination-info text-muted">
          عرض ${start}-${end} من ${totalItems}
        </div>
        <nav aria-label="Workflow pagination">
          <ul class="pagination mb-0">
            <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
              <button class="page-link" onclick="window.changePage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>السابق</button>
            </li>
            ${generatePageNumbers(totalPages)}
            <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
              <button class="page-link" onclick="window.changePage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>التالي</button>
            </li>
          </ul>
        </nav>
      </div>
    `;
  }
  
  function generatePageNumbers(totalPages) {
    let pages = '';
    const maxVisible = 5;
    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, startPage + maxVisible - 1);
    
    if (endPage - startPage < maxVisible - 1) {
      startPage = Math.max(1, endPage - maxVisible + 1);
    }
    
    for (let i = startPage; i <= endPage; i++) {
      pages += `
        <li class="page-item ${i === currentPage ? 'active' : ''}">
          <button class="page-link" onclick="window.changePage(${i})">${i}</button>
        </li>
      `;
    }
    return pages;
  }
  
  window.changePage = function(page) {
    currentPage = page;
    paginateWorkflows();
    
    // Scroll to top of workflows
    document.getElementById('all-workflows')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };
  
  function sanitizeInput(input) {
    // Remove potentially dangerous characters
    return input.replace(/[<>\"\'&]/g, '');
  }
  
  function showNoResultsMessage(show) {
    const container = document.getElementById('all-workflows');
    if (!container) return;
    
    let message = container.querySelector('.no-results-message');
    
    if (show) {
      if (!message) {
        message = document.createElement('div');
        message.className = 'no-results-message text-center text-muted p-4';
        message.innerHTML = '<i class="bi bi-search"></i><p class="mt-2">لا توجد نتائج مطابقة</p>';
        container.appendChild(message);
      }
    } else {
      if (message) {
        message.remove();
      }
    }
  }
  
  function announceResults(count) {
    const announcement = count === 0 
      ? 'لا توجد نتائج' 
      : `تم العثور على ${count} من سير العمل`;
    
    // Create or update ARIA live region
    let liveRegion = document.getElementById('workflow-search-status');
    if (!liveRegion) {
      liveRegion = document.createElement('div');
      liveRegion.id = 'workflow-search-status';
      liveRegion.className = 'visually-hidden';
      liveRegion.setAttribute('role', 'status');
      liveRegion.setAttribute('aria-live', 'polite');
      liveRegion.setAttribute('aria-atomic', 'true');
      document.body.appendChild(liveRegion);
    }
    
    liveRegion.textContent = announcement;
  }
  
  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
  
  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
  
  // Expose for testing
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { sanitizeInput, filterWorkflows };
  }
})();
