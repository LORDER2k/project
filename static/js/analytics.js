// Analytics.js - Script para análises avançadas

let analyticsCharts = {
    trend: null,
    expense: null,
    income: null
};

// Inicializar análises
function initAnalytics() {
    setupAnalyticsFilters();
    setupChartExport();
    setupDataRefresh();
}

// Configurar filtros
function setupAnalyticsFilters() {
    // Filtro de período
    document.querySelectorAll('[data-period]').forEach(btn => {
        btn.addEventListener('click', function() {
            const period = this.dataset.period;
            updateAnalyticsPeriod(period);
        });
    });
    
    // Filtro de categoria
    const categoryFilter = document.getElementById('category-filter');
    if (categoryFilter) {
        categoryFilter.addEventListener('change', function() {
            filterByCategory(this.value);
        });
    }
}

// Renderizar gráfico de tendências
function renderTrendChart(data) {
    const ctx = document.getElementById('trendChart').getContext('2d');
    
    if (analyticsCharts.trend) {
        analyticsCharts.trend.destroy();
    }
    
    const labels = data.map(item => item.mes);
    const receitas = data.map(item => item.receitas);
    const despesas = data.map(item => item.despesas);
    const saldos = data.map(item => item.saldo);
    
    analyticsCharts.trend = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Receitas',
                    data: receitas,
                    borderColor: '#1cc88a',
                    backgroundColor: 'rgba(28, 200, 138, 0.1)',
                    tension: 0.3,
                    fill: false
                },
                {
                    label: 'Despesas',
                    data: despesas,
                    borderColor: '#e74a3b',
                    backgroundColor: 'rgba(231, 74, 59, 0.1)',
                    tension: 0.3,
                    fill: false
                },
                {
                    label: 'Saldo',
                    data: saldos,
                    borderColor: '#4e73df',
                    backgroundColor: 'rgba(78, 115, 223, 0.2)',
                    tension: 0.3,
                    fill: '+1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: R$ ${context.raw.toFixed(2)}`;
                        },
                    },
                },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return 'R$ ' + value.toFixed(2);
                        }
                    }
                }
            }
        }
    });
}

// Renderizar gráfico de despesas
function renderExpenseChart(expenses) {
    const ctx = document.getElementById('expenseChart').getContext('2d');
    
    if (analyticsCharts.expense) {
        analyticsCharts.expense.destroy();
    }
    
    const labels = expenses.map(item => item.name);
    const data = expenses.map(item => item.total);
    const colors = expenses.map(item => item.color || '#6c757d');
    
    analyticsCharts.expense = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            const total = data.reduce((a, b) => a + b, 0);
                            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                            return `${context.label}: R$ ${value.toFixed(2)} (${percentage}%)`;
                        },
                    },
                },
            },
        },
    });
}

// Renderizar gráfico de receitas
function renderIncomeChart(incomes) {
    const ctx = document.getElementById('incomeChart').getContext('2d');
    
    if (analyticsCharts.income) {
        analyticsCharts.income.destroy();
    }
    
    const labels = incomes.map(item => item.name);
    const data = incomes.map(item => item.total);
    const colors = incomes.map(item => item.color || '#36b9cc');
    
    analyticsCharts.income = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            const total = data.reduce((a, b) => a + b, 0);
                            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                            return `${context.label}: R$ ${value.toFixed(2)} (${percentage}%)`;
                        },
                    },
                },
            },
        },
    });
}

// Alterar tipo de gráfico de tendências
function changeTrendChart(type) {
    if (analyticsCharts.trend) {
        analyticsCharts.trend.config.type = type;
        analyticsCharts.trend.update();
        
        // Atualizar botões ativos
        document.querySelectorAll('[onclick*="changeTrendChart"]').forEach(btn => {
            btn.classList.remove('active');
        });
        event.target.classList.add('active');
    }
}

// Atualizar período de análise
function updateAnalyticsPeriod(period) {
    const url = new URL(window.location.href);
    url.searchParams.set('periodo', period);
    
    showLoading();
    window.location.href = url.toString();
}

// Filtrar por categoria
function filterByCategory(categoryId) {
    showLoading();
    
    // Atualizar gráficos com filtro aplicado
    fetch(`/api/category-filter?category_id=${categoryId}`)
        .then(response => response.json())
        .then(data => {
            updateFilteredCharts(data);
            hideLoading();
        });
}

// Atualizar gráficos filtrados
function updateFilteredCharts(filteredData) {
    if (filteredData.trend) {
        renderTrendChart(filteredData.trend);
    }
    
    if (filteredData.categories) {
        renderExpenseChart(filteredData.categories.expenses);
        renderIncomeChart(filteredData.categories.incomes);
    }
}

// Exportar análise como PDF
function exportAnalyticsPDF() {
    showToast('Gerando PDF...', 'info');
    
    // Capturar elementos do dashboard
    const element = document.querySelector('.container-fluid');
    
    html2pdf()
        .from(element)
        .set({
            margin: [10, 10, 10, 10],
            filename: `analise-financeira-${new Date().toISOString().split('T')[0]}.pdf`,
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2 },
            jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
        })
        .save()
        .then(() => {
            showToast('PDF gerado com sucesso!', 'success');
        });
}

// Exportar análise como Excel
function exportAnalyticsExcel() {
    showToast('Gerando Excel...', 'info');
    
    // Preparar dados
    const data = [
        ['Relatório Financeiro', '', '', ''],
        ['Data', new Date().toLocaleDateString('pt-BR'), '', ''],
        ['', '', '', ''],
        ['Categoria', 'Valor Total', 'Quantidade', 'Média']
    ];
    
    // Adicionar despesas
    window.categoriesData.expenses.forEach(item => {
        data.push([item.name, item.total, item.quantidade || 1, item.media || item.total]);
    });
    
    data.push(['', '', '', '']);
    data.push(['Receitas', '', '', '']);
    
    // Adicionar receitas
    window.categoriesData.incomes.forEach(item => {
        data.push([item.name, item.total, '', '']);
    });
    
    // Criar workbook
    const ws = XLSX.utils.aoa_to_sheet(data);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Análise Financeira');
    
    // Baixar arquivo
    XLSX.writeFile(wb, `analise-financeira-${new Date().toISOString().split('T')[0]}.xlsx`);
    showToast('Excel gerado com sucesso!', 'success');
}

// Compartilhar análise
function shareAnalytics() {
    if (navigator.share) {
        navigator.share({
            title: 'Minha Análise Financeira - ContaSmart Pro',
            text: 'Confira minha análise financeira completa!',
            url: window.location.href
        })
        .then(() => showToast('Análise compartilhada!', 'success'))
        .catch(error => console.log('Erro ao compartilhae:', error));
    } else {
        // Fallback para copiar link
        navigator.clipboard.writeText(window.location.href)
            .then(() => showToast('Link copiado para a área de transferência!', 'success'));
    }
}

// Configurar atualização automática
function setupDataRefresh() {
    // Atualizar a cada 5 minutos
    setInterval(() => {
        if (document.visibilityState === 'visible') {
            refreshAnalyticsData();
        }
    }, 300000); // 5 minutos
}

// Atualizar dados de análise
function refreshAnalyticsData() {
    fetch('/api/refresh-analytics')
        .then(response => response.json())
        .then(data => {
            if (data.updated) {
                showToast('Dados atualizados!', 'success');
                updateChartsWithNewData(data);
            }
        });
}

// Atualizar gráficos com novos dados
function updateChartsWithNewData(data) {
    if (data.trend && analyticsCharts.trend) {
        analyticsCharts.trend.data.datasets[0].data = data.trend.receitas;
        analyticsCharts.trend.data.datasets[1].data = data.trend.despesas;
        analyticsCharts.trend.data.datasets[2].data = data.trend.saldos;
        analyticsCharts.trend.update();
    }
}

// Mostrar loading
function showLoading() {
    const loader = document.createElement('div');
    loader.id = 'analytics-loader';
    loader.className = 'loader-overlay';
    loader.innerHTML = `
        <div class="loader-content">
            <div class="loader"></div>
            <p class="mt-3">Processando análise...</p>
        </div>
    `;
    document.body.appendChild(loader);
}

// Esconder loading
function hideLoading() {
    const loader = document.getElementById('analytics-loader');
    if (loader) {
        loader.remove();
    }
}

// Funções auxiliares
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

function showToast(message, type = 'info') {
    // Implementar notificação toast
    alert(`${type.toUpperCase()}: ${message}`);
}

// Inicializar ao carregar
document.addEventListener('DOMContentLoaded', initAnalytics);