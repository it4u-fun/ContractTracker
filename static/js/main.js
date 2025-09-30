/**
 * Contract Tracker - Main JavaScript
 */

// Global configuration
const CONFIG = {
    API_BASE_URL: '/api',
    DATE_FORMAT: 'YYYY-MM-DD',
    CURRENCY_SYMBOL: '£'
};

// Utility functions
const Utils = {
    /**
     * Format a number as currency
     */
    formatCurrency: function(amount) {
        return new Intl.NumberFormat('en-GB', {
            style: 'currency',
            currency: 'GBP'
        }).format(amount);
    },

    /**
     * Format a date string
     */
    formatDate: function(dateString, format = 'DD MMM YYYY') {
        const date = new Date(dateString);
        const options = {
            day: '2-digit',
            month: 'short',
            year: 'numeric'
        };
        return date.toLocaleDateString('en-GB', options);
    },

    /**
     * Calculate days between two dates
     */
    daysBetween: function(startDate, endDate) {
        const start = new Date(startDate);
        const end = new Date(endDate);
        const diffTime = Math.abs(end - start);
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
    },

    /**
     * Make API request with error handling
     */
    apiRequest: async function(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    },

    /**
     * Show loading state
     */
    showLoading: function(element) {
        if (element) {
            element.innerHTML = `
                <div class="text-center py-4">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-3 text-muted">Loading...</p>
                </div>
            `;
        }
    },

    /**
     * Hide loading state
     */
    hideLoading: function(element) {
        if (element) {
            element.innerHTML = '';
        }
    },

    /**
     * Debounce function calls
     */
    debounce: function(func, wait) {
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
    ,
    /**
     * Safely decode HTML entities to plain text (no HTML injection)
     */
    decodeHtmlEntities: function(value) {
        if (value == null) return '';
        const textarea = document.createElement('textarea');
        textarea.innerHTML = String(value);
        return textarea.value;
    }
};

// Global event handlers
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Global error handler
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    if (window.showFlashMessage) {
        showFlashMessage('An unexpected error occurred. Please try again.', 'danger');
    }
});

// Global unhandled promise rejection handler
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    if (window.showFlashMessage) {
        showFlashMessage('An error occurred while processing your request.', 'danger');
    }
});

// Export utilities for use in other scripts
window.Utils = Utils;
window.CONFIG = CONFIG;
