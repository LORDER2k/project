/**
 * ContaSmart Pro Executive Actions
 * Sistema de ações rápidas e interações
 */

class ExecutiveActions {
    constructor() {
        this.modals = new Map();
        this.notifications = [];
        this.shortcuts = new Map();
        this.init();
    }

    init() {
        this.setupKeyboardShortcuts();
        this.setupDragAndDrop();
        this.setupContextMenus();
        this.setupTooltips();
        this.setupNotifications();
        this.setupAutoSave();
    }

    setupKeyboardShortcuts() {
        // Shortcuts globais
        this.registerShortcut('ctrl+s', 'Salvar', (e) => {
            e.preventDefault();
            this.saveCurrentForm();
        });

        this.registerShortcut('ctrl+n', 'Nova Transação', (e) => {
            e.preventDefault();
            this.openQuickTransaction();
        });

        this.registerShortcut('ctrl+g', 'Nova Meta', (e) => {
            e.preventDefault();
            this.openQuickGoal();
        });

        this.registerShortcut('ctrl+r', 'Relatório', (e) => {
            e.preventDefault();
            this.generateQuickReport();
        });

        this.registerShortcut('ctrl+f', 'Buscar', (e) => {
            e.preventDefault();
            this.focusSearch();
        });

        this.registerShortcut('ctrl+d', 'Dashboard', (e) => {
            e.preventDefault();
            window.location.href = '/dashboard';
        });

        this.registerShortcut('ctrl+a', 'Análises', (e) => {
            e.preventDefault();
            window.location.href = '/analytics';
        });

        this.registerShortcut('ctrl+m', 'Metas', (e) => {
            e.preventDefault();
            window.location.href = '/goals';
        });

        this.registerShortcut('ctrl+i', 'IA Financeira', (e) => {
            e.preventDefault();
            window.location.href = '/ai_financeira';
        });

        this.registerShortcut('ctrl+p', 'Perfil', (e) => {
            e.preventDefault();
            window.location.href = '/profile';
        });

        // Tecla ESC para fejar modais
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
                this.hideAllTooltips();
            }
        });

        // Mostrar help modal com F1
        document.addEventListener('keydown', (e) => {
            if (e.key === 'F1') {
                e.preventDefault();
                this.showKeyboardShortcuts();
            }
        });
    }

    registerShortcut(keys, description, callback) {
        this.shortcuts.set(keys, { description, callback });
        
        document.addEventListener('keydown', (e) => {
            const key = e.key.toLowerCase();
            const ctrl = e.ctrlKey || e.metaKey;
            const shift = e.shiftKey;
            const alt = e.altKey;
            
            const shortcutKey = `${ctrl ? 'ctrl+' : ''}${shift ? 'shift+' : ''}${alt ? 'alt+' : ''}${key}`;
            
            if (this.shortcuts.has(shortcutKey)) {
                this.shortcuts.get(shortcutKey).callback(e);
            }
        });
    }

    setupDragAndDrop() {
        // Drag and drop para transações
        const transactionRows = document.querySelectorAll('.transaction-row[draggable]');
        transactionRows.forEach(row => {
            row.setAttribute('draggable', 'true');
            
            row.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('text/plain', row.dataset.id);
                row.classList.add('dragging');
            });
            
            row.addEventListener('dragend', () => {
                row.classList.remove('dragging');
            });
        });

        // Áreas de drop para categorias
        const categoryAreas = document.querySelectorAll('.category-drop-area');
        categoryAreas.forEach(area => {
            area.addEventListener('dragover', (e) => {
                e.preventDefault();
                area.classList.add('drag-over');
            });
            
            area.addEventListener('dragleave', () => {
                area.classList.remove('drag-over');
            });
            
            area.addEventListener('drop', (e) => {
                e.preventDefault();
                area.classList.remove('drag-over');
                
                const transactionId = e.dataTransfer.getData('text/plain');
                const categoryId = area.dataset.categoryId;
                
                this.assignCategoryToTransaction(transactionId, categoryId);
            });
        });
    }

    setupContextMenus() {
        // Context menu para transações
        document.addEventListener('contextmenu', (e) => {
            const transactionRow = e.target.closest('.transaction-row');
            if (transactionRow) {
                e.preventDefault();
                this.showTransactionContextMenu(e, transactionRow);
            }
            
            const goalItem = e.target.closest('.goal-item');
            if (goalItem) {
                e.preventDefault();
                this.showGoalContextMenu(e, goalItem);
            }
        });

        // Fechar context menu ao clicar
        document.addEventListener('click', () => {
            this.hideContextMenus();
        });
    }

    showTransactionContextMenu(e, row) {
        this.hideContextMenus();
        
        const menu = document.createElement('div');
        menu.className = 'context-menu';
        menu.style.cssText = `
            position: fixed;
            left: ${e.pageX}px;
            top: ${e.pageY}px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius-md);
            box-shadow: var(--elevation-3);
            z-index: 10000;
            min-width: 200px;
        `;
        
        const transactionId = row.dataset.id;
        
        menu.innerHTML = `
            <div class="context-menu-header">
                <span>Ações da Transação</span>
            </div>
            <div class="context-menu-items">
                <a href="#" class="context-menu-item" data-action="edit">
                    <i class="fas fa-edit"></i>
                    <span>Editar</span>
                </a>
                <a href="#" class="context-menu-item" data-action="duplicate">
                    <i class="fas fa-copy"></i>
                    <span>Duplicar</span>
                </a>
                <a href="#" class="context-menu-item" data-action="categorize">
                    <i class="fas fa-tag"></i>
                    <span>Categorizar</span>
                </a>
                <div class="context-menu-divider"></div>
                <a href="#" class="context-menu-item text-danger" data-action="delete">
                    <i class="fas fa-trash"></i>
                    <span>Excluir</span>
                </a>
            </div>
        `;
        
        document.body.appendChild(menu);
        
        // Event handlers
        menu.querySelectorAll('.context-menu-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const action = item.dataset.action;
                this.handleTransactionAction(transactionId, action);
                menu.remove();
            });
        });
    }

    showGoalContextMenu(e, item) {
        this.hideContextMenus();
        
        const menu = document.createElement('div');
        menu.className = 'context-menu';
        menu.style.cssText = `
            position: fixed;
            left: ${e.pageX}px;
            top: ${e.pageY}px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius-md);
            box-shadow: var(--elevation-3);
            z-index: 10000;
            min-width: 200px;
        `;
        
        const goalId = item.dataset.id;
        
        menu.innerHTML = `
            <div class="context-menu-header">
                <span>Ações da Meta</span>
            </div>
            <div class="context-menu-items">
                <a href="#" class="context-menu-item" data-action="edit-goal">
                    <i class="fas fa-edit"></i>
                    <span>Editar</span>
                </a>
                <a href="#" class="context-menu-item" data-action="add-progress">
                    <i class="fas fa-plus-circle"></i>
                    <span>Adicionar Progresso</span>
                </a>
                <a href="#" class="context-menu-item" data-action="mark-complete">
                    <i class="fas fa-check-circle"></i>
                    <span>Marcar como Concluída</span>
                </a>
                <div class="context-menu-divider"></div>
                <a href="#" class="context-menu-item text-danger" data-action="delete-goal">
                    <i class="fas fa-trash"></i>
                    <span>Excluir</span>
                </a>
            </div>
        `;
        
        document.body.appendChild(menu);
        
        // Event handlers
        menu.querySelectorAll('.context-menu-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const action = item.dataset.action;
                this.handleGoalAction(goalId, action);
                menu.remove();
            });
        });
    }

    hideContextMenus() {
        document.querySelectorAll('.context-menu').forEach(menu => menu.remove());
    }

    setupTooltips() {
        // Tooltips para elementos com data-tooltip
        document.querySelectorAll('[data-tooltip]').forEach(element => {
            element.addEventListener('mouseenter', (e) => {
                this.showTooltip(e.target, e.target.dataset.tooltip);
            });
            
            element.addEventListener('mouseleave', () => {
                this.hideTooltip();
            });
        });

        // Tooltips dinâmicos para valores monetários
        document.addEventListener('mouseover', (e) => {
            if (e.target.classList.contains('monetary-value')) {
                const value = parseFloat(e.target.textContent.replace(/[^\d.,]/g, '').replace(',', '.'));
                if (!isNaN(value)) {
                    const tooltipText = this.formatMonetaryTooltip(value);
                    this.showTooltip(e.target, tooltipText);
                }
            }
        });
    }

    showTooltip(element, text) {
        this.hideTooltip();
        
        const tooltip = document.createElement('div');
        tooltip.className = 'executive-tooltip';
        tooltip.textContent = text;
        
        document.body.appendChild(tooltip);
        
        // Posicionar tooltip
        const rect = element.getBoundingClientRect();
        tooltip.style.left = `${rect.left + rect.width / 2 - tooltip.offsetWidth / 2}px`;
        tooltip.style.top = `${rect.top - tooltip.offsetHeight - 10}px`;
    }

    hideTooltip() {
        const tooltip = document.querySelector('.executive-tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }

    hideAllTooltips() {
        document.querySelectorAll('.executive-tooltip').forEach(tooltip => tooltip.remove());
    }

    formatMonetaryTooltip(value) {
        const formatter = new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        });
        
        const formatted = formatter.format(value);
        
        // Adicionar informações extras
        const info = [];
        
        if (value > 10000) info.push('Valor alto');
        if (value < 0) info.push('Valor negativo');
        if (Math.abs(value) < 50) info.push('Valor baixo');
        
        return info.length > 0 ? 
            `${formatted} (${info.join(', ')})` : 
            formatted;
    }

    setupNotifications() {
        // Verificar novas notificações periodicamente
        setInterval(() => this.checkNewNotifications(), 60000);
        
        // Notificação de boas-vindas
        setTimeout(() => {
            this.showNotification({
                title: 'Bem-vindo ao Sistema Executivo',
                message: 'Seu dashboard está pronto para uso. Use Ctrl+N para nova transação.',
                type: 'info',
                duration: 5000
            });
        }, 1000);
    }

    async checkNewNotifications() {
        try {
            const response = await fetch('/api/notifications/unread');
            const notifications = await response.json();
            
            notifications.forEach(notification => {
                if (!this.notifications.includes(notification.id)) {
                    this.showNotification(notification);
                    this.notifications.push(notification.id);
                }
            });
        } catch (error) {
            console.error('Error checking notifications:', error);
        }
    }

    showNotification(notification) {
        const notificationElement = document.createElement('div');
        notificationElement.className = `executive-notification notification-${notification.type}`;
        
        notificationElement.innerHTML = `
            <div class="notification-icon">
                <i class="fas fa-${this.getNotificationIcon(notification.type)}"></i>
            </div>
            <div class="notification-content">
                <div class="notification-title">${notification.title}</div>
                <div class="notification-message">${notification.message}</div>
            </div>
            <button class="notification-close">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        const container = document.querySelector('.notification-container');
        if (!container) {
            const newContainer = document.createElement('div');
            newContainer.className = 'notification-container';
            newContainer.style.cssText = `
                position: fixed;
                top: 80px;
                right: 20px;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                gap: 10px;
            `;
            document.body.appendChild(newContainer);
            container = newContainer;
        }
        
        container.appendChild(notificationElement);
        
        // Animar entrada
        notificationElement.style.transform = 'translateX(100%)';
        notificationElement.style.opacity = '0';
        
        setTimeout(() => {
            notificationElement.style.transform = 'translateX(0)';
            notificationElement.style.opacity = '1';
        }, 10);
        
        // Auto-remover após duração
        const duration = notification.duration || 5000;
        setTimeout(() => {
            this.removeNotification(notificationElement);
        }, duration);
        
        // Botão de fechar
        notificationElement.querySelector('.notification-close').addEventListener('click', () => {
            this.removeNotification(notificationElement);
        });
        
        // Click para ação
        if (notification.action) {
            notificationElement.style.cursor = 'pointer';
            notificationElement.addEventListener('click', () => {
                if (notification.action.url) {
                    window.location.href = notification.action.url;
                } else if (notification.action.callback) {
                    eval(notification.action.callback);
                }
                this.removeNotification(notificationElement);
            });
        }
    }

    removeNotification(element) {
        element.style.transform = 'translateX(100%)';
        element.style.opacity = '0';
        setTimeout(() => element.remove(), 300);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'bell';
    }

    setupAutoSave() {
        // Auto-save para formulários
        document.querySelectorAll('form[data-autosave]').forEach(form => {
            let timeout;
            
            form.addEventListener('input', () => {
                clearTimeout(timeout);
                timeout = setTimeout(() => {
                    this.autoSaveForm(form);
                }, 1000);
            });
            
            form.addEventListener('submit', (e) => {
                clearTimeout(timeout);
            });
        });
        
        // Auto-save ao sair da página
        window.addEventListener('beforeunload', (e) => {
            const hasUnsavedChanges = document.querySelectorAll('form[data-unsaved]').length > 0;
            if (hasUnsavedChanges) {
                e.preventDefault();
                e.returnValue = 'Você tem alterações não salvas. Deseja realmente sair?';
                return e.returnValue;
            }
        });
    }

    async autoSaveForm(form) {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        try {
            const response = await fetch(form.dataset.autosaveUrl || form.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                this.showAutoSaveIndicator(form, true);
            } else {
                this.showAutoSaveIndicator(form, false);
            }
        } catch (error) {
            console.error('Auto-save error:', error);
            this.showAutoSaveIndicator(form, false);
        }
    }

    showAutoSaveIndicator(form, success) {
        let indicator = form.querySelector('.autosave-indicator');
        
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.className = 'autosave-indicator';
            form.appendChild(indicator);
        }
        
        indicator.innerHTML = success ? 
            '<i class="fas fa-check"></i> Salvo automaticamente' :
            '<i class="fas fa-exclamation-triangle"></i> Erro ao salvar';
        
        indicator.style.opacity = '1';
        
        setTimeout(() => {
            indicator.style.opacity = '0';
        }, 2000);
    }

    // Métodos de ação
    openQuickTransaction() {
        // Criar modal rápido de transação
        const modal = this.createQuickModal('transaction', {
            title: 'Nova Transação Rápida',
            fields: [
                {
                    type: 'select',
                    name: 'type',
                    label: 'Tipo',
                    options: [
                        { value: 'income', label: 'Receita' },
                        { value: 'expense', label: 'Despesa' }
                    ],
                    required: true
                },
                {
                    type: 'number',
                    name: 'amount',
                    label: 'Valor',
                    placeholder: '0,00',
                    required: true,
                    step: '0.01'
                },
                {
                    type: 'text',
                    name: 'description',
                    label: 'Descrição',
                    placeholder: 'Descrição da transação',
                    required: true
                }
            ],
            onSubmit: (data) => this.submitQuickTransaction(data)
        });
        
        this.showModal(modal);
    }

    openQuickGoal() {
        const modal = this.createQuickModal('goal', {
            title: 'Nova Meta Rápida',
            fields: [
                {
                    type: 'text',
                    name: 'title',
                    label: 'Título',
                    placeholder: 'Nome da meta',
                    required: true
                },
                {
                    type: 'number',
                    name: 'target_amount',
                    label: 'Valor Alvo',
                    placeholder: '0,00',
                    required: true,
                    step: '0.01'
                },
                {
                    type: 'date',
                    name: 'deadline',
                    label: 'Prazo',
                    required: true
                }
            ],
            onSubmit: (data) => this.submitQuickGoal(data)
        });
        
        this.showModal(modal);
    }

    createQuickModal(type, config) {
        const modalId = `quick-${type}-modal`;
        
        const modalHTML = `
            <div class="quick-modal" id="${modalId}">
                <div class="quick-modal-backdrop"></div>
                <div class="quick-modal-content">
                    <div class="quick-modal-header">
                        <h3>${config.title}</h3>
                        <button class="quick-modal-close">&times;</button>
                    </div>
                    <div class="quick-modal-body">
                        <form id="${modalId}-form">
                            ${config.fields.map(field => `
                                <div class="form-group">
                                    <label for="${field.name}">${field.label}</label>
                                    ${this.renderFormField(field)}
                                </div>
                            `).join('')}
                        </form>
                    </div>
                    <div class="quick-modal-footer">
                        <button type="button" class="neon-btn outline quick-modal-cancel">
                            Cancelar
                        </button>
                        <button type="submit" form="${modalId}-form" class="neon-btn primary">
                            <i class="fas fa-save"></i>
                            Salvar
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        const modal = document.createElement('div');
        modal.innerHTML = modalHTML;
        
        // Configurar eventos
        const form = modal.querySelector('form');
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            config.onSubmit(data);
            this.closeModal(modalId);
        });
        
        modal.querySelector('.quick-modal-close').addEventListener('click', () => {
            this.closeModal(modalId);
        });
        
        modal.querySelector('.quick-modal-cancel').addEventListener('click', () => {
            this.closeModal(modalId);
        });
        
        return { id: modalId, element: modal };
    }

    renderFormField(field) {
        switch(field.type) {
            case 'select':
                return `
                    <select class="neon-select" name="${field.name}" ${field.required ? 'required' : ''}>
                        ${field.options.map(opt => `
                            <option value="${opt.value}">${opt.label}</option>
                        `).join('')}
                    </select>
                `;
            case 'textarea':
                return `
                    <textarea class="neon-input" name="${field.name}" 
                              placeholder="${field.placeholder || ''}"
                              ${field.required ? 'required' : ''}
                              rows="3"></textarea>
                `;
            default:
                return `
                    <input type="${field.type}" 
                           class="neon-input" 
                           name="${field.name}" 
                           placeholder="${field.placeholder || ''}"
                           ${field.required ? 'required' : ''}
                           ${field.step ? `step="${field.step}"` : ''}>
                `;
        }
    }

    showModal(modal) {
        this.modals.set(modal.id, modal);
        document.body.appendChild(modal.element);
        
        // Animar entrada
        setTimeout(() => {
            modal.element.classList.add('active');
        }, 10);
    }

    closeModal(modalId) {
        const modal = this.modals.get(modalId);
        if (modal) {
            modal.element.classList.remove('active');
            setTimeout(() => {
                modal.element.remove();
                this.modals.delete(modalId);
            }, 300);
        }
    }

    closeAllModals() {
        this.modals.forEach(modal => {
            modal.element.classList.remove('active');
            setTimeout(() => modal.element.remove(), 300);
        });
        this.modals.clear();
    }

    async submitQuickTransaction(data) {
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
                this.showNotification({
                    title: 'Sucesso',
                    message: 'Transação adicionada com sucesso!',
                    type: 'success'
                });
                
                // Atualizar dashboard se estiver visível
                if (window.executiveDashboard) {
                    window.executiveDashboard.updateDashboardData();
                }
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            this.showNotification({
                title: 'Erro',
                message: 'Falha ao adicionar transação: ' + error.message,
                type: 'error'
            });
        }
    }

    async submitQuickGoal(data) {
        try {
            const response = await fetch('/api/add_goal', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification({
                    title: 'Sucesso',
                    message: 'Meta criada com sucesso!',
                    type: 'success'
                });
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            this.showNotification({
                title: 'Erro',
                message: 'Falha ao criar meta: ' + error.message,
                type: 'error'
            });
        }
    }

    async assignCategoryToTransaction(transactionId, categoryId) {
        try {
            const response = await fetch(`/api/transaction/${transactionId}/category`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ category_id: categoryId })
            });
            
            if (response.ok) {
                this.showNotification({
                    title: 'Sucesso',
                    message: 'Transação categorizada!',
                    type: 'success'
                });
            }
        } catch (error) {
            console.error('Error assigning category:', error);
        }
    }

    handleTransactionAction(transactionId, action) {
        switch(action) {
            case 'edit':
                this.editTransaction(transactionId);
                break;
            case 'duplicate':
                this.duplicateTransaction(transactionId);
                break;
            case 'categorize':
                this.showCategorySelector(transactionId);
                break;
            case 'delete':
                this.deleteTransaction(transactionId);
                break;
        }
    }

    handleGoalAction(goalId, action) {
        switch(action) {
            case 'edit-goal':
                this.editGoal(goalId);
                break;
            case 'add-progress':
                this.addGoalProgress(goalId);
                break;
            case 'mark-complete':
                this.markGoalComplete(goalId);
                break;
            case 'delete-goal':
                this.deleteGoal(goalId);
                break;
        }
    }

    async deleteTransaction(transactionId) {
        if (!confirm('Tem certeza que deseja excluir esta transação?')) return;
        
        try {
            const response = await fetch(`/api/delete_transaction/${transactionId}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification({
                    title: 'Sucesso',
                    message: 'Transação excluída!',
                    type: 'success'
                });
                
                // Remover da interface
                const row = document.querySelector(`[data-id="${transactionId}"]`);
                if (row) {
                    row.style.opacity = '0';
                    setTimeout(() => row.remove(), 300);
                }
            }
        } catch (error) {
            this.showNotification({
                title: 'Erro',
                message: 'Falha ao excluir transação',
                type: 'error'
            });
        }
    }

    async deleteGoal(goalId) {
        if (!confirm('Tem certeza que deseja excluir esta meta?')) return;
        
        try {
            const response = await fetch(`/api/delete_goal/${goalId}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification({
                    title: 'Sucesso',
                    message: 'Meta excluída!',
                    type: 'success'
                });
            }
        } catch (error) {
            this.showNotification({
                title: 'Erro',
                message: 'Falha ao excluir meta',
                type: 'error'
            });
        }
    }

    generateQuickReport() {
        this.showNotification({
            title: 'Gerando Relatório',
            message: 'O relatório está sendo preparado...',
            type: 'info'
        });
        
        // Simular geração de relatório
        setTimeout(() => {
            this.showNotification({
                title: 'Relatório Pronto',
                message: 'Clique para baixar o relatório',
                type: 'success',
                action: {
                    url: '#',
                    callback: 'alert("Download iniciado!")'
                }
            });
        }, 2000);
    }

    focusSearch() {
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }

    saveCurrentForm() {
        const activeForm = document.querySelector('form:focus-within');
        if (activeForm) {
            activeForm.dispatchEvent(new Event('submit'));
        } else {
            this.showNotification({
                title: 'Nenhum formulário ativo',
                message: 'Foque em um campo de formulário para salvar',
                type: 'warning'
            });
        }
    }

    showKeyboardShortcuts() {
        const shortcuts = Array.from(this.shortcuts.entries())
            .map(([keys, data]) => `<tr><td><kbd>${keys}</kbd></td><td>${data.description}</td></tr>`)
            .join('');
        
        const modal = this.createQuickModal('shortcuts', {
            title: 'Atalhos de Teclado',
            fields: [],
            onSubmit: () => {}
        });
        
        // Substituir conteúdo do modal
        const modalBody = modal.element.querySelector('.quick-modal-body');
        modalBody.innerHTML = `
            <div class="shortcuts-table">
                <table>
                    <thead>
                        <tr>
                            <th>Atalho</th>
                            <th>Ação</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${shortcuts}
                    </tbody>
                </table>
            </div>
            <div class="shortcuts-help">
                <p><i class="fas fa-info-circle"></i> Pressione F1 para abrir este painel a qualquer momento</p>
            </div>
        `;
        
        this.showModal(modal);
    }

    // Métodos utilitários
    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showNotification({
                title: 'Copiado!',
                message: 'Texto copiado para a área de transferência',
                type: 'success',
                duration: 2000
            });
        }).catch(err => {
            console.error('Falha ao copiar: ', err);
        });
    }

    shareContent(title, text, url) {
        if (navigator.share) {
            navigator.share({
                title: title,
                text: text,
                url: url
            });
        } else {
            this.copyToClipboard(url);
        }
    }

    takeScreenshot(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            html2canvas(element).then(canvas => {
                const link = document.createElement('a');
                link.download = `screenshot-${new Date().getTime()}.png`;
                link.href = canvas.toDataURL();
                link.click();
            });
        }
    }

    // Método para iniciar tour guiado
    startGuidedTour() {
        this.showNotification({
            title: 'Tour Iniciado',
            message: 'Siga as instruções para conhecer o sistema',
            type: 'info'
        });
        
        // Implementar lógica do tour
        // Pode usar bibliotecas como Shepherd.js
    }
}

// Inicializar ações
document.addEventListener('DOMContentLoaded', () => {
    window.executiveActions = new ExecutiveActions();
    
    // Adicionar estilos para componentes dinâmicos
    const style = document.createElement('style');
    style.textContent = `
        .context-menu {
            animation: slideInDown 0.2s ease;
        }
        
        .context-menu-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 15px;
            color: var(--text-primary);
            text-decoration: none;
            transition: background-color 0.2s;
        }
        
        .context-menu-item:hover {
            background: var(--bg-tertiary);
        }
        
        .context-menu-divider {
            height: 1px;
            background: var(--border-color);
            margin: 5px 0;
        }
        
        .executive-tooltip {
            position: fixed;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            padding: 8px 12px;
            border-radius: var(--border-radius-md);
            font-size: var(--font-size-sm);
            color: var(--text-primary);
            z-index: 9999;
            pointer-events: none;
            animation: fadeIn 0.2s ease;
            box-shadow: var(--elevation-2);
            max-width: 300px;
        }
        
        .executive-notification {
            display: flex;
            align-items: flex-start;
            gap: 12px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius-md);
            padding: 15px;
            width: 350px;
            animation: slideInRight 0.3s ease;
            transition: all 0.3s ease;
        }
        
        .notification-success {
            border-left: 4px solid var(--success-color);
        }
        
        .notification-error {
            border-left: 4px solid var(--danger-color);
        }
        
        .notification-warning {
            border-left: 4px solid var(--warning-color);
        }
        
        .notification-info {
            border-left: 4px solid var(--info-color);
        }
        
        .quick-modal {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
        }
        
        .quick-modal.active {
            opacity: 1;
            visibility: visible;
        }
        
        .quick-modal-backdrop {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(10, 10, 15, 0.9);
            backdrop-filter: blur(10px);
        }
        
        .quick-modal-content {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius-lg);
            width: 90%;
            max-width: 500px;
            position: relative;
            z-index: 1;
            transform: translateY(-20px);
            transition: transform 0.3s ease;
        }
        
        .quick-modal.active .quick-modal-content {
            transform: translateY(0);
        }
        
        .autosave-indicator {
            position: absolute;
            bottom: 10px;
            right: 10px;
            font-size: var(--font-size-xs);
            color: var(--text-muted);
            opacity: 0;
            transition: opacity 0.3s;
        }
    `;
    
    document.head.appendChild(style);
});

// Funções globais de conveniência
function showQuickTransaction() {
    if (window.executiveActions) {
        window.executiveActions.openQuickTransaction();
    }
}

function showQuickGoal() {
    if (window.executiveActions) {
        window.executiveActions.openQuickGoal();
    }
}

function copyTextToClipboard(text) {
    if (window.executiveActions) {
        window.executiveActions.copyToClipboard(text);
    }
}