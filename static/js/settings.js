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


// Initialize form when page loads
document.addEventListener('DOMContentLoaded', function() {
    new SettingsForm();
});
