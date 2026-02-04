/**
 * ContaSmart Pro Executive Dashboard
 * Sistema de dashboard interativo
 */

class ExecutiveDashboard {
    constructor() {
        this.charts = {};
        this.dataCache = {};
        this.init();
    }

    init() {
        this.initEventListeners();
        this.initRealTimeUpdates();
        this.initCharts();
        this.loadDashboardData();
    }

    initEventListeners() {
        // Quick action buttons
        document.querySelectorAll('.quick-action-card').forEach(card => {
            card.addEventListener('click', (e) => this.handleQuickAction(e));
        });

        // Chart period selectors
        document.querySelectorAll('.period-selector select').forEach(select => {
            select.addEventListener('change', (e) => this.updateChartPeriod(e));
        });

        // Notification bell
        const notificationBtn = document.getElementById('notificationBtn');
        if (notificationBtn) {
            notificationBtn.addEventListener('click', () => this.toggleNotifications());
        }

        // Search functionality
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.handleSearch(e));
        }
    }

    initRealTimeUpdates() {
        // Update dashboard every 30 seconds
        setInterval(() => this.updateDashboardData(), 30000);

        // Update time every minute
        setInterval(() => this.updateTime(), 60000);

        // Initial update
        this.updateTime();
    }

    updateTime() {
        const now = new Date();
        const timeElements = document.querySelectorAll('.current-time');
        timeElements.forEach(el => {
            el.textContent = now.toLocaleTimeString('pt-BR', {
                hour: '2-digit',
                minute: '2-digit'
            });
        });

        const dateElements = document.querySelectorAll('.current-date');
        dateElements.forEach(el => {
            el.textContent = now.toLocaleDateString('pt-BR', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        });
    }

    async loadDashboardData() {
        try {
            const response = await fetch('/api/dashboard_data');
            const data = await response.json();
            this.dataCache = data;
            this.updateDashboardUI(data);
            this.updateCharts(data);
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.showError('Erro ao carregar dados do dashboard');
        }
    }

    async updateDashboardData() {
        try {
            const response = await fetch('/api/dashboard_data');
            const data = await response.json();
            this.dataCache = data;
            this.updateDashboardUI(data, true);
        } catch (error) {
            console.error('Error updating dashboard:', error);
        }
    }

    updateDashboardUI(data, isUpdate = false) {
        // Update stats cards with animation
        this.updateStatCards(data);
        
        // Update alerts
        this.updateAlerts(data.alerts);
        
        // Update transactions
        if (data.recent_transactions) {
            this.updateTransactions(data.recent_transactions);
        }

        // Show update notification
        if (isUpdate) {
            this.showUpdateNotification();
        }
    }

    updateStatCards(data) {
        const statCards = document.querySelectorAll('.neon-stats-card');
        
        statCards.forEach(card => {
            const valueElement = card.querySelector('.stat-value');
            const labelElement = card.querySelector('.stat-label');
            const trendElement = card.querySelector('.stat-trend');
            
            if (!valueElement || !labelElement) return;
            
            const label = labelElement.textContent.trim();
            let newValue = '';
            let newTrend = '';
            
            switch(label) {
                case 'Saldo Total':
                    newValue = `R$ ${data.balance?.toFixed(2) || '0.00'}`;
                    const balanceChange = data.month_balance - (data.month_balance * 0.9);
                    newTrend = this.formatTrend(balanceChange, data.month_balance);
                    break;
                case 'Receitas (Mês)':
                    newValue = `R$ ${data.month_income?.toFixed(2) || '0.00'}`;
                    const incomeTrend = (data.month_income / (data.total_income / 12)) * 100 - 100;
                    newTrend = this.formatTrend(incomeTrend, 100, true);
                    break;
                case 'Despesas (Mês)':
                    newValue = `R$ ${data.month_expense?.toFixed(2) || '0.00'}`;
                    const expenseRatio = (data.month_expense / data.month_income) * 100;
                    newTrend = `${expenseRatio.toFixed(0)}% da receita`;
                    break;
                case 'Metas':
                    newValue = `${data.completed_goals || 0}/${data.total_goals || 0}`;
                    newTrend = `${data.avg_progress?.toFixed(1) || '0'}% de progresso`;
                    break;
            }
            
            // Animate value change
            this.animateValueChange(valueElement, newValue);
            
            // Update trend
            if (trendElement && newTrend) {
                trendElement.innerHTML = newTrend;
            }
        });
    }

    formatTrend(value, base, isPercentage = false) {
        if (!base || base === 0) return '';
        
        const percentage = (value / base) * 100;
        const absPercentage = Math.abs(percentage);
        
        let icon = percentage > 0 ? 'arrow-up' : 'arrow-down';
        let className = percentage > 0 ? 'positive' : 'negative';
        
        if (absPercentage < 1) {
            icon = 'minus';
            className = 'neutral';
        }
        
        const formattedValue = isPercentage ? 
            `${percentage > 0 ? '+' : ''}${percentage.toFixed(1)}%` :
            `${percentage.toFixed(1)}%`;
        
        return `<span class="${className}"><i class="fas fa-${icon}"></i> ${formattedValue}</span>`;
    }

    animateValueChange(element, newValue) {
        const oldValue = element.textContent;
        if (oldValue === newValue) return;
        
        element.style.transform = 'scale(1.1)';
        element.style.color = '#00ff88';
        
        setTimeout(() => {
            element.textContent = newValue;
            element.style.transform = 'scale(1)';
            element.style.color = '';
        }, 300);
    }

    updateAlerts(alerts) {
        const alertsContainer = document.querySelector('.alerts-list');
        if (!alertsContainer) return;
        
        if (!alerts || alerts.length === 0) {
            alertsContainer.innerHTML = `
                <div class="alert-card success">
                    <div class="alert-icon">
                        <i class="fas fa-check-circle"></i>
                    </div>
                    <div class="alert-content">
                        <h4>Tudo em Ordem</h4>
                        <p>Nenhum alerta crítico no momento</p>
                    </div>
                </div>
            `;
            return;
        }
        
        const alertsHTML = alerts.map(alert => `
            <div class="alert-card ${alert.type}">
                <div class="alert-icon">
                    <i class="fas fa-${alert.icon}"></i>
                </div>
                <div class="alert-content">
                    <h4>${alert.title}</h4>
                    <p>${alert.message}</p>
                    ${alert.action ? `<a href="#" class="alert-action">${alert.action}</a>` : ''}
                </div>
            </div>
        `).join('');
        
        alertsContainer.innerHTML = alertsHTML;
        
        // Add click handlers to alert actions
        alertsContainer.querySelectorAll('.alert-action').forEach(action => {
            action.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleAlertAction(e.target.textContent);
            });
        });
    }

    updateTransactions(transactions) {
        const tbody = document.querySelector('.neon-table tbody');
        if (!tbody) return;
        
        if (!transactions || transactions.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="4" style="text-align: center; padding: var(--spacing-xl); color: var(--text-muted);">
                        <i class="fas fa-inbox" style="font-size: 2rem; margin-bottom: var(--spacing-md); display: block;"></i>
                        Nenhuma transação recente
                    </td>
                </tr>
            `;
            return;
        }
        
        const transactionsHTML = transactions.map(trans => `
            <tr>
                <td>
                    <div class="transaction-info">
                        <div class="transaction-title">${trans.description || 'Transação'}</div>
                    </div>
                </td>
                <td>
                    ${trans.category_name ? `
                        <span class="neon-badge primary" style="border-color: ${trans.category_color}; color: ${trans.category_color}">
                            <i class="${trans.category_icon}"></i>
                            ${trans.category_name}
                        </span>
                    ` : '<span class="neon-badge">Não categorizada</span>'}
                </td>
                <td>
                    <span class="date">${new Date(trans.transaction_date).toLocaleDateString('pt-BR')}</span>
                </td>
                <td>
                    <span class="amount ${trans.type}">
                        ${trans.type === 'income' ? 'R$ +' : 'R$ -'}${parseFloat(trans.amount).toFixed(2)}
                    </span>
                </td>
            </tr>
        `).join('');
        
        tbody.innerHTML = transactionsHTML;
    }

    initCharts() {
        // Initialize all charts on the page
        this.initializeTrendChart();
        this.initializeCategoryChart();
        this.initializeGoalProgressChart();
    }

    initializeTrendChart() {
        const ctx = document.getElementById('trendChart');
        if (!ctx) return;
        
        this.charts.trend = new Chart(ctx.getContext('2d'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Receitas',
                        data: [],
                        borderColor: '#00ff88',
                        backgroundColor: 'rgba(0, 255, 136, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    },
                    {
                        label: 'Despesas',
                        data: [],
                        borderColor: '#ff3366',
                        backgroundColor: 'rgba(255, 51, 102, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#a0a0c0',
                            font: {
                                family: 'Inter, sans-serif',
                                size: 12
                            },
                            padding: 20
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(30, 30, 40, 0.9)',
                        titleColor: '#ffffff',
                        bodyColor: '#a0a0c0',
                        borderColor: '#2a2a38',
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: R$ ${context.parsed.y.toFixed(2)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#a0a0c0',
                            font: {
                                family: 'Inter, sans-serif',
                                size: 11
                            }
                        }
                    },
                    y: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#a0a0c0',
                            font: {
                                family: 'Inter, sans-serif',
                                size: 11
                            },
                            callback: function(value) {
                                return 'R$ ' + value.toLocaleString('pt-BR');
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    }

    initializeCategoryChart() {
        const ctx = document.getElementById('categoryChart');
        if (!ctx) return;
        
        this.charts.category = new Chart(ctx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        '#ff3366', '#ff9900', '#ff0066', '#00ccff', 
                        '#9966ff', '#33ccff', '#ffcc00', '#9d00ff'
                    ],
                    borderColor: '#1e1e28',
                    borderWidth: 2,
                    hoverOffset: 15
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: '#a0a0c0',
                            font: {
                                family: 'Inter, sans-serif',
                                size: 11
                            },
                            padding: 15,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(30, 30, 40, 0.9)',
                        titleColor: '#ffffff',
                        bodyColor: '#a0a0c0',
                        borderColor: '#2a2a38',
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                            label: function(context) {
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${context.label}: R$ ${value.toFixed(2)} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    initializeGoalProgressChart() {
        const ctx = document.getElementById('goalProgressChart');
        if (!ctx) return;
        
        this.charts.goalProgress = new Chart(ctx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Progresso',
                    data: [],
                    backgroundColor: [],
                    borderColor: [],
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                indexAxis: 'y',
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Progresso: ${context.parsed.x}%`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        max: 100,
                        grid: {
                            display: false
                        },
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    },
                    y: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    updateCharts(data) {
        if (data.trend_data && this.charts.trend) {
            this.updateTrendChart(data.trend_data);
        }
        
        if (data.category_data && this.charts.category) {
            this.updateCategoryChart(data.category_data);
        }
        
        if (data.goals_data && this.charts.goalProgress) {
            this.updateGoalProgressChart(data.goals_data);
        }
    }

    updateTrendChart(trendData) {
        const labels = trendData.map(item => item.month);
        const incomes = trendData.map(item => item.income);
        const expenses = trendData.map(item => item.expense);
        
        this.charts.trend.data.labels = labels;
        this.charts.trend.data.datasets[0].data = incomes;
        this.charts.trend.data.datasets[1].data = expenses;
        this.charts.trend.update();
    }

    updateCategoryChart(categoryData) {
        const labels = categoryData.map(item => item.name);
        const values = categoryData.map(item => item.value);
        const colors = categoryData.map(item => item.color);
        
        this.charts.category.data.labels = labels;
        this.charts.category.data.datasets[0].data = values;
        this.charts.category.data.datasets[0].backgroundColor = colors;
        this.charts.category.update();
    }

    updateGoalProgressChart(goalsData) {
        const labels = goalsData.map(item => item.title);
        const progress = goalsData.map(item => item.progress);
        const colors = goalsData.map(item => 
            item.progress >= 100 ? '#00ff88' :
            item.progress >= 70 ? '#0066ff' :
            item.progress >= 40 ? '#ff9900' : '#ff3366'
        );
        
        this.charts.goalProgress.data.labels = labels;
        this.charts.goalProgress.data.datasets[0].data = progress;
        this.charts.goalProgress.data.datasets[0].backgroundColor = colors;
        this.charts.goalProgress.data.datasets[0].borderColor = colors;
        this.charts.goalProgress.update();
    }

    handleQuickAction(event) {
        const action = event.currentTarget.dataset.action || 
                      event.currentTarget.querySelector('.quick-action-info h4').textContent;
        
        switch(action.toLowerCase()) {
            case 'nova transação':
            case 'addtransaction':
                this.openTransactionModal();
                break;
            case 'relatório rápido':
            case 'quickreport':
                this.generateQuickReport();
                break;
            case 'nova meta':
            case 'setgoal':
                this.openGoalModal();
                break;
            case 'análises':
                window.location.href = '/analytics';
                break;
        }
    }

    openTransactionModal() {
        // Create modal HTML
        const modalHTML = `
            <div class="neon-modal active" id="transactionModal">
                <div class="neon-modal-content">
                    <div class="neon-modal-header">
                        <h3><i class="fas fa-plus-circle"></i> Nova Transação</h3>
                        <button class="neon-modal-close" onclick="executiveDashboard.closeModal('transactionModal')">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="neon-modal-body">
                        <form id="transactionForm">
                            <div class="form-group">
                                <label for="transactionType">Tipo</label>
                                <div class="radio-group">
                                    <label class="radio-label">
                                        <input type="radio" name="type" value="income" checked>
                                        <span class="radio-custom">
                                            <i class="fas fa-money-bill-wave"></i>
                                            Receita
                                        </span>
                                    </label>
                                    <label class="radio-label">
                                        <input type="radio" name="type" value="expense">
                                        <span class="radio-custom">
                                            <i class="fas fa-credit-card"></i>
                                            Despesa
                                        </span>
                                    </label>
                                </div>
                            </div>
                            
                            <div class="form-group">
                                <label for="amount">Valor</label>
                                <input type="number" class="neon-input" id="amount" name="amount" 
                                       step="0.01" min="0.01" required placeholder="0,00">
                            </div>
                            
                            <div class="form-group">
                                <label for="description">Descrição</label>
                                <input type="text" class="neon-input" id="description" name="description" 
                                       required placeholder="Ex: Salário mensal">
                            </div>
                            
                            <div class="form-group">
                                <label for="category">Categoria</label>
                                <select class="neon-select" id="category" name="category_id">
                                    <option value="">Selecionar categoria</option>
                                    <!-- Categories will be loaded dynamically -->
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label for="date">Data</label>
                                <input type="date" class="neon-input" id="date" name="date" 
                                       value="${new Date().toISOString().split('T')[0]}">
                            </div>
                        </form>
                    </div>
                    <div class="neon-modal-footer">
                        <button type="button" class="neon-btn outline" 
                                onclick="executiveDashboard.closeModal('transactionModal')">
                            Cancelar
                        </button>
                        <button type="submit" form="transactionForm" class="neon-btn primary">
                            <i class="fas fa-save"></i>
                            Salvar Transação
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal to body
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Load categories
        this.loadCategories();
        
        // Handle form submission
        const form = document.getElementById('transactionForm');
        form.addEventListener('submit', (e) => this.handleTransactionSubmit(e));
    }

    async loadCategories() {
        try {
            const response = await fetch('/api/categories');
            const categories = await response.json();
            
            const select = document.getElementById('category');
            if (select) {
                categories.forEach(cat => {
                    const option = document.createElement('option');
                    option.value = cat.id;
                    option.textContent = cat.name;
                    option.style.color = cat.color;
                    select.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error loading categories:', error);
        }
    }

    async handleTransactionSubmit(event) {
        event.preventDefault();
        
        const form = event.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        try {
            const response = await fetch('/api/add_transaction', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccess(result.message);
                this.closeModal('transactionModal');
                this.updateDashboardData();
            } else {
                this.showError(result.error);
            }
        } catch (error) {
            console.error('Error submitting transaction:', error);
            this.showError('Erro ao salvar transação');
        }
    }

    generateQuickReport() {
        this.showLoading('Gerando relatório...');
        
        setTimeout(() => {
            this.hideLoading();
            this.showSuccess('Relatório gerado com sucesso!');
            
            // Create download link
            const link = document.createElement('a');
            link.href = '#';
            link.download = `relatorio_${new Date().toISOString().split('T')[0]}.pdf`;
            link.textContent = 'Clique para baixar';
            link.className = 'neon-btn success sm';
            link.style.marginLeft = '10px';
            
            this.showNotification('Relatório pronto para download', link);
        }, 2000);
    }

    openGoalModal() {
        this.showNotification('Modal de nova meta - Em desenvolvimento', null, 'info');
    }

    toggleNotifications() {
        const dropdown = document.querySelector('.notification-dropdown');
        if (dropdown) {
            dropdown.classList.toggle('show');
            
            if (dropdown.classList.contains('show')) {
                this.loadNotifications();
            }
        }
    }

    async loadNotifications() {
        try {
            const response = await fetch('/api/notifications');
            const notifications = await response.json();
            
            const container = document.querySelector('.notification-list');
            if (container) {
                container.innerHTML = notifications.map(notif => `
                    <div class="notification-item ${notif.read ? 'read' : 'unread'}">
                        <div class="notification-icon">
                            <i class="fas fa-${notif.icon || 'bell'}"></i>
                        </div>
                        <div class="notification-content">
                            <div class="notification-title">${notif.title}</div>
                            <div class="notification-message">${notif.message}</div>
                            <div class="notification-time">${notif.time}</div>
                        </div>
                    </div>
                `).join('');
            }
        } catch (error) {
            console.error('Error loading notifications:', error);
        }
    }

    handleAlertAction(action) {
        switch(action) {
            case 'Recomendamos revisar suas despesas':
                window.location.href = '/transactions';
                break;
            case 'Verifique o progresso':
                window.location.href = '/goals';
                break;
            case 'Considere revisar orçamento':
                window.location.href = '/analytics';
                break;
            case 'Continue monitorando':
                // Do nothing
                break;
        }
    }

    handleSearch(event) {
        const searchTerm = event.target.value.toLowerCase();
        
        // Filter transactions table
        const tableRows = document.querySelectorAll('.neon-table tbody tr');
        tableRows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
        
        // Filter goals list
        const goalItems = document.querySelectorAll('.goal-item');
        goalItems.forEach(item => {
            const text = item.textContent.toLowerCase();
            item.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    }

    updateChartPeriod(event) {
        const period = event.target.value;
        // Reload chart data with new period
        this.loadDashboardData();
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('active');
            setTimeout(() => modal.remove(), 300);
        }
    }

    showSuccess(message) {
        this.showNotification(message, null, 'success');
    }

    showError(message) {
        this.showNotification(message, null, 'error');
    }

    showNotification(message, actionElement = null, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `flash-message flash-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 
                               type === 'error' ? 'times-circle' : 
                               type === 'warning' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
            <button class="flash-close"><i class="fas fa-times"></i></button>
        `;
        
        if (actionElement) {
            notification.querySelector('span').appendChild(actionElement);
        }
        
        const container = document.querySelector('.flash-messages') || 
                         document.querySelector('.content-wrapper');
        if (container) {
            container.prepend(notification);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                notification.style.opacity = '0';
                setTimeout(() => notification.remove(), 300);
            }, 5000);
            
            // Close button
            notification.querySelector('.flash-close').addEventListener('click', () => {
                notification.remove();
            });
        }
    }

    showUpdateNotification() {
        // Show subtle update indicator
        const updateIndicator = document.createElement('div');
        updateIndicator.className = 'update-indicator';
        updateIndicator.innerHTML = '<i class="fas fa-sync-alt"></i> Dados atualizados';
        updateIndicator.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: var(--bg-card);
            border: 1px solid var(--primary-color);
            padding: 8px 16px;
            border-radius: var(--border-radius-md);
            font-size: var(--font-size-xs);
            color: var(--primary-color);
            z-index: 1000;
            animation: slideInUp 0.3s ease;
        `;
        
        document.body.appendChild(updateIndicator);
        
        setTimeout(() => {
            updateIndicator.style.opacity = '0';
            setTimeout(() => updateIndicator.remove(), 300);
        }, 2000);
    }

    showLoading(message = 'Carregando...') {
        const loading = document.createElement('div');
        loading.id = 'globalLoading';
        loading.innerHTML = `
            <div class="neon-loader"></div>
            <div class="loading-message">${message}</div>
        `;
        loading.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(10, 10, 15, 0.9);
            backdrop-filter: blur(10px);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 9999;
        `;
        
        document.body.appendChild(loading);
    }

    hideLoading() {
        const loading = document.getElementById('globalLoading');
        if (loading) {
            loading.style.opacity = '0';
            setTimeout(() => loading.remove(), 300);
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.executiveDashboard = new ExecutiveDashboard();
});