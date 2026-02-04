// Neon Charts - Gráficos Futuristas com Chart.js

class NeonCharts {
    constructor() {
        this.charts = {};
        this.colors = {
            neonBlue: '#00f3ff',
            neonPurple: '#b967ff',
            neonGreen: '#00ff9d',
            neonPink: '#ff00ff',
            neonYellow: '#ffff00',
            neonCyan: '#00ffff'
        };
    }
    
    // Criar gradiente neon
    createNeonGradient(ctx, color1, color2, direction = 'vertical') {
        const gradient = direction === 'vertical'
            ? ctx.createLinearGradient(0, 0, 0, 400)
            : ctx.createLinearGradient(0, 0, 400, 0);
        
        gradient.addColorStop(0, color1);
        gradient.addColorStop(1, color2);
        
        return gradient;
    }
    
    // Inicializar gráfico principal
    initMainChart(canvasId, data) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        // Criar gradientes
        const incomeGradient = this.createNeonGradient(ctx, 
            this.colors.neonGreen + '80', 
            this.colors.neonGreen + '20'
        );
        
        const expenseGradient = this.createNeonGradient(ctx, 
            this.colors.neonPink + '80', 
            this.colors.neonPink + '20'
        );
        
        // Configuração do gráfico
        this.charts.main = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels || ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
                datasets: [
                    {
                        label: 'Receitas',
                        data: data.incomes || [1200, 1900, 1500, 2200, 1800, 2500],
                        borderColor: this.colors.neonGreen,
                        backgroundColor: incomeGradient,
                        tension: 0.4,
                        fill: true,
                        pointBackgroundColor: this.colors.neonGreen,
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 6,
                        pointHoverRadius: 8
                    },
                    {
                        label: 'Despesas',
                        data: data.expenses || [800, 1100, 900, 1400, 1200, 1600],
                        borderColor: this.colors.neonPink,
                        backgroundColor: expenseGradient,
                        tension: 0.4,
                        fill: true,
                        pointBackgroundColor: this.colors.neonPink,
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 6,
                        pointHoverRadius: 8
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#fff',
                            font: {
                                family: "'Exo 2', sans-serif",
                                size: 12
                            },
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: this.colors.neonBlue,
                        borderWidth: 1,
                        cornerRadius: 8,
                        padding: 12,
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: R$ ${context.raw.toFixed(2)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)',
                            callback: function(value) {
                                return 'R$ ' + value;
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                animations: {
                    tension: {
                        duration: 1000,
                        easing: 'linear'
                    }
                }
            }
        });
    }
    
    // Inicializar gráfico de pizza
    initPieChart(canvasId, data) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        this.charts.pie = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels || ['Alimentação', 'Transporte', 'Moradia', 'Lazer', 'Saúde', 'Outros'],
                datasets: [{
                    data: data.values || [30, 20, 25, 10, 8, 7],
                    backgroundColor: [
                        this.colors.neonBlue,
                        this.colors.neonPurple,
                        this.colors.neonGreen,
                        this.colors.neonPink,
                        this.colors.neonYellow,
                        this.colors.neonCyan
                    ],
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 2,
                    hoverOffset: 20
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: '#fff',
                            padding: 20,
                            font: {
                                size: 11
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: R$ ${value.toFixed(2)} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Inicializar gráfico de barras
    initBarChart(canvasId, data) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        // Criar gradiente para barras
        const barGradient = this.createNeonGradient(ctx, 
            this.colors.neonBlue + 'FF', 
            this.colors.neonPurple + 'FF',
            'vertical'
        );
        
        this.charts.bar = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels || ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
                datasets: [{
                    label: 'Gastos Diários',
                    data: data.values || [85, 120, 95, 150, 200, 180, 130],
                    backgroundColor: barGradient,
                    borderColor: this.colors.neonBlue,
                    borderWidth: 1,
                    borderRadius: 8,
                    hoverBackgroundColor: this.colors.neonPurple
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)',
                            callback: function(value) {
                                return 'R$ ' + value;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Gráfico de radar futurista
    initRadarChart(canvasId, data) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        this.charts.radar = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: data.labels || ['Poupança', 'Investimentos', 'Controle', 'Metas', 'Educação'],
                datasets: [
                    {
                        label: 'Seu Progresso',
                        data: data.userData || [85, 70, 90, 65, 80],
                        backgroundColor: this.colors.neonBlue + '20',
                        borderColor: this.colors.neonBlue,
                        pointBackgroundColor: this.colors.neonBlue,
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: this.colors.neonBlue,
                        borderWidth: 2
                    },
                    {
                        label: 'Média Geral',
                        data: data.averageData || [65, 60, 75, 55, 70],
                        backgroundColor: this.colors.neonPurple + '20',
                        borderColor: this.colors.neonPurple,
                        pointBackgroundColor: this.colors.neonPurple,
                        pointBorderColor: '#fff',
                        borderWidth: 2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            stepSize: 20,
                            color: 'rgba(255, 255, 255, 0.7)',
                            callback: function(value) {
                                return value + '%';
                            }
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        angleLines: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        pointLabels: {
                            color: 'rgba(255, 255, 255, 0.8)',
                            font: {
                                size: 11
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: '#fff'
                        }
                    }
                }
            }
        });
    }
    
    // Gráfico de linha com efeito neon
    initSparkline(canvasId, data, color = this.colors.neonBlue) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map((_, i) => i + 1),
                datasets: [{
                    data: data,
                    borderColor: color,
                    backgroundColor: color + '20',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                },
                scales: {
                    x: { display: false },
                    y: { display: false }
                },
                elements: {
                    line: {
                        tension: 0.4
                    }
                }
            }
        });
    }
    
    // Atualizar gráfico com novos dados
    updateChart(chartId, newData) {
        if (this.charts[chartId]) {
            this.charts[chartId].data.datasets.forEach((dataset, index) => {
                if (newData[index]) {
                    dataset.data = newData[index];
                }
            });
            
            if (newData.labels) {
                this.charts[chartId].data.labels = newData.labels;
            }
            
            this.charts[chartId].update();
        }
    }
    
    // Exportar gráfico como imagem
    exportChart(chartId, filename = 'grafico') {
        if (this.charts[chartId]) {
            const link = document.createElement('a');
            link.download = `${filename}-${new Date().toISOString().split('T')[0]}.png`;
            link.href = this.charts[chartId].toBase64Image();
            link.click();
            
            showNeonNotification('Gráfico exportado com sucesso!', 'success');
        }
    }
    
    // Alternar tipo de gráfico
    toggleChartType(chartId, newType) {
        if (this.charts[chartId]) {
            this.charts[chartId].config.type = newType;
            this.charts[chartId].update();
        }
    }
    
    // Animação de entrada do gráfico
    animateChart(chartId) {
        if (this.charts[chartId]) {
            this.charts[chartId].options.animation = {
                duration: 1000,
                easing: 'easeOutQuart'
            };
            this.charts[chartId].update();
        }
    }
    
    // Destruir gráfico
    destroyChart(chartId) {
        if (this.charts[chartId]) {
            this.charts[chartId].destroy();
            delete this.charts[chartId];
        }
    }
}

// Inicializar gráficos globalmente
const neonCharts = new NeonCharts();

// Funções globais
function initNeonCharts() {
    // Inicializar gráficos se os canvas existirem
    if (document.getElementById('mainNeonChart')) {
        neonCharts.initMainChart('mainNeonChart', window.chartData || {});
    }
    
    if (document.getElementById('categoryNeonChart')) {
        neonCharts.initPieChart('categoryNeonChart', window.pieChartData || {});
    }
    
    if (document.getElementById('barNeonChart')) {
        neonCharts.initBarChart('barNeonChart', window.barChartData || {});
    }
    
    if (document.getElementById('radarNeonChart')) {
        neonCharts.initRadarChart('radarNeonChart', window.radarChartData || {});
    }
}

function refreshPieChart() {
    // Simular atualização de dados
    const newData = {
        labels: ['Alimentação', 'Transporte', 'Moradia', 'Lazer', 'Saúde', 'Educação', 'Investimentos'],
        values: [25, 15, 30, 10, 8, 7, 5]
    };
    
    neonCharts.updateChart('pie', newData);
    showNeonNotification('Gráfico atualizado!', 'success');
}

function exportChartAsImage(chartId) {
    neonCharts.exportChart(chartId);
}

// Inicializar ao carregar
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar gráficos após um pequeno delay
    setTimeout(initNeonCharts, 100);
    
    // Configurar eventos de botões de gráficos
    document.querySelectorAll('[data-chart-action]').forEach(btn => {
        btn.addEventListener('click', function() {
            const action = this.dataset.chartAction;
            const target = this.dataset.chartTarget;
            
            switch(action) {
                case 'export':
                    exportChartAsImage(target);
                    break;
                case 'refresh':
                    if (target === 'categoryNeonChart') {
                        refreshPieChart();
                    }
                    break;
                case 'animate':
                    neonCharts.animateChart(target);
                    break;
            }
        });
    });
});