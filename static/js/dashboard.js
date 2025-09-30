/**
 * Dashboard JavaScript
 */

class Dashboard {
    constructor() {
        this.contracts = [];
        this.settings = {};
        this.init();
    }

    async init() {
        try {
            await this.loadDashboardData();
            this.renderDashboard();
        } catch (error) {
            console.error('Failed to initialize dashboard:', error);
            this.showError('Failed to load dashboard data');
        }
    }

    async loadDashboardData() {
        const data = await Utils.apiRequest('/api/dashboard/');
        
        if (data.success) {
            this.contracts = data.dashboard.contracts;
            this.settings = data.settings;
        } else {
            throw new Error(data.error || 'Failed to load dashboard data');
        }
    }

    renderDashboard() {
        this.updateStats();
        this.renderContracts();
    }

    updateStats() {
        const totalContracts = this.contracts.length;
        const totalValue = this.contracts.reduce((sum, contract) => sum + contract.total_value, 0);
        const totalEarned = this.contracts.reduce((sum, contract) => sum + contract.earned_value, 0);
        const totalRemaining = totalValue - totalEarned;

        document.getElementById('total-contracts').textContent = totalContracts;
        document.getElementById('total-value').textContent = Utils.formatCurrency(totalValue);
        document.getElementById('total-earned').textContent = Utils.formatCurrency(totalEarned);
        document.getElementById('total-remaining').textContent = Utils.formatCurrency(totalRemaining);
    }

    renderContracts() {
        const container = document.getElementById('contracts-container');
        const loadingState = document.getElementById('loading-state');
        const emptyState = document.getElementById('empty-state');

        // Hide loading state
        if (loadingState) {
            loadingState.style.display = 'none';
        }

        if (this.contracts.length === 0) {
            // Show empty state
            if (emptyState) {
                emptyState.style.display = 'block';
            }
            if (container) {
                container.innerHTML = '';
            }
            return;
        }

        // Hide empty state
        if (emptyState) {
            emptyState.style.display = 'none';
        }

        // Render contracts
        if (container) {
            container.innerHTML = '';
            this.contracts.forEach(contract => {
                const contractCard = this.createContractCard(contract);
                container.appendChild(contractCard);
            });
        }
    }

    createContractCard(contract) {
        const card = document.createElement('div');
        card.className = 'contract-card card mb-4 fade-in';
        card.setAttribute('data-contract-key', contract.key);

        const progressPercentage = contract.total_days > 0 ? 
            (contract.working_days_count / contract.total_days * 100) : 0;

        const healthScoreColor = contract.health_score.score >= 80 ? 'success' : 
                                contract.health_score.score >= 60 ? 'warning' : 'danger';

        card.innerHTML = `
            <div class="card-header d-flex justify-content-between align-items-center">
                <div>
                    <h5 class="card-title mb-0">${contract.client_company}</h5>
                    <small class="text-muted">${contract.staff_name} - ${contract.contract_name}</small>
                </div>
                <div class="contract-status">
                    ${contract.is_balanced ? 
                        '<span class="badge bg-success"><i class="fas fa-check-circle me-1"></i>Balanced</span>' :
                        `<span class="badge bg-warning"><i class="fas fa-exclamation-triangle me-1"></i>${contract.remaining_days} days remaining</span>`
                    }
                </div>
            </div>
            
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <div class="contract-info">
                            <p class="mb-1">
                                <strong><i class="fas fa-calendar-alt me-2"></i>Period:</strong>
                                ${Utils.formatDate(contract.start_date)} to ${Utils.formatDate(contract.end_date)}
                            </p>
                            <p class="mb-1">
                                <strong><i class="fas fa-pound-sign me-2"></i>Rate:</strong>
                                £${contract.daily_rate}/day
                            </p>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="contract-stats">
                            <p class="mb-1">
                                <strong><i class="fas fa-briefcase me-2"></i>Days:</strong>
                                ${contract.working_days_count} / ${contract.total_days}
                            </p>
                            <p class="mb-1">
                                <strong><i class="fas fa-chart-line me-2"></i>Value:</strong>
                                ${Utils.formatCurrency(contract.earned_value)} / ${Utils.formatCurrency(contract.total_value)}
                            </p>
                        </div>
                    </div>
                </div>
                
                <!-- Progress Bar -->
                <div class="progress mt-3" style="height: 8px;">
                    <div class="progress-bar" 
                         role="progressbar" 
                         style="width: ${progressPercentage}%"
                         aria-valuenow="${progressPercentage}" 
                         aria-valuemin="0" 
                         aria-valuemax="100">
                    </div>
                </div>
                <small class="text-muted">${progressPercentage.toFixed(1)}% complete</small>
                
                <!-- Health Score -->
                <div class="health-score mt-2">
                    <small class="text-muted">
                        <i class="fas fa-heartbeat me-1"></i>
                        Health: ${contract.health_score.score}/100 
                        <span class="badge bg-${healthScoreColor}">
                            ${contract.health_score.status}
                        </span>
                    </small>
                </div>
            </div>
            
            <div class="card-footer">
                <div class="d-flex justify-content-between">
                    <div>
                        <a href="/contracts/${contract.key}/calendar" class="btn btn-primary btn-sm">
                            <i class="fas fa-calendar me-1"></i>
                            Calendar
                        </a>
                        <a href="/contracts/${contract.key}" class="btn btn-outline-secondary btn-sm ms-2">
                            <i class="fas fa-eye me-1"></i>
                            Details
                        </a>
                    </div>
                    <div>
                        <button class="btn btn-outline-danger btn-sm" 
                                onclick="dashboard.deleteContract('${contract.key}')">
                            <i class="fas fa-trash me-1"></i>
                            Delete
                        </button>
                    </div>
                </div>
            </div>
        `;

        return card;
    }

    async deleteContract(contractKey) {
        if (!confirm('Are you sure you want to delete this contract? This action cannot be undone.')) {
            return;
        }

        try {
            const data = await Utils.apiRequest(`/api/contracts/${contractKey}`, {
                method: 'DELETE'
            });

            if (data.success) {
                showFlashMessage('Contract deleted successfully', 'success');
                
                // Remove contract from local data
                this.contracts = this.contracts.filter(contract => contract.key !== contractKey);
                
                // Update display
                this.updateStats();
                this.renderContracts();
            } else {
                throw new Error(data.error || 'Failed to delete contract');
            }
        } catch (error) {
            console.error('Error deleting contract:', error);
            showFlashMessage(error.message || 'Failed to delete contract', 'danger');
        }
    }

    async refresh() {
        try {
            const loadingState = document.getElementById('loading-state');
            if (loadingState) {
                loadingState.style.display = 'block';
            }

            await this.loadDashboardData();
            this.renderDashboard();

            showFlashMessage('Dashboard refreshed successfully', 'success');
        } catch (error) {
            console.error('Failed to refresh dashboard:', error);
            this.showError('Failed to refresh dashboard');
        }
    }

    showError(message) {
        showFlashMessage(message, 'danger');
        
        const loadingState = document.getElementById('loading-state');
        const emptyState = document.getElementById('empty-state');
        
        if (loadingState) {
            loadingState.style.display = 'none';
        }
        
        if (emptyState) {
            emptyState.style.display = 'block';
            emptyState.innerHTML = `
                <i class="fas fa-exclamation-triangle fa-3x text-danger mb-3"></i>
                <h4 class="text-danger">Error Loading Dashboard</h4>
                <p class="text-muted">${message}</p>
                <button class="btn btn-primary" onclick="dashboard.refresh()">
                    <i class="fas fa-sync-alt me-2"></i>
                    Try Again
                </button>
            `;
        }
    }
}

// Global functions
function refreshDashboard() {
    if (window.dashboard) {
        window.dashboard.refresh();
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.dashboard = new Dashboard();
});
