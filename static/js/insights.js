// Insights.js - Script para insights financeiros

let insightsData = {};

// Inicializar insights
function initInsights() {
    loadInsightsData();
    setupInsightsInteractions();
    setupInsightsRefresh();
}

// Carregar dados de insights
function loadInsightsData() {
    fetch('/api/insights-detailed')
        .then(response => response.json())
        .then(data => {
            insightsData = data;
            updateInsightsUI(data);
        });
}

// Atualizar UI de insights
function updateInsightsUI(data) {
    // Atualizar economia
    const economyElement = document.querySelector('.economy-value');
    if (economyElement && data.economia) {
        economyElement.textContent = `R$ ${data.economia.valor.toFixed(2)}`;
        
        const progressBar = document.querySelector('.economy-progress .progress-bar');
        if (progressBar) {
            progressBar.style.width = `${data.economia.percentual}%`;
        }
    }
    
    // Atualizar investimentos
    if (data.investimento) {
        const riskBadge = document.querySelector('.investment-badges .badge.bg-warning, .investment-badges .badge.bg-danger');
        if (riskBadge) {
            riskBadge.textContent = `Risco ${data.investimento.risco}`;
            riskBadge.className = `badge bg-${getRiskColor(data.investimento.risco)}`;
        }
    }
}

// Configurar interações
function setupInsightsInteractions() {
    // Botões de ação
    document.querySelectorAll('.recommendation-card .btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const action = this.closest('.recommendation-card').querySelector('h6').textContent;
            handleRecommendationAction(action);
        });
    });
    
    // Botão de refresh
    const refreshBtn = document.querySelector('[onclick="refreshInsights()"]');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshInsights);
    }
    
    // FAQ accordion
    const faqItems = document.querySelectorAll('.accordion-button');
    faqItems.forEach(item => {
        item.addEventListener('click', function() {
            this.classList.toggle('collapsed');
        });
    });
}

// Atualizar insights
function refreshInsights() {
    showLoading('Atualizando insights...');
    
    fetch('/api/refresh-insights', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showToast('Insights atualizados com sucesso!', 'success');
            loadInsightsData();
        } else {
            showToast('Erro ao atualizar insights', 'danger');
        }
    });
}

// Mostrar planejador de orçamento
function showBudgetPlanner() {
    const modal = new bootstrap.Modal(document.getElementById('budgetPlannerModal'));
    
    // Carregar conteúdo do planejador
    fetch('/api/budget-planner')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('budget-planner-content');
            container.innerHTML = renderBudgetPlanner(data);
            modal.show();
        });
}

// Renderizar planejador de orçamento
function renderBudgetPlanner(data) {
    return `
        <div class="budget-planner">
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label class="form-label">Renda Mensal (R$)</label>
                        <input type="number" class="form-control" id="monthly-income" 
                               value="${data.renda_mensal || ''}" step="0.01">
                    </div>
                    
                    <h6 class="mt-4 mb-3">Despesas Fixas</h6>
                    ${renderExpenseCategories(data.fixas || [])}
                </div>
                
                <div class="col-md-6">
                    <h6 class="mb-3">Distribuição Sugerida</h6>
                    <div class="budget-distribution">
                        <div class="distribution-item">
                            <span>Despesas Essenciais</span>
                            <div class="progress mb-2">
                                <div class="progress-bar bg-success" style="width: 50%"></div>
                            </div>
                            <small class="text-muted">50% da renda</small>
                        </div>
                        
                        <div class="distribution-item">
                            <span>Estilo de Vida</span>
                            <div class="progress mb-2">
                                <div class="progress-bar bg-warning" style="width: 30%"></div>
                            </div>
                            <small class="text-muted">30% da renda</small>
                        </div>
                        
                        <div class="distribution-item">
                            <span>Investimentos</span>
                            <div class="progress mb-2">
                                <div class="progress-bar bg-primary" style="width: 20%"></div>
                            </div>
                            <small class="text-muted">20% da renda</small>
                        </div>
                    </div>
                    
                    <div class="mt-4">
                        <button class="btn btn-primary w-100" onclick="calculateBudget()">
                            <i class="fas fa-calculator me-2"></i>Calcular Orçamento
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Renderizar categorias de despesa
function renderExpenseCategories(categories) {
    if (!categories.length) {
        return '<p class="text-muted">Nenhuma categoria definida</p>';
    }
    
    let html = '';
    categories.forEach(cat => {
        html += `
            <div class="input-group mb-2">
                <span class="input-group-text">${cat.name}</span>
                <input type="number" class="form-control" value="${cat.value || ''}" 
                       placeholder="Valor mensal">
                <span class="input-group-text">%</span>
                <input type="number" class="form-control" value="${cat.percentage || ''}" 
                       placeholder="%" readonly>
            </div>
        `;
    });
    
    return html;
}

// Calcular orçamento
function calculateBudget() {
    const income = parseFloat(document.getElementById('monthly-income').value);
    
    if (!income || income <= 0) {
        showToast('Digite uma renda válida', 'warning');
        return;
    }
    
    const essentials = income * 0.5;
    const lifestyle = income * 0.3;
    const investments = income * 0.2;
    
    const result = `
        <div class="alert alert-success mt-3">
            <h6>📊 Resultado do Orçamento</h6>
            <p><strong>Renda:</strong> R$ ${income.toFixed(2)}</p>
            <p><strong>Despesas Essenciais:</strong> R$ ${essentials.toFixed(2)} (50%)</p>
            <p><strong>Estilo de Vida:</strong> R$ ${lifestyle.toFixed(2)} (30%)</p>
            <p><strong>Investimentos:</strong> R$ ${investments.toFixed(2)} (20%)</p>
        </div>
    `;
    
    document.querySelector('.budget-planner').insertAdjacentHTML('beforeend', result);
}

// Lidar com ação de recomendação
function handleRecommendationAction(action) {
    switch(action) {
        case 'Educação Financeira':
            window.open('https://www.investopedia.com/', '_blank');
            break;
        case 'Ferramentas Úteis':
            showCompoundInterestCalculator();
            break;
        case 'Análise Comparativa':
            showComparativeAnalysis();
            break;
        case 'Planejamento':
            downloadBudgetPlanner();
            break;
    }
}

// Mostrar calculadora de juros compostos
function showCompoundInterestCalculator() {
    const modalContent = `
        <div class="compound-calculator">
            <div class="mb-3">
                <label class="form-label">Valor Inicial (R$)</label>
                <input type="number" class="form-control" id="initial-amount" value="1000">
            </div>
            
            <div class="mb-3">
                <label class="form-label">Aporte Mensal (R$)</label>
                <input type="number" class="form-control" id="monthly-contribution" value="100">
            </div>
            
            <div class="mb-3">
                <label class="form-label">Taxa Anual (%)</label>
                <input type="number" class="form-control" id="annual-rate" value="12">
            </div>
            
            <div class="mb-3">
                <label class="form-label">Período (anos)</label>
                <input type="number" class="form-control" id="period-years" value="10">
            </div>
            
            <button class="btn btn-primary w-100" onclick="calculateCompoundInterest()">
                Calcular
            </button>
            
            <div id="calculation-result" class="mt-3"></div>
        </div>
    `;
    
    showModal('Calculadora de Juros Compostos', modalContent);
}

// Calcular juros compostos
function calculateCompoundInterest() {
    const initial = parseFloat(document.getElementById('initial-amount').value);
    const monthly = parseFloat(document.getElementById('monthly-contribution').value);
    const rate = parseFloat(document.getElementById('annual-rate').value) / 100;
    const years = parseFloat(document.getElementById('period-years').value);
    
    const monthlyRate = Math.pow(1 + rate, 1/12) - 1;
    const months = years * 12;
    
    // Fórmula de valor futuro com aportes mensais
    let futureValue = initial * Math.pow(1 + monthlyRate, months);
    futureValue += monthly * ((Math.pow(1 + monthlyRate, months) - 1) / monthlyRate);
    
    const totalInvested = initial + (monthly * months);
    const totalInterest = futureValue - totalInvested;
    
    const result = `
        <div class="alert alert-success">
            <h6>💰 Resultado da Projeção</h6>
            <p><strong>Valor Futuro:</strong> R$ ${futureValue.toFixed(2)}</p>
            <p><strong>Total Investido:</strong> R$ ${totalInvested.toFixed(2)}</p>
            <p><strong>Juros Acumulados:</strong> R$ ${totalInterest.toFixed(2)}</p>
            <p><strong>Retorno:</strong> ${((totalInterest / totalInvested) * 100).toFixed(2)}%</p>
        </div>
    `;
    
    document.getElementById('calculation-result').innerHTML = result;
}

// Mostrar análise comparativa
function showComparativeAnalysis() {
    fetch('/api/comparative-analysis')
        .then(response => response.json())
        .then(data => {
            const modalContent = `
                <div class="comparative-analysis">
                    <h6 class="mb-3">📊 Comparativo com Média da Sua Faixa</h6>
                    ${renderComparativeData(data)}
                </div>
            `;
            
            showModal('Análise Comparativa', modalContent);
        });
}

// Renderizar dados comparativos
function renderComparativeData(data) {
    return `
        <table class="table table-sm">
            <thead>
                <tr>
                    <th>Indicador</th>
                    <th>Você</th>
                    <th>Média</th>
                    <th>Diferença</th>
                </tr>
            </thead>
            <tbody>
                ${data.map(item => `
                    <tr>
                        <td>${item.indicator}</td>
                        <td>${item.your_value}</td>
                        <td>${item.average_value}</td>
                        <td class="${item.difference_class}">
                            ${item.difference}
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// Baixar planejador de orçamento
function downloadBudgetPlanner() {
    const content = `
        =================================
        PLANEJADOR DE ORÇAMENTO ANUAL
        =================================
        Data: ${new Date().toLocaleDateString('pt-BR')}
        
        INSTRUÇÕES:
        1. Preencha sua renda mensal
        2. Liste todas as despesas fixas
        3. Defina metas de economia
        4. Acompanhe mensalmente
        
        DISTRIBUIÇÃO SUGERIDA:
        - 50% Despesas Essenciais
        - 30% Estilo de Vida
        - 20% Investimentos/Poupança
        
        MÊS A MÊS:
        [ ] Janeiro
        [ ] Fevereiro
        [ ] Março
        [ ] Abril
        [ ] Maio
        [ ] Junho
        [ ] Julho
        [ ] Agosto
        [ ] Setembro
        [ ] Outubro
        [ ] Novembro
        [ ] Dezembro
        
        METAS ANUAIS:
        1. ________________________________
        2. ________________________________
        3. ________________________________
        
        ContaSmart Pro - Seu aliado financeiro!
    `;
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `planejador-orcamento-${new Date().getFullYear()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showToast('Planejador baixado com sucesso!', 'success');
}

// Configurar atualização automática
function setupInsightsRefresh() {
    // Atualizar insights a cada hora
    setInterval(() => {
        if (document.visibilityState === 'visible') {
            refreshInsights();
        }
    }, 3600000); // 1 hora
}

// Funções auxiliares
function getRiskColor(risk) {
    const colors = {
        'Baixo': 'success',
        'Moderado': 'warning',
        'Alto': 'danger',
        'Moderado-Alto': 'danger',
        'Baixo-Moderado': 'warning'
    };
    return colors[risk] || 'secondary';
}

function showModal(title, content) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">${title}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
    
    modal.addEventListener('hidden.bs.modal', () => {
        modal.remove();
    });
}

function showLoading(message = 'Carregando...') {
    const loader = document.createElement('div');
    loader.className = 'loader-overlay';
    loader.innerHTML = `
        <div class="loader-content">
            <div class="spinner-border text-primary"></div>
            <p class="mt-3">${message}</p>
        </div>
    `;
    document.body.appendChild(loader);
}

function hideLoading() {
    const loader = document.querySelector('.loader-overlay');
    if (loader) {
        loader.remove();
    }
}

function showToast(message, type = 'info') {
    // Implementar toast
    alert(`${type.toUpperCase()}: ${message}`);
}

// Exportar funções globais
window.refreshInsights = refreshInsights;
window.showBudgetPlanner = showBudgetPlanner;
window.showCompoundInterestCalculator = showCompoundInterestCalculator;
window.calculateCompoundInterest = calculateCompoundInterest;
window.calculateBudget = calculateBudget;

// Inicializar
document.addEventListener('DOMContentLoaded', initInsights);