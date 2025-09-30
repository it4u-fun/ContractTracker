/**
 * New Contract Form JavaScript
 */

class NewContractForm {
    constructor() {
        this.form = document.getElementById('new-contract-form');
        this.init();
    }

    init() {
        if (this.form) {
            this.setupEventListeners();
            this.updatePreview();
        }
    }

    setupEventListeners() {
        // Form submission
        this.form.addEventListener('submit', this.handleSubmit.bind(this));

        // Real-time preview updates
        const previewFields = ['staff_name', 'client_company', 'contract_name', 'start_date', 'end_date', 'total_days', 'daily_rate'];
        previewFields.forEach(fieldName => {
            const field = document.getElementById(fieldName);
            if (field) {
                field.addEventListener('input', Utils.debounce(this.updatePreview.bind(this), 300));
            }
        });

        // Date validation
        const startDateField = document.getElementById('start_date');
        const endDateField = document.getElementById('end_date');
        
        if (startDateField && endDateField) {
            startDateField.addEventListener('change', () => this.validateDates());
            endDateField.addEventListener('change', () => this.validateDates());
        }
    }

    updatePreview() {
        const formData = this.getFormData();
        
        if (formData.staff_name && formData.client_company && formData.contract_name) {
            const contractKey = `${formData.staff_name}_${formData.client_company}_${formData.contract_name}`;
            document.getElementById('preview-key').textContent = contractKey;
        } else {
            document.getElementById('preview-key').textContent = '-';
        }

        if (formData.total_days && formData.daily_rate) {
            const totalValue = formData.total_days * formData.daily_rate;
            document.getElementById('preview-total').textContent = totalValue.toLocaleString();
        } else {
            document.getElementById('preview-total').textContent = '0';
        }

        if (formData.start_date && formData.end_date) {
            const duration = Utils.daysBetween(formData.start_date, formData.end_date);
            document.getElementById('preview-duration').textContent = duration;
        } else {
            document.getElementById('preview-duration').textContent = '0';
        }

        if (formData.daily_rate) {
            document.getElementById('preview-rate').textContent = formData.daily_rate;
        } else {
            document.getElementById('preview-rate').textContent = '0';
        }
    }

    getFormData() {
        return {
            staff_name: this.sanitizeInput(document.getElementById('staff_name')?.value || ''),
            client_company: this.sanitizeInput(document.getElementById('client_company')?.value || ''),
            contract_name: this.sanitizeInput(document.getElementById('contract_name')?.value || ''),
            start_date: this.sanitizeInput(document.getElementById('start_date')?.value || ''),
            end_date: this.sanitizeInput(document.getElementById('end_date')?.value || ''),
            total_days: parseInt(document.getElementById('total_days')?.value) || 0,
            daily_rate: parseFloat(document.getElementById('daily_rate')?.value) || 0
        };
    }

    sanitizeInput(value) {
        if (typeof value !== 'string') {
            return value;
        }
        
        // Remove null bytes and control characters
        value = value.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '');
        
        // Trim whitespace
        value = value.trim();
        
        // HTML escape
        value = value.replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/"/g, '&quot;')
                    .replace(/'/g, '&#x27;');
        
        return value;
    }

    validateDates() {
        const startDate = document.getElementById('start_date')?.value;
        const endDate = document.getElementById('end_date')?.value;

        if (startDate && endDate) {
            const start = new Date(startDate);
            const end = new Date(endDate);

            if (end <= start) {
                this.showFieldError('end_date', 'End date must be after start date');
            } else {
                this.clearFieldError('end_date');
            }
        }
    }

    showFieldError(fieldName, message) {
        const field = document.getElementById(fieldName);
        if (field) {
            field.classList.add('is-invalid');
            
            let feedback = field.parentNode.querySelector('.invalid-feedback');
            if (!feedback) {
                feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                field.parentNode.appendChild(feedback);
            }
            feedback.textContent = message;
        }
    }

    clearFieldError(fieldName) {
        const field = document.getElementById(fieldName);
        if (field) {
            field.classList.remove('is-invalid');
            const feedback = field.parentNode.querySelector('.invalid-feedback');
            if (feedback) {
                feedback.remove();
            }
        }
    }

    async handleSubmit(event) {
        event.preventDefault();
        
        const submitButton = event.target.querySelector('button[type="submit"]');
        const originalText = submitButton.innerHTML;
        
        try {
            // Disable form and show loading
            this.setFormLoading(true, submitButton);
            
            const formData = this.getFormData();
            
            // Validate form data
            const validation = this.validateForm(formData);
            if (!validation.isValid) {
                throw new Error(validation.errors.join(', '));
            }
            
            // Submit to API
            const response = await Utils.apiRequest('/api/contracts/', {
                method: 'POST',
                body: JSON.stringify(formData)
            });
            
            if (response.success) {
                showFlashMessage('Contract created successfully!', 'success');
                
                // Redirect to contract calendar
                window.location.href = `/contracts/${encodeURIComponent(response.contract_key)}/calendar`;
            } else {
                throw new Error(response.error || 'Failed to create contract');
            }
            
        } catch (error) {
            console.error('Error creating contract:', error);
            showFlashMessage(error.message || 'Failed to create contract', 'danger');
        } finally {
            this.setFormLoading(false, submitButton, originalText);
        }
    }

    validateForm(formData) {
        const errors = [];
        
        // Required field validation
        const requiredFields = {
            'staff_name': 'Staff name',
            'client_company': 'Client company',
            'contract_name': 'Contract name',
            'start_date': 'Start date',
            'end_date': 'End date',
            'total_days': 'Total days',
            'daily_rate': 'Daily rate'
        };
        
        Object.entries(requiredFields).forEach(([field, label]) => {
            if (!formData[field] || formData[field].toString().trim() === '') {
                errors.push(`${label} is required`);
                this.showFieldError(field, `${label} is required`);
            } else {
                this.clearFieldError(field);
            }
        });
        
        // Date validation
        if (formData.start_date && formData.end_date) {
            const start = new Date(formData.start_date);
            const end = new Date(formData.end_date);
            
            if (end <= start) {
                errors.push('End date must be after start date');
                this.showFieldError('end_date', 'End date must be after start date');
            }
        }
        
        // Number validation
        if (formData.total_days && (formData.total_days < 1 || formData.total_days > 365)) {
            errors.push('Total days must be between 1 and 365');
            this.showFieldError('total_days', 'Total days must be between 1 and 365');
        }
        
        if (formData.daily_rate && formData.daily_rate < 0) {
            errors.push('Daily rate must be positive');
            this.showFieldError('daily_rate', 'Daily rate must be positive');
        }
        
        return {
            isValid: errors.length === 0,
            errors: errors
        };
    }

    setFormLoading(loading, button, originalText = null) {
        const form = document.getElementById('new-contract-form');
        const inputs = form.querySelectorAll('input, select, textarea, button');
        
        inputs.forEach(input => {
            input.disabled = loading;
        });
        
        if (button) {
            if (loading) {
                button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Creating...';
            } else if (originalText) {
                button.innerHTML = originalText;
            }
        }
    }
}

// Initialize form when page loads
document.addEventListener('DOMContentLoaded', function() {
    new NewContractForm();
});
