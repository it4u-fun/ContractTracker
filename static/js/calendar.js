/**
 * Contract Calendar JavaScript
 */

class ContractCalendar {
    constructor() {
        this.contract = null;
        this.contractKey = null;
        this.calendarMonths = [];
        this.currentSelectedDate = null;
        this.init();
    }

    async init() {
        // Get contract key from URL
        const pathParts = window.location.pathname.split('/');
        this.contractKey = pathParts[pathParts.length - 2]; // Assuming URL is /contracts/{key}/calendar
        
        if (!this.contractKey) {
            this.showError('Contract key not found in URL');
            return;
        }

        try {
            await this.loadContract();
            this.updateContractInfo();
            this.renderCalendar();
            this.setupEventListeners();
        } catch (error) {
            console.error('Failed to initialize calendar:', error);
            this.showError('Failed to load contract calendar');
        }
    }

    async loadContract() {
        const data = await Utils.apiRequest(`/api/contracts/${this.contractKey}`);
        
        if (data.success) {
            this.contract = data.contract;
            
            // Generate calendar months
            const startDate = new Date(this.contract.start_date);
            const endDate = new Date(this.contract.end_date);
            
            this.calendarMonths = this.generateCalendarMonths(startDate, endDate);
        } else {
            throw new Error(data.error || 'Failed to load contract');
        }
    }

    generateCalendarMonths(startDate, endDate) {
        const months = [];
        const current = new Date(startDate.getFullYear(), startDate.getMonth(), 1);
        
        while (current <= endDate) {
            const monthData = {
                year: current.getFullYear(),
                month: current.getMonth() + 1,
                monthName: current.toLocaleDateString('en-GB', { month: 'long', year: 'numeric' }),
                weeks: this.generateMonthWeeks(current.getFullYear(), current.getMonth() + 1, startDate, endDate)
            };
            
            months.push(monthData);
            
            // Move to next month
            current.setMonth(current.getMonth() + 1);
        }
        
        return months;
    }

    generateMonthWeeks(year, month, contractStart, contractEnd) {
        const firstDay = new Date(year, month - 1, 1);
        const lastDay = new Date(year, month, 0);
        const firstWeekday = firstDay.getDay();
        
        const weeks = [];
        let currentWeek = [];
        
        // Add empty cells for days before the first day of the month
        for (let i = 0; i < firstWeekday; i++) {
            currentWeek.push(null);
        }
        
        // Add all days of the month
        for (let day = 1; day <= lastDay.getDate(); day++) {
            const currentDate = new Date(year, month - 1, day);
            const dateString = currentDate.toISOString().split('T')[0];
            
            const dayData = {
                day: day,
                date: dateString,
                isWeekend: currentDate.getDay() >= 5,
                isOutsidePeriod: currentDate < contractStart || currentDate > contractEnd,
                status: this.getDayStatus(dateString),
                isCurrentMonth: true
            };
            
            currentWeek.push(dayData);
            
            // If week is complete, add it and start new week
            if (currentWeek.length === 7) {
                weeks.push(currentWeek);
                currentWeek = [];
            }
        }
        
        // Add remaining empty cells to complete the last week
        while (currentWeek.length > 0 && currentWeek.length < 7) {
            currentWeek.push(null);
        }
        
        if (currentWeek.length > 0) {
            weeks.push(currentWeek);
        }
        
        return weeks;
    }

    getDayStatus(dateString) {
        if (this.contract && this.contract.days && this.contract.days[dateString]) {
            return this.contract.days[dateString].status;
        }
        return 'not_applicable';
    }

    updateContractInfo() {
        if (!this.contract) return;

        document.getElementById('contract-info').textContent = 
            `${this.contract.client_company} - ${this.contract.contract_name}`;
        
        document.getElementById('working-days-count').textContent = this.contract.working_days_count || 0;
        document.getElementById('remaining-days').textContent = this.contract.remaining_working_days || 0;
        document.getElementById('total-allowed').textContent = this.contract.total_days || 0;
        
        const balanceStatus = document.getElementById('balance-status');
        if (this.contract.is_balanced) {
            balanceStatus.textContent = 'Balanced';
            balanceStatus.className = 'badge bg-success';
        } else {
            balanceStatus.textContent = 'Not Balanced';
            balanceStatus.className = 'badge bg-warning';
        }
        
        // Update progress bar
        const progressPercentage = this.contract.total_days > 0 ? 
            (this.contract.working_days_count / this.contract.total_days * 100) : 0;
        const progressBar = document.getElementById('progress-bar');
        if (progressBar) {
            progressBar.style.width = `${progressPercentage}%`;
        }
    }

    renderCalendar() {
        const container = document.getElementById('calendar-container');
        const loadingState = document.getElementById('calendar-loading');
        
        if (loadingState) {
            loadingState.style.display = 'none';
        }
        
        if (container) {
            container.innerHTML = '';
            
            this.calendarMonths.forEach(month => {
                const monthElement = this.createMonthElement(month);
                container.appendChild(monthElement);
            });
        }
    }

    createMonthElement(month) {
        const monthDiv = document.createElement('div');
        monthDiv.className = 'calendar-month';
        
        monthDiv.innerHTML = `
            <h5 class="text-center mb-3">${month.monthName}</h5>
            <div class="calendar-grid">
                <div class="calendar-header row">
                    <div class="col text-center">Mon</div>
                    <div class="col text-center">Tue</div>
                    <div class="col text-center">Wed</div>
                    <div class="col text-center">Thu</div>
                    <div class="col text-center">Fri</div>
                    <div class="col text-center">Sat</div>
                    <div class="col text-center">Sun</div>
                </div>
                ${month.weeks.map(week => `
                    <div class="row">
                        ${week.map(day => day ? this.createDayElement(day) : '<div class="col calendar-day"></div>').join('')}
                    </div>
                `).join('')}
            </div>
        `;
        
        return monthDiv;
    }

    createDayElement(day) {
        const statusClass = `calendar-day ${day.status}`;
        const additionalClasses = [];
        
        if (day.isWeekend) additionalClasses.push('weekend');
        if (day.isOutsidePeriod) additionalClasses.push('outside-period');
        
        return `
            <div class="col ${statusClass} ${additionalClasses.join(' ')}" 
                 data-date="${day.date}"
                 onclick="calendar.selectDay('${day.date}')">
                <div class="day-number">${day.day}</div>
                ${day.isWeekend ? '<div class="weekend-indicator">W/E</div>' : ''}
            </div>
        `;
    }

    setupEventListeners() {
        // Setup modal event listeners
        const modal = document.getElementById('dayStatusModal');
        if (modal) {
            modal.addEventListener('hidden.bs.modal', () => {
                this.currentSelectedDate = null;
            });
        }
    }

    selectDay(dateString) {
        if (this.currentSelectedDate === dateString) {
            return; // Already selected
        }
        
        this.currentSelectedDate = dateString;
        this.showDayStatusModal(dateString);
    }

    showDayStatusModal(dateString) {
        const modal = document.getElementById('dayStatusModal');
        const dateInfo = document.getElementById('modal-date-info');
        const statusSelect = document.getElementById('day-status-select');
        const notesTextarea = document.getElementById('day-notes');
        
        if (!modal) return;
        
        // Update modal content
        const date = new Date(dateString);
        dateInfo.textContent = `Date: ${date.toLocaleDateString('en-GB', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        })}`;
        
        // Set current status
        const currentStatus = this.getDayStatus(dateString);
        statusSelect.value = currentStatus;
        
        // Clear notes
        notesTextarea.value = '';
        
        // Show modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    async saveDayStatus() {
        if (!this.currentSelectedDate) return;
        
        const statusSelect = document.getElementById('day-status-select');
        const notesTextarea = document.getElementById('day-notes');
        
        const status = statusSelect.value;
        const notes = notesTextarea.value;
        
        try {
            const data = await Utils.apiRequest(`/api/contracts/${this.contractKey}/days`, {
                method: 'POST',
                body: JSON.stringify({
                    date: this.currentSelectedDate,
                    status: status,
                    notes: notes
                })
            });
            
            if (data.success) {
                // Update local contract data
                if (!this.contract.days) {
                    this.contract.days = {};
                }
                this.contract.days[this.currentSelectedDate] = {
                    status: status,
                    notes: notes
                };
                
                // Update UI
                this.updateContractInfo();
                this.updateDayElement(this.currentSelectedDate, status);
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('dayStatusModal'));
                if (modal) {
                    modal.hide();
                }
                
                showFlashMessage('Day status updated successfully', 'success');
            } else {
                throw new Error(data.error || 'Failed to update day status');
            }
            
        } catch (error) {
            console.error('Error updating day status:', error);
            showFlashMessage(error.message || 'Failed to update day status', 'danger');
        }
    }

    updateDayElement(dateString, status) {
        const dayElement = document.querySelector(`[data-date="${dateString}"]`);
        if (dayElement) {
            // Remove old status classes
            dayElement.className = dayElement.className.replace(/working|bank_holiday|holiday|in_lieu|on_call|not_applicable/g, '');
            // Add new status class
            dayElement.classList.add(status);
        }
    }

    async showSuggestions() {
        try {
            const data = await Utils.apiRequest(`/api/contracts/${this.contractKey}/suggestions`);
            
            if (data.success) {
                this.displaySuggestions(data.suggestions);
            } else {
                throw new Error(data.error || 'Failed to get suggestions');
            }
        } catch (error) {
            console.error('Error getting suggestions:', error);
            showFlashMessage(error.message || 'Failed to get suggestions', 'danger');
        }
    }

    displaySuggestions(suggestions) {
        const modal = document.getElementById('suggestionsModal');
        const content = document.getElementById('suggestions-content');
        
        if (!modal || !content) return;
        
        content.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-lightbulb me-2"></i>
                ${suggestions.length} working days suggested for your contract period.
            </div>
            <div class="row">
                ${suggestions.map(date => `
                    <div class="col-md-3 col-sm-4 col-6 mb-2">
                        <div class="badge bg-primary">${Utils.formatDate(date)}</div>
                    </div>
                `).join('')}
            </div>
        `;
        
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    async applySuggestions() {
        try {
            const data = await Utils.apiRequest(`/api/contracts/${this.contractKey}/suggestions`, {
                method: 'POST',
                body: JSON.stringify({
                    suggested_dates: []
                })
            });
            
            if (data.success) {
                showFlashMessage('Suggestions applied successfully', 'success');
                
                // Refresh the calendar
                await this.loadContract();
                this.updateContractInfo();
                this.renderCalendar();
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('suggestionsModal'));
                if (modal) {
                    modal.hide();
                }
            } else {
                throw new Error(data.error || 'Failed to apply suggestions');
            }
        } catch (error) {
            console.error('Error applying suggestions:', error);
            showFlashMessage(error.message || 'Failed to apply suggestions', 'danger');
        }
    }

    async showValidation() {
        try {
            const data = await Utils.apiRequest(`/api/contracts/${this.contractKey}/validate`);
            
            if (data.success) {
                this.displayValidation(data.validation, data.health_score);
            } else {
                throw new Error(data.error || 'Failed to validate contract');
            }
        } catch (error) {
            console.error('Error validating contract:', error);
            showFlashMessage(error.message || 'Failed to validate contract', 'danger');
        }
    }

    displayValidation(validation, healthScore) {
        let message = `Contract Health: ${healthScore.score}/100 (${healthScore.status})`;
        
        if (validation.violations.length > 0) {
            message += '\n\nViolations:\n' + validation.violations.join('\n');
        }
        
        if (validation.warnings.length > 0) {
            message += '\n\nWarnings:\n' + validation.warnings.join('\n');
        }
        
        alert(message);
    }

    exportCalendar() {
        showFlashMessage('Calendar export feature coming soon!', 'info');
    }

    async refresh() {
        try {
            await this.loadContract();
            this.updateContractInfo();
            this.renderCalendar();
            showFlashMessage('Calendar refreshed successfully', 'success');
        } catch (error) {
            console.error('Error refreshing calendar:', error);
            showFlashMessage('Failed to refresh calendar', 'danger');
        }
    }

    showError(message) {
        const container = document.getElementById('calendar-container');
        const loadingState = document.getElementById('calendar-loading');
        
        if (loadingState) {
            loadingState.style.display = 'none';
        }
        
        if (container) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-exclamation-triangle fa-3x text-danger mb-3"></i>
                    <h4 class="text-danger">Error Loading Calendar</h4>
                    <p class="text-muted">${message}</p>
                    <button class="btn btn-primary" onclick="calendar.refresh()">
                        <i class="fas fa-sync-alt me-2"></i>
                        Try Again
                    </button>
                </div>
            `;
        }
    }
}

// Global functions
function refreshCalendar() {
    if (window.calendar) {
        window.calendar.refresh();
    }
}

function showSuggestions() {
    if (window.calendar) {
        window.calendar.showSuggestions();
    }
}

function showValidation() {
    if (window.calendar) {
        window.calendar.showValidation();
    }
}

function exportCalendar() {
    if (window.calendar) {
        window.calendar.exportCalendar();
    }
}

function saveDayStatus() {
    if (window.calendar) {
        window.calendar.saveDayStatus();
    }
}

// Initialize calendar when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.calendar = new ContractCalendar();
});
