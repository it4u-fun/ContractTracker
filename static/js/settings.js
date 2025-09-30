/**
 * Settings JavaScript
 */

class SettingsForm {
    constructor() {
        this.form = document.getElementById('settings-form');
        this.init();
    }

    async init() {
        if (this.form) {
            await this.loadSettings();
            this.setupEventListeners();
        }
    }

    async loadSettings() {
        try {
            const data = await Utils.apiRequest('/api/dashboard/settings');
            
            if (data.success) {
                this.populateForm(data.settings);
            } else {
                throw new Error(data.error || 'Failed to load settings');
            }
        } catch (error) {
            console.error('Error loading settings:', error);
            showFlashMessage('Failed to load settings', 'danger');
        }
    }

    populateForm(settings) {
        // Financial settings
        document.getElementById('financial_year_start').value = settings.financial_year_start || '15-Jul';
        document.getElementById('vat_rate').value = settings.vat_rate || 20;
        document.getElementById('daily_rate').value = settings.daily_rate || 575;

        // Holiday settings
        document.getElementById('max_holiday_weeks').value = settings.max_holiday_weeks || 2;
        document.getElementById('holiday_gap_weeks').value = settings.holiday_gap_weeks || 1;

        // Calendar settings
        document.getElementById('week_starts_monday').checked = settings.week_starts_monday !== false;
        document.getElementById('show_weekends').checked = settings.show_weekends !== false;

        // Data sources
        const enabledSources = settings.enabled_data_sources || {};
        document.getElementById('uk_bank_holidays').checked = enabledSources.uk_bank_holidays !== false;
        document.getElementById('praewood_school').checked = enabledSources.praewood_school !== false;
        document.getElementById('custom_holidays').checked = enabledSources.custom_holidays !== false;
    }

    setupEventListeners() {
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
    }

    async handleSubmit(event) {
        event.preventDefault();
        
        const submitButton = event.target.querySelector('button[type="submit"]');
        const originalText = submitButton.innerHTML;
        
        try {
            // Disable form and show loading
            this.setFormLoading(true, submitButton);
            
            const formData = this.getFormData();
            
            // Submit to API
            const response = await Utils.apiRequest('/api/dashboard/settings', {
                method: 'PUT',
                body: JSON.stringify(formData)
            });
            
            if (response.success) {
                showFlashMessage('Settings saved successfully!', 'success');
            } else {
                throw new Error(response.error || 'Failed to save settings');
            }
            
        } catch (error) {
            console.error('Error saving settings:', error);
            showFlashMessage(error.message || 'Failed to save settings', 'danger');
        } finally {
            this.setFormLoading(false, submitButton, originalText);
        }
    }

    getFormData() {
        const enabledSources = {};
        
        // Get data source checkboxes
        const ukBankHolidays = document.getElementById('uk_bank_holidays');
        const praewoodSchool = document.getElementById('praewood_school');
        const customHolidays = document.getElementById('custom_holidays');
        
        if (ukBankHolidays) enabledSources.uk_bank_holidays = ukBankHolidays.checked;
        if (praewoodSchool) enabledSources.praewood_school = praewoodSchool.checked;
        if (customHolidays) enabledSources.custom_holidays = customHolidays.checked;

        return {
            financial_year_start: document.getElementById('financial_year_start')?.value || '15-Jul',
            vat_rate: parseInt(document.getElementById('vat_rate')?.value) || 20,
            daily_rate: parseFloat(document.getElementById('daily_rate')?.value) || 575,
            max_holiday_weeks: parseInt(document.getElementById('max_holiday_weeks')?.value) || 2,
            holiday_gap_weeks: parseInt(document.getElementById('holiday_gap_weeks')?.value) || 1,
            week_starts_monday: document.getElementById('week_starts_monday')?.checked !== false,
            show_weekends: document.getElementById('show_weekends')?.checked !== false,
            enabled_data_sources: enabledSources
        };
    }

    setFormLoading(loading, button, originalText = null) {
        const form = document.getElementById('settings-form');
        const inputs = form.querySelectorAll('input, select, textarea, button');
        
        inputs.forEach(input => {
            input.disabled = loading;
        });
        
        if (button) {
            if (loading) {
                button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';
            } else if (originalText) {
                button.innerHTML = originalText;
            }
        }
    }
}

// Custom Holidays Management
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
            const data = await Utils.apiRequest('/api/custom-holidays');
            
            if (data.success) {
                this.displayHolidays(data.holidays);
            } else {
                throw new Error(data.error || 'Failed to load custom holidays');
            }
        } catch (error) {
            console.error('Error loading custom holidays:', error);
            showFlashMessage('Failed to load custom holidays', 'danger');
        }
    }

    displayHolidays(holidays) {
        const container = document.getElementById('customHolidaysList');
        if (!container) return;

        if (holidays.length === 0) {
            container.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    No custom holidays defined yet. Click "Add Custom Holiday" to create your first holiday period.
                </div>
            `;
            return;
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

// Initialize form when page loads
document.addEventListener('DOMContentLoaded', function() {
    new SettingsForm();
    customHolidaysManager = new CustomHolidaysManager();
});
