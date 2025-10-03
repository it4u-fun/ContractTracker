/**
 * Custom Holidays JavaScript
 */

class CustomHolidaysManager {
    constructor() {
        this.currentHolidayId = null;
        this.init();
    }

    async init() {
        await this.loadCustomHolidays();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Modal event listeners
        const modal = document.getElementById('addHolidayModal');
        if (modal) {
            modal.addEventListener('hidden.bs.modal', () => {
                this.clearForm();
            });
        }
    }

    async loadCustomHolidays() {
        try {
            // Hide loading state and show content
            this.hideLoadingState();
            
            const data = await Utils.apiRequest('/api/custom-holidays');
            
            if (data.success) {
                this.displayHolidays(data.holidays);
            } else {
                throw new Error(data.error || 'Failed to load custom holidays');
            }
        } catch (error) {
            console.error('Error loading custom holidays:', error);
            showFlashMessage('Failed to load custom holidays', 'danger');
            this.showEmptyState();
        }
    }

    displayHolidays(holidays) {
        const container = document.getElementById('customHolidaysList');
        const emptyState = document.getElementById('empty-state');
        
        if (!container) return;

        if (holidays.length === 0) {
            this.showEmptyState();
            return;
        }

        // Hide empty state
        if (emptyState) {
            emptyState.style.display = 'none';
        }

        const table = `
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Type</th>
                        <th>Start Date</th>
                        <th>End Date</th>
                        <th>Description</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${holidays.map(holiday => `
                        <tr>
                            <td><strong>${Utils.escapeHtml(holiday.name)}</strong></td>
                            <td>
                                <span class="badge ${this.getHolidayTypeBadgeClass(holiday.holiday_type)}">
                                    ${this.getHolidayTypeLabel(holiday.holiday_type)}
                                </span>
                            </td>
                            <td>${holiday.start_date}</td>
                            <td>${holiday.end_date}</td>
                            <td>${holiday.description ? Utils.escapeHtml(holiday.description) : '-'}</td>
                            <td>
                                <button class="btn btn-sm btn-outline-primary me-1" onclick="customHolidaysManager.editHoliday('${holiday.holiday_id}')">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger" onclick="customHolidaysManager.deleteHoliday('${holiday.holiday_id}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        container.innerHTML = table;
    }

    getHolidayTypeBadgeClass(type) {
        const classes = {
            'bank_holiday': 'bg-warning text-dark',
            'office_closure': 'bg-danger',
            'personal_holiday': 'bg-info'
        };
        return classes[type] || 'bg-secondary';
    }

    getHolidayTypeLabel(type) {
        const labels = {
            'bank_holiday': 'Bank Holiday',
            'office_closure': 'Office Closure',
            'personal_holiday': 'Personal Holiday'
        };
        return labels[type] || type;
    }

    async saveCustomHoliday() {
        try {
            const form = document.getElementById('holidayForm');
            const formData = new FormData(form);
            
            const holidayData = {
                name: formData.get('name'),
                description: formData.get('description') || null,
                start_date: formData.get('start_date'),
                end_date: formData.get('end_date'),
                holiday_type: formData.get('holiday_type')
            };

            // Validate required fields
            if (!holidayData.name || !holidayData.start_date || !holidayData.end_date) {
                showFlashMessage('Please fill in all required fields', 'warning');
                return;
            }

            // Validate dates
            if (new Date(holidayData.start_date) > new Date(holidayData.end_date)) {
                showFlashMessage('End date must be after start date', 'warning');
                return;
            }

            let response;
            if (this.currentHolidayId) {
                // Update existing holiday
                response = await Utils.apiRequest(`/api/custom-holidays/${this.currentHolidayId}`, {
                    method: 'PUT',
                    body: JSON.stringify(holidayData)
                });
            } else {
                // Add new holiday
                response = await Utils.apiRequest('/api/custom-holidays', {
                    method: 'POST',
                    body: JSON.stringify(holidayData)
                });
            }

            if (response.success) {
                showFlashMessage(response.message, 'success');
                await this.loadCustomHolidays();
                this.closeModal();
            } else {
                throw new Error(response.error || 'Failed to save holiday');
            }

        } catch (error) {
            console.error('Error saving custom holiday:', error);
            showFlashMessage(error.message || 'Failed to save holiday', 'danger');
        }
    }

    async editHoliday(holidayId) {
        try {
            const data = await Utils.apiRequest('/api/custom-holidays');
            
            if (data.success) {
                const holiday = data.holidays.find(h => h.holiday_id === holidayId);
                if (holiday) {
                    this.currentHolidayId = holidayId;
                    this.populateForm(holiday);
                    this.showModal('Edit Custom Holiday');
                } else {
                    throw new Error('Holiday not found');
                }
            } else {
                throw new Error(data.error || 'Failed to load holiday data');
            }
        } catch (error) {
            console.error('Error loading holiday for edit:', error);
            showFlashMessage('Failed to load holiday data', 'danger');
        }
    }

    async deleteHoliday(holidayId) {
        if (!confirm('Are you sure you want to delete this holiday? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await Utils.apiRequest(`/api/custom-holidays/${holidayId}`, {
                method: 'DELETE'
            });

            if (response.success) {
                showFlashMessage(response.message, 'success');
                await this.loadCustomHolidays();
            } else {
                throw new Error(response.error || 'Failed to delete holiday');
            }

        } catch (error) {
            console.error('Error deleting holiday:', error);
            showFlashMessage(error.message || 'Failed to delete holiday', 'danger');
        }
    }

    populateForm(holiday) {
        document.getElementById('holidayId').value = holiday.holiday_id || '';
        document.getElementById('holidayName').value = holiday.name || '';
        document.getElementById('holidayDescription').value = holiday.description || '';
        document.getElementById('holidayStartDate').value = holiday.start_date || '';
        document.getElementById('holidayEndDate').value = holiday.end_date || '';
        document.getElementById('holidayType').value = holiday.holiday_type || 'bank_holiday';
    }

    clearForm() {
        this.currentHolidayId = null;
        document.getElementById('holidayId').value = '';
        document.getElementById('holidayName').value = '';
        document.getElementById('holidayDescription').value = '';
        document.getElementById('holidayStartDate').value = '';
        document.getElementById('holidayEndDate').value = '';
        document.getElementById('holidayType').value = 'bank_holiday';
    }

    showModal(title) {
        document.getElementById('addHolidayModalLabel').textContent = title;
        const modal = new bootstrap.Modal(document.getElementById('addHolidayModal'));
        modal.show();
    }

    closeModal() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('addHolidayModal'));
        if (modal) {
            modal.hide();
        }
    }

    hideLoadingState() {
        const loadingState = document.getElementById('loading-state');
        if (loadingState) {
            loadingState.style.display = 'none';
        }
    }

    showEmptyState() {
        const emptyState = document.getElementById('empty-state');
        const container = document.getElementById('customHolidaysList');
        
        if (emptyState) {
            emptyState.style.display = 'block';
        }
        if (container) {
            container.innerHTML = '';
        }
    }
}

// Global functions for HTML onclick handlers
let customHolidaysManager;

async function loadCustomHolidays() {
    if (customHolidaysManager) {
        await customHolidaysManager.loadCustomHolidays();
    }
}

async function saveCustomHoliday() {
    if (customHolidaysManager) {
        await customHolidaysManager.saveCustomHoliday();
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    customHolidaysManager = new CustomHolidaysManager();
});
