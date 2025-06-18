/*
 * Simple pagination JavaScript for e-reader compatibility
 * No modern JS features - compatible with basic browsers
 */

// Simple pagination state
var currentPage = 1;
var itemsPerPage = 12; // Default items per page
var totalItems = 0;
var totalPages = 1;
var allItems = [];

// Initialize pagination when page loads
function initPagination() {
    // Disable pagination on series and authors pages - complex layouts cause issues
    if (window.location.pathname.includes('/series') || window.location.pathname.includes('/authors')) {
        return; // No pagination for series or authors pages
    } else {
        // For other pages, use individual items
        var itemSelectors = [
            '.author-button',    // Authors page
            '.book-item:not(.empty)' // Books pages
        ];
        
        var items = [];
        for (var i = 0; i < itemSelectors.length; i++) {
            var found = document.querySelectorAll(itemSelectors[i]);
            if (found.length > 0) {
                items = Array.prototype.slice.call(found);
                break;
            }
        }
        allItems = items;
    }
    
    totalItems = allItems.length;
    totalPages = Math.ceil(totalItems / itemsPerPage);
    
    // Only show pagination if we have enough items
    if (totalItems <= itemsPerPage) {
        return; // Don't show pagination for short lists
    }
    
    createPaginationControls();
    showPage(1);
}

// Create pagination control elements
function createPaginationControls() {
    var body = document.body;
    
    // Create pagination container
    var controls = document.createElement('div');
    controls.className = 'pagination-controls';
    controls.innerHTML = 
        '<div class="pagination-arrow" id="page-up" onclick="previousPage()">↑</div>' +
        '<div class="pagination-arrow" id="page-down" onclick="nextPage()">↓</div>';
    
    // Create page indicator
    var indicator = document.createElement('div');
    indicator.className = 'page-indicator';
    indicator.id = 'page-indicator';
    
    body.appendChild(controls);
    body.appendChild(indicator);
    
    updateControls();
}

// Show specific page
function showPage(pageNum) {
    if (pageNum < 1 || pageNum > totalPages) return;
    
    currentPage = pageNum;
    
    // Hide all items
    for (var i = 0; i < allItems.length; i++) {
        allItems[i].style.display = 'none';
    }
    
    // Show items for current page
    var start = (currentPage - 1) * itemsPerPage;
    var end = Math.min(start + itemsPerPage, totalItems);
    
    for (var i = start; i < end; i++) {
        allItems[i].style.display = '';
    }
    
    updateControls();
    
    // Smooth scroll to top
    window.scrollTo(0, 0);
}

// Go to previous page
function previousPage() {
    if (currentPage > 1) {
        showPage(currentPage - 1);
    }
}

// Go to next page  
function nextPage() {
    if (currentPage < totalPages) {
        showPage(currentPage + 1);
    }
}

// Update control states and indicator
function updateControls() {
    var upButton = document.getElementById('page-up');
    var downButton = document.getElementById('page-down');
    var indicator = document.getElementById('page-indicator');
    
    if (!upButton || !downButton || !indicator) return;
    
    // Update button states
    if (currentPage <= 1) {
        upButton.className = 'pagination-arrow disabled';
    } else {
        upButton.className = 'pagination-arrow';
    }
    
    if (currentPage >= totalPages) {
        downButton.className = 'pagination-arrow disabled';
    } else {
        downButton.className = 'pagination-arrow';
    }
    
    // Update page indicator
    indicator.textContent = currentPage + ' / ' + totalPages;
    indicator.style.display = 'block';
}

// Initialize when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPagination);
} else {
    initPagination();
}