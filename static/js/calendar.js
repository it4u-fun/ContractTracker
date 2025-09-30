/**
 * Contract Calendar JavaScript
 */

class ContractCalendar {
    constructor() {
        this.contract = null;
        this.contractKey = null;
        this.calendarMonths = [];
        this.currentSelectedDate = null;
        this.dataSourceFlags = {};
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
            
            // Load data source information
            await this.loadDataSourceFlags();
            
            // Generate calendar months
            const startDate = new Date(this.contract.start_date);
            const endDate = new Date(this.contract.end_date);
            
            this.calendarMonths = this.generateCalendarMonths(startDate, endDate);
        } else {
            throw new Error(data.error || 'Failed to load contract');
        }
    }

    async loadDataSourceFlags() {
        try {
            // Load settings to get enabled data sources
            const settingsData = await Utils.apiRequest('/api/dashboard/settings');
            
            if (settingsData.success && settingsData.settings.enabled_data_sources) {
                this.dataSourceFlags = {};
                const settings = settingsData.settings;
                
                // Load UK Bank Holidays if enabled
                if (settings.enabled_data_sources.uk_bank_holidays) {
                    this.dataSourceFlags.uk_bank_holidays = this.getUKBankHolidays(
                        this.contract.start_date, 
                        this.contract.end_date
                    );
                }
                
                // Load School Holidays if enabled (placeholder for now)
                if (settings.enabled_data_sources.praewood_school) {
                    this.dataSourceFlags.school_holidays = this.getSchoolHolidays(
                        this.contract.start_date, 
                        this.contract.end_date
                    );
                }
                
                // Load Custom Holidays if enabled
                if (settings.enabled_data_sources.custom_holidays) {
                    this.dataSourceFlags.custom_holidays = await this.getCustomHolidays(
                        this.contract.start_date, 
                        this.contract.end_date
                    );
                }
            }
        } catch (error) {
            console.warn('Failed to load data source flags:', error);
            this.dataSourceFlags = {};
        }
    }

    getUKBankHolidays(startDate, endDate) {
        const holidays = [];
        const startYear = new Date(startDate).getFullYear();
        const endYear = new Date(endDate).getFullYear();
        
        for (let year = startYear; year <= endYear; year++) {
            // New Year's Day
            holidays.push(`${year}-01-01`);
            
            // Good Friday (approximate calculation)
            const easter = this.calculateEaster(year);
            const goodFriday = new Date(easter);
            goodFriday.setDate(easter.getDate() - 2);
            holidays.push(goodFriday.toISOString().split('T')[0]);
            
            // Easter Monday
            const easterMonday = new Date(easter);
            easterMonday.setDate(easter.getDate() + 1);
            holidays.push(easterMonday.toISOString().split('T')[0]);
            
            // Early May Bank Holiday (first Monday in May)
            const mayBankHoliday = this.getFirstMondayInMonth(year, 5);
            holidays.push(mayBankHoliday);
            
            // Spring Bank Holiday (last Monday in May)
            const springBankHoliday = this.getLastMondayInMonth(year, 5);
            holidays.push(springBankHoliday);
            
            // Summer Bank Holiday (last Monday in August)
            const summerBankHoliday = this.getLastMondayInMonth(year, 8);
            holidays.push(summerBankHoliday);
            
            // Christmas Day
            holidays.push(`${year}-12-25`);
            
            // Boxing Day
            holidays.push(`${year}-12-26`);
        }
        
        // Filter to contract period
        return holidays.filter(date => date >= startDate && date <= endDate);
    }
    
    getSchoolHolidays(startDate, endDate) {
        // Placeholder for PraeWood School holidays
        // This would be populated from actual school calendar data
        return [];
    }
    
    async getCustomHolidays(startDate, endDate) {
        try {
            const response = await Utils.apiRequest(`/api/custom-holidays/range?start_date=${startDate}&end_date=${endDate}`);
            
            if (response.success) {
                // Convert holidays to date flags
                const holidayFlags = {};
                response.holidays.forEach(holiday => {
                    const dates = this.getHolidayDates(holiday.start_date, holiday.end_date);
                    dates.forEach(date => {
                        holidayFlags[date] = {
                            type: 'custom_holiday',
                            name: holiday.name,
                            description: holiday.description,
                            holiday_type: holiday.holiday_type
                        };
                    });
                });
                return holidayFlags;
            }
        } catch (error) {
            console.warn('Failed to load custom holidays:', error);
        }
        return {};
    }
    
    getHolidayDates(startDate, endDate) {
        const dates = [];
        const start = new Date(startDate);
        const end = new Date(endDate);
        
        const current = new Date(start);
        while (current <= end) {
            dates.push(current.toISOString().split('T')[0]);
            current.setDate(current.getDate() + 1);
        }
        
        return dates;
    }
    
    calculateEaster(year) {
        // Simplified Easter calculation (Gauss algorithm)
        const a = year % 19;
        const b = Math.floor(year / 100);
        const c = year % 100;
        const d = Math.floor(b / 4);
        const e = b % 4;
        const f = Math.floor((b + 8) / 25);
        const g = Math.floor((b - f + 1) / 3);
        const h = (19 * a + b - d - g + 15) % 30;
        const i = Math.floor(c / 4);
        const k = c % 4;
        const l = (32 + 2 * e + 2 * i - h - k) % 7;
        const m = Math.floor((a + 11 * h + 22 * l) / 451);
        const month = Math.floor((h + l - 7 * m + 114) / 31);
        const day = ((h + l - 7 * m + 114) % 31) + 1;
        
        return new Date(year, month - 1, day);
    }
    
    getFirstMondayInMonth(year, month) {
        const date = new Date(year, month - 1, 1);
        const dayOfWeek = date.getDay();
        const daysUntilMonday = dayOfWeek === 0 ? 1 : 8 - dayOfWeek;
        date.setDate(daysUntilMonday);
        return date.toISOString().split('T')[0];
    }
    
    getLastMondayInMonth(year, month) {
        const date = new Date(year, month, 0); // Last day of month
        const dayOfWeek = date.getDay();
        const daysBackToMonday = dayOfWeek === 0 ? 6 : dayOfWeek - 1;
        date.setDate(date.getDate() - daysBackToMonday);
        return date.toISOString().split('T')[0];
    }

    getDataSourceFlags(dateString) {
        const flags = [];
        
        if (this.dataSourceFlags) {
            // Check UK Bank Holidays
            if (this.dataSourceFlags.uk_bank_holidays && 
                this.dataSourceFlags.uk_bank_holidays.includes(dateString)) {
                flags.push({
                    type: 'bank_holiday',
                    label: 'Bank Holiday',
                    icon: '🏛️'
                });
            }
            
            // Check School Holidays
            if (this.dataSourceFlags.school_holidays && 
                this.dataSourceFlags.school_holidays.includes(dateString)) {
                flags.push({
                    type: 'school_holiday',
                    label: 'School Holiday',
                    icon: '🎓'
                });
            }
            
            // Check Custom Holidays
            if (this.dataSourceFlags.custom_holidays && 
                this.dataSourceFlags.custom_holidays[dateString]) {
                const holiday = this.dataSourceFlags.custom_holidays[dateString];
                const icon = this.getCustomHolidayIcon(holiday.holiday_type);
                flags.push({
                    type: 'custom_holiday',
                    label: holiday.name,
                    icon: icon,
                    description: holiday.description,
                    holiday_type: holiday.holiday_type
                });
            }
        }
        
        return flags;
    }
    
    getCustomHolidayIcon(holidayType) {
        const icons = {
            'bank_holiday': '🏛️',
            'office_closure': '🚫',
            'personal_holiday': '🏖️'
        };
        return icons[holidayType] || '📅';
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
        // Convert JavaScript getDay() (Sunday=0) to Monday-based (Monday=0)
        const firstWeekday = (firstDay.getDay() + 6) % 7;
        
        const weeks = [];
        let currentWeek = [];
        
        // Add empty cells for days before the first day of the month
        for (let i = 0; i < firstWeekday; i++) {
            currentWeek.push(null);
        }
        
        // Add all days of the month
        for (let day = 1; day <= lastDay.getDate(); day++) {
            const currentDate = new Date(year, month - 1, day);
            // Use timezone-safe date formatting to avoid UTC conversion issues
            const dateString = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            
            const dayData = {
                day: day,
                date: dateString,
                isWeekend: currentDate.getDay() === 0 || currentDate.getDay() === 6, // Sunday (0) or Saturday (6)
                isOutsidePeriod: currentDate < contractStart || currentDate > contractEnd,
                status: this.getDayStatus(dateString),
                isCurrentMonth: true,
                dataSourceFlags: this.getDataSourceFlags(dateString)
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
        return 'holiday';
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
        
        // Hide loading state
        if (loadingState) {
            loadingState.style.display = 'none';
        }
        
        // Show calendar container
        if (container) {
            container.style.display = 'block';
            container.innerHTML = '';
            
            this.calendarMonths.forEach(month => {
                const monthElement = this.createMonthElement(month);
                container.appendChild(monthElement);
            });
        }
        
        // Show data source legend if there are any flags
        this.updateDataSourceLegend();
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
        
        // Create data source flag indicators
        let dataSourceIndicators = '';
        if (day.dataSourceFlags && day.dataSourceFlags.length > 0) {
            dataSourceIndicators = day.dataSourceFlags.map(flag => 
                `<div class="data-source-flag ${flag.type}" title="${flag.label}">${flag.icon}</div>`
            ).join('');
        }
        // Add suggestion overlay bar if date is in current suggestions
        let suggestionBar = '';
        if (this.currentSuggestions && Array.isArray(this.currentSuggestions) && this.currentSuggestions.includes(day.date)) {
            suggestionBar = '<div class="suggestion-bar" title="Suggested working day"></div>';
        }
        
        // Determine if day is clickable
        const clickable = !day.isOutsidePeriod;
        const clickHandler = clickable ? `onclick="calendar.toggleDay('${day.date}')"` : '';
        
        return `
            <div class="col ${statusClass} ${additionalClasses.join(' ')} ${!clickable ? 'non-clickable' : ''}" 
                 data-date="${day.date}"
                 ${clickHandler}>
                ${suggestionBar}
                <div class="day-number">${day.day}</div>
                ${day.isWeekend ? '<div class="weekend-indicator">W/E</div>' : ''}
                ${dataSourceIndicators}
                ${day.isOutsidePeriod ? '<div class="outside-period-indicator">Outside Contract</div>' : ''}
            </div>
        `;
    }
    async toggleDay(dateString) {
        // Determine next status: only two states supported (working/holiday)
        const current = this.getDayStatus(dateString);
        const nextStatus = current === 'working' ? 'holiday' : 'working';

        try {
            const data = await Utils.apiRequest(`/api/contracts/${this.contractKey}/days`, {
                method: 'POST',
                body: JSON.stringify({
                    date: dateString,
                    status: nextStatus,
                    notes: ''
                })
            });
            
            if (data.success) {
                // Update local contract day
                if (!this.contract.days) {
                    this.contract.days = {};
                }
                this.contract.days[dateString] = { status: nextStatus, notes: '' };
                // Sync counters from server response
                if (typeof data.working_days_count === 'number') {
                    this.contract.working_days_count = data.working_days_count;
                }
                if (typeof data.remaining_days === 'number') {
                    this.contract.remaining_working_days = data.remaining_days;
                }
                if (typeof data.is_balanced === 'boolean') {
                    this.contract.is_balanced = data.is_balanced;
                }

                this.updateContractInfo();
                this.updateDayElement(dateString, nextStatus);
            } else {
                throw new Error(data.error || 'Failed to update day status');
            }
        } catch (error) {
            console.error('Error toggling day status:', error);
            showFlashMessage(error.message || 'Failed to update day status', 'danger');
        }
    }


    updateDataSourceLegend() {
        const legend = document.getElementById('data-source-legend');
        if (!legend) return;
        
        // Check if there are any data source flags in the calendar
        let hasFlags = false;
        
        if (this.dataSourceFlags) {
            // Check if any data sources have dates
            if ((this.dataSourceFlags.uk_bank_holidays && this.dataSourceFlags.uk_bank_holidays.length > 0) ||
                (this.dataSourceFlags.school_holidays && this.dataSourceFlags.school_holidays.length > 0) ||
                (this.dataSourceFlags.custom_holidays && Object.keys(this.dataSourceFlags.custom_holidays).length > 0)) {
                hasFlags = true;
            }
        }
        
        // Show legend if there are flags or outside period days
        if (hasFlags || this.hasOutsidePeriodDays()) {
            legend.style.display = 'block';
        } else {
            legend.style.display = 'none';
        }
    }
    
    hasOutsidePeriodDays() {
        // Check if any calendar months have outside period days
        return this.calendarMonths.some(month => 
            month.weeks.some(week => 
                week.some(day => day && day.isOutsidePeriod)
            )
        );
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
            // Remove old status classes (only two supported)
            dayElement.className = dayElement.className.replace(/\bworking\b|\bholiday\b/g, '');
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
        
        // Persist current suggestions for later apply
        this.currentSuggestions = suggestions.slice();

        content.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-lightbulb me-2"></i>
                ${suggestions.length} working days suggested for your contract period.
            </div>
            <div class="row">
                ${suggestions.map(date => `
                    <div class="col-md-6 col-lg-4 mb-2 suggestion-item" data-date="${date}">
                        <div class="d-flex align-items-center gap-2">
                            <span class="badge bg-primary flex-shrink-0" style="min-width: 120px; text-align:center;">${Utils.formatDate(date)}</span>
                            <input type="text" class="form-control form-control-sm suggestion-note" data-date="${date}" placeholder="Add a comment (optional)" />
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    async applySuggestions() {
        try {
            // Collect dates and optional notes from the modal
            const container = document.getElementById('suggestions-content');
            const itemNodes = container ? container.querySelectorAll('.suggestion-item') : [];
            const suggestedDates = [];
            const notesByDate = {};
            itemNodes.forEach(item => {
                const date = item.getAttribute('data-date');
                if (!date) return;
                suggestedDates.push(date);
                const noteInput = item.querySelector('.suggestion-note');
                if (noteInput && noteInput.value && noteInput.value.trim().length > 0) {
                    notesByDate[date] = noteInput.value.trim();
                }
            });

            const data = await Utils.apiRequest(`/api/contracts/${this.contractKey}/suggestions`, {
                method: 'POST',
                body: JSON.stringify({
                    suggested_dates: suggestedDates,
                    notes_by_date: notesByDate
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
