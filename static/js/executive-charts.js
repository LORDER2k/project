/**
 * ContaSmart Pro Executive Charts
 * Sistema de gráficos executivos avançados
 */

class ExecutiveCharts {
    constructor() {
        this.charts = new Map();
        this.theme = {
            background: '#1e1e28',
            text: '#a0a0c0',
            grid: 'rgba(255, 255, 255, 0.05)',
            primary: '#0066ff',
            success: '#00ff88',
            warning: '#ff9900',
            danger: '#ff3366',
            accent: '#9d00ff',
            info: '#00ccff'
        };
        
        this.palette = [
            '#ff3366', '#ff9900', '#ff0066', '#00ccff',
            '#9966ff', '#33ccff', '#ffcc00', '#9d00ff',
            '#00ff88', '#0066ff', '#ff33cc', '#33ffcc'
        ];
        
        this.init();
    }

    init() {
        this.registerChartPlugins();
        this.autoInitCharts();
        this.setupResponsiveCharts();
    }

    registerChartPlugins() {
        // Plugin para background gradient
        Chart.register({
            id: 'gradientBackground',
            beforeDraw: (chart) => {
                const ctx = chart.ctx;
                const chartArea = chart.chartArea;
                
                if (!chartArea) return;
                
                // Background gradient
                const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
                gradient.addColorStop(0, 'rgba(30, 30, 40, 0.1)');
                gradient.addColorStop(1, 'rgba(30, 30, 40, 0.3)');
                
                ctx.save();
                ctx.fillStyle = gradient;
                ctx.fillRect(chartArea.left, chartArea.top, chartArea.right - chartArea.left, chartArea.bottom - chartArea.top);
                ctx.restore();
            }
        });

        // Plugin para tooltip personalizado
        Chart.register({
            id: 'executiveTooltip',
            afterDraw: (chart) => {
                const tooltip = chart.tooltip;
                if (!tooltip || !tooltip.opacity) return;
                
                const ctx = chart.ctx;
                const tooltipModel = tooltip;
                
                // Tooltip background com efeito de vidro
                ctx.save();
                ctx.shadowColor = 'rgba(0, 0, 0, 0.5)';
                ctx.shadowBlur = 20;
                ctx.shadowOffsetX = 0;
                ctx.shadowOffsetY = 10;
                
                // Background com blur
                ctx.fillStyle = 'rgba(30, 30, 40, 0.95)';
                ctx.fillRect(
                    tooltipModel.x - tooltipModel.width / 2 - 10,
                    tooltipModel.y - tooltipModel.height - 10,
                    tooltipModel.width + 20,
                    tooltipModel.height + 20
                );
                
                // Borda neon
                ctx.strokeStyle = this.theme.primary;
                ctx.lineWidth = 2;
                ctx.strokeRect(
                    tooltipModel.x - tooltipModel.width / 2 - 10,
                    tooltipModel.y - tooltipModel.height - 10,
                    tooltipModel.width + 20,
                    tooltipModel.height + 20
                );
                
                ctx.restore();
            }
        });
    }

    autoInitCharts() {
        // Inicializar todos os gráficos na página
        document.querySelectorAll('canvas[data-chart]').forEach(canvas => {
            const chartType = canvas.dataset.chart;
            const dataUrl = canvas.dataset.url;
            
            if (dataUrl) {
                this.loadChartData(canvas, chartType, dataUrl);
            } else {
                this.initChart(canvas, chartType);
            }
        });
    }

    async loadChartData(canvas, chartType, dataUrl) {
        try {
            const response = await fetch(dataUrl);
            const data = await response.json();
            this.initChart(canvas, chartType, data);
        } catch (error) {
            console.error(`Error loading chart data from ${dataUrl}:`, error);
            this.initChart(canvas, chartType);
        }
    }

    initChart(canvas, chartType, data = null) {
        const ctx = canvas.getContext('2d');
        
        let chart;
        
        switch(chartType) {
            case 'trend':
                chart = this.createTrendChart(ctx, data);
                break;
            case 'category':
                chart = this.createCategoryChart(ctx, data);
                break;
            case 'comparison':
                chart = this.createComparisonChart(ctx, data);
                break;
            case 'goal-progress':
                chart = this.createGoalProgressChart(ctx, data);
                break;
            case 'income-expense':
                chart = this.createIncomeExpenseChart(ctx, data);
                break;
            case 'forecast':
                chart = this.createForecastChart(ctx, data);
                break;
            default:
                chart = this.createLineChart(ctx, data);
        }
        
        this.charts.set(canvas.id, chart);
        this.applyChartEffects(canvas.id, chart);
    }

    createTrendChart(ctx, data) {
        const defaultData = {
            labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
            datasets: [
                {
                    label: 'Receitas',
                    data: [3200, 4200, 3800, 5100, 4900, 6200],
                    borderColor: this.theme.success,
                    backgroundColor: this.hexToRgba(this.theme.success, 0.1),
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 6,
                    pointHoverRadius: 10,
                    pointBackgroundColor: this.theme.success,
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2
                },
                {
                    label: 'Despesas',
                    data: [2800, 3500, 3200, 4200, 3800, 4500],
                    borderColor: this.theme.danger,
                    backgroundColor: this.hexToRgba(this.theme.danger, 0.1),
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 6,
                    pointHoverRadius: 10,
                    pointBackgroundColor: this.theme.danger,
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2
                },
                {
                    label: 'Saldo',
                    data: [400, 700, 600, 900, 1100, 1700],
                    borderColor: this.theme.primary,
                    backgroundColor: 'transparent',
                    borderWidth: 3,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 6,
                    pointHoverRadius: 10,
                    pointBackgroundColor: this.theme.primary,
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    borderDash: [5, 5]
                }
            ]
        };

        return new Chart(ctx, {
            type: 'line',
            data: data || defaultData,
            options: this.getLineChartOptions()
        });
    }

    createCategoryChart(ctx, data) {
        const defaultData = {
            labels: ['Alimentação', 'Transporte', 'Moradia', 'Lazer', 'Educação', 'Saúde', 'Compras', 'Outros'],
            datasets: [{
                data: [25, 15, 30, 10, 12, 8, 15, 5],
                backgroundColor: this.palette,
                borderColor: this.theme.background,
                borderWidth: 2,
                hoverOffset: 20
            }]
        };

        return new Chart(ctx, {
            type: 'doughnut',
            data: data || defaultData,
            options: this.getDoughnutChartOptions()
        });
    }

    createComparisonChart(ctx, data) {
        const defaultData = {
            labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai'],
            datasets: [
                {
                    label: '2024',
                    data: [3200, 4200, 3800, 5100, 4900],
                    backgroundColor: this.hexToRgba(this.theme.primary, 0.7),
                    borderColor: this.theme.primary,
                    borderWidth: 2
                },
                {
                    label: '2023',
                    data: [2800, 3500, 3200, 4200, 3800],
                    backgroundColor: this.hexToRgba(this.theme.accent, 0.7),
                    borderColor: this.theme.accent,
                    borderWidth: 2
                }
            ]
        };

        return new Chart(ctx, {
            type: 'bar',
            data: data || defaultData,
            options: this.getBarChartOptions()
        });
    }

    createGoalProgressChart(ctx, data) {
        const defaultData = {
            labels: ['Reserva Emergencial', 'Viagem Internacional', 'Novo Notebook', 'Investimentos', 'Curso Especialização'],
            datasets: [{
                label: 'Progresso',
                data: [75, 40, 60, 90, 50],
                backgroundColor: [
                    this.theme.success,
                    this.theme.warning,
                    this.theme.primary,
                    this.theme.accent,
                    this.theme.info
                ],
                borderColor: this.theme.background,
                borderWidth: 1,
                borderRadius: 8
            }]
        };

        return new Chart(ctx, {
            type: 'bar',
            data: data || defaultData,
            options: this.getHorizontalBarOptions()
        });
    }

    createIncomeExpenseChart(ctx, data) {
        const defaultData = {
            labels: ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
            datasets: [
                {
                    label: 'Receitas',
                    data: [150, 200, 180, 300, 250, 100, 50],
                    backgroundColor: this.hexToRgba(this.theme.success, 0.8),
                    borderColor: this.theme.success,
                    borderWidth: 2
                },
                {
                    label: 'Despesas',
                    data: [100, 120, 150, 200, 180, 80, 40],
                    backgroundColor: this.hexToRgba(this.theme.danger, 0.8),
                    borderColor: this.theme.danger,
                    borderWidth: 2
                }
            ]
        };

        return new Chart(ctx, {
            type: 'bar',
            data: data || defaultData,
            options: this.getGroupedBarOptions()
        });
    }

    createForecastChart(ctx, data) {
        const defaultData = {
            labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
            datasets: [
                {
                    label: 'Realizado',
                    data: [3200, 4200, 3800, 5100, 4900, 6200, 5800, 6500, 7000, 7500, 8000, 8500],
                    borderColor: this.theme.primary,
                    backgroundColor: this.hexToRgba(this.theme.primary, 0.1),
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Previsão',
                    data: [null, null, null, null, null, null, 6200, 6800, 7200, 7800, 8200, 8800],
                    borderColor: this.theme.accent,
                    backgroundColor: this.hexToRgba(this.theme.accent, 0.1),
                    borderWidth: 3,
                    fill: '+1',
                    tension: 0.4,
                    borderDash: [5, 5]
                }
            ]
        };

        return new Chart(ctx, {
            type: 'line',
            data: data || defaultData,
            options: this.getForecastChartOptions()
        });
    }

    createLineChart(ctx, data) {
        const defaultData = {
            labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
            datasets: [{
                label: 'Dataset',
                data: [65, 59, 80, 81, 56, 55],
                borderColor: this.theme.primary,
                backgroundColor: this.hexToRgba(this.theme.primary, 0.1),
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        };

        return new Chart(ctx, {
            type: 'line',
            data: data || defaultData,
            options: this.getLineChartOptions()
        });
    }

    getLineChartOptions() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: this.theme.text,
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
                    backgroundColor: 'rgba(30, 30, 40, 0.95)',
                    titleColor: '#ffffff',
                    bodyColor: this.theme.text,
                    borderColor: this.theme.primary,
                    borderWidth: 1,
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        label: (context) => {
                            return `${context.dataset.label}: R$ ${context.parsed.y.toFixed(2)}`;
                        },
                    },
                },
            },
            scales: {
                x: {
                    grid: {
                        color: this.theme.grid,
                        drawBorder: false
                    },
                    ticks: {
                        color: this.theme.text,
                        font: {
                            family: 'Inter, sans-serif',
                            size: 11
                        }
                    }
                },
                y: {
                    grid: {
                        color: this.theme.grid,
                        drawBorder: false
                    },
                    ticks: {
                        color: this.theme.text,
                        font: {
                            family: 'Inter, sans-serif',
                            size: 11
                        },
                        callback: (value) => {
                            return 'R$ ' + value.toLocaleString('pt-BR');
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        };
    }

    getDoughnutChartOptions() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: this.theme.text,
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
                    backgroundColor: 'rgba(30, 30, 40, 0.95)',
                    titleColor: '#ffffff',
                    bodyColor: this.theme.text,
                    borderColor: this.theme.primary,
                    borderWidth: 1,
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        label: (context) => {
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${context.label}: R$ ${value.toFixed(2)} (${percentage}%)`;
                        },
                    },
                },
            },
        };
    }

    getBarChartOptions() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: this.theme.text,
                        font: {
                            family: 'Inter, sans-serif',
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(30, 30, 40, 0.95)',
                    titleColor: '#ffffff',
                    bodyColor: this.theme.text,
                    borderColor: this.theme.primary,
                    borderWidth: 1,
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        label: (context) => {
                            return `${context.dataset.label}: R$ ${context.parsed.y.toFixed(2)}`;
                        },
                    },
                },
            },
            scales: {
                x: {
                    grid: {
                        color: this.theme.grid,
                        drawBorder: false
                    },
                    ticks: {
                        color: this.theme.text,
                        font: {
                            family: 'Inter, sans-serif',
                            size: 11
                        }
                    }
                },
                y: {
                    grid: {
                        color: this.theme.grid,
                        drawBorder: false
                    },
                    ticks: {
                        color: this.theme.text,
                        font: {
                            family: 'Inter, sans-serif',
                            size: 11
                        },
                        callback: (value) => {
                            return 'R$ ' + value.toLocaleString('pt-BR');
                        }
                    }
                }
            }
        };
    }

    getHorizontalBarOptions() {
        const options = this.getBarChartOptions();
        options.indexAxis = 'y';
        options.scales.x.max = 100;
        options.scales.x.ticks.callback = (value) => {
            return value + '%';
        };
        return options;
    }

    getGroupedBarOptions() {
        return {
            ...this.getBarChartOptions(),
            scales: {
                x: {
                    grid: {
                        color: this.theme.grid,
                        drawBorder: false
                    },
                    ticks: {
                        color: this.theme.text,
                        font: {
                            family: 'Inter, sans-serif',
                            size: 11
                        }
                    }
                },
                y: {
                    grid: {
                        color: this.theme.grid,
                        drawBorder: false
                    },
                    ticks: {
                        color: this.theme.text,
                        font: {
                            family: 'Inter, sans-serif',
                            size: 11
                        },
                        callback: (value) => {
                            return 'R$ ' + value.toLocaleString('pt-BR');
                        }
                    },
                    stacked: false
                }
            }
        };
    }

    getForecastChartOptions() {
        return {
            ...this.getLineChartOptions(),
            plugins: {
                ...this.getLineChartOptions().plugins,
                tooltip: {
                    ...this.getLineChartOptions().plugins.tooltip,
                    callbacks: {
                        label: (context) => {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += `R$ ${context.parsed.y.toFixed(2)}`;
                                if (context.dataset.label === 'Previsão') {
                                    label += ' (projetado)';
                                }
                            }
                            return label;
                        },
                    },
                },
            },
        };
    }

    applyChartEffects(chartId, chart) {
        // Adicionar efeitos visuais aos gráficos
        const canvas = chart.canvas;
        
        // Efeito de brilho no hover
        canvas.addEventListener('mouseenter', () => {
            canvas.style.filter = 'drop-shadow(0 0 10px rgba(0, 102, 255, 0.5))';
        });
        
        canvas.addEventListener('mouseleave', () => {
            canvas.style.filter = '';
        });
        
        // Animação de entrada
        chart.options.animation = {
            duration: 1000,
            easing: 'easeOutQuart'
        };
        
        chart.update();
    }

    setupResponsiveCharts() {
        // Redimensionar gráficos quando a janela mudar de tamanho
        window.addEventListener('resize', () => {
            this.charts.forEach(chart => {
                chart.resize();
            });
        });
    }

    updateChart(chartId, newData) {
        const chart = this.charts.get(chartId);
        if (chart) {
            chart.data = newData;
            chart.update();
        }
    }

    addDataPoint(chartId, label, data) {
        const chart = this.charts.get(chartId);
        if (chart) {
            chart.data.labels.push(label);
            chart.data.datasets.forEach((dataset, i) => {
                dataset.data.push(data[i] || 0);
            });
            chart.update();
        }
    }

    removeDataPoint(chartId, index) {
        const chart = this.charts.get(chartId);
        if (chart) {
            chart.data.labels.splice(index, 1);
            chart.data.datasets.forEach(dataset => {
                dataset.data.splice(index, 1);
            });
            chart.update();
        }
    }

    changeChartType(chartId, newType) {
        const chart = this.charts.get(chartId);
        if (chart) {
            chart.config.type = newType;
            chart.update();
        }
    }

    exportChart(chartId, format = 'png') {
        const chart = this.charts.get(chartId);
        if (chart) {
            const link = document.createElement('a');
            link.download = `chart-${chartId}-${new Date().getTime()}.${format}`;
            link.href = chart.toBase64Image();
            link.click();
        }
    }

    printChart(chartId) {
        const chart = this.charts.get(chartId);
        if (chart) {
            const win = window.open('');
            win.document.write(`
                <html>
                    <head>
                        <title>Gráfico - ${chartId}</title>
                        <style>
                            body { 
                                font-family: Arial, sans-serif; 
                                padding: 20px;
                                display: flex;
                                justify-content: center;
                                align-items: center;
                                height: 100vh;
                            }
                            img { 
                                max-width: 100%;
                                height: auto;
                            }
                        </style>
                    </head>
                    <body>
                        <img src="${chart.toBase64Image()}">
                        <script>
                            window.onload = () => window.print();
                        </script>
                    </body>
                </html>
            `);
            win.document.close();
        }
    }

    hexToRgba(hex, alpha = 1) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    generateRandomData(count = 6, min = 1000, max = 10000) {
        return Array.from({ length: count }, () => 
            Math.floor(Math.random() * (max - min + 1)) + min
        );
    }

    generateTimeSeriesData(days = 30, base = 1000, variance = 500) {
        const data = [];
        let current = base;
        
        for (let i = 0; i < days; i++) {
            current += (Math.random() - 0.5) * variance * 2;
            current = Math.max(0, current);
            data.push(Math.round(current));
        }
        
        return data;
    }

    // Métodos utilitários para dashboard
    createMiniSparkline(canvas, data, color = this.theme.primary) {
        const ctx = canvas.getContext('2d');
        
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map((_, i) => i),
                datasets: [{
                    data: data,
                    borderColor: color,
                    backgroundColor: this.hexToRgba(color, 0.1),
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

    createProgressCircle(canvas, percentage, color = this.theme.primary) {
        const ctx = canvas.getContext('2d');
        
        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [percentage, 100 - percentage],
                    backgroundColor: [color, this.theme.grid],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '75%',
                rotation: -90,
                circumference: 180,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                },
                animation: {
                    animateRotate: true,
                    animateScale: true
                }
            }
        });
    }

    createGaugeChart(canvas, value, max = 100, color = this.theme.primary) {
        const ctx = canvas.getContext('2d');
        const percentage = (value / max) * 100;
        
        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [percentage, 100 - percentage],
                    backgroundColor: [color, this.theme.grid],
                    borderWidth: 0,
                    circumference: 270,
                    rotation: -135
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '85%',
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                }
            }
        });
    }

    // Método para criar dashboard de métricas
    createMetricsDashboard(containerId, metrics) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        const dashboardHTML = `
            <div class="metrics-dashboard">
                ${metrics.map(metric => `
                    <div class="metric-card">
                        <div class="metric-header">
                            <h4>${metric.title}</h4>
                            <span class="metric-badge ${metric.trend > 0 ? 'positive' : 'negative'}">
                                <i class="fas fa-${metric.trend > 0 ? 'arrow-up' : 'arrow-down'}"></i>
                                ${Math.abs(metric.trend)}%
                            </span>
                        </div>
                        <div class="metric-value">${metric.value}</div>
                        <div class="metric-chart">
                            <canvas id="chart-${metric.id}" height="40"></canvas>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        container.innerHTML = dashboardHTML;
        
        // Inicializar mini gráficos
        metrics.forEach(metric => {
            const canvas = document.getElementById(`chart-${metric.id}`);
            if (canvas && metric.sparklineData) {
                this.createMiniSparkline(canvas, metric.sparklineData, metric.color);
            }
        });
    }
}

// Inicializar sistema de gráficos
document.addEventListener('DOMContentLoaded', () => {
    window.executiveCharts = new ExecutiveCharts();
    
    // Adicionar atalhos de teclado
    document.addEventListener('keydown', (e) => {
        // Ctrl + P para imprimir gráfico ativo
        if (e.ctrlKey && e.key === 'p') {
            e.preventDefault();
            const activeChart = document.querySelector('canvas:hover');
            if (activeChart && activeChart.id) {
                executiveCharts.printChart(activeChart.id);
            }
        }
        
        // Ctrl + E para exportar gráfico ativo
        if (e.ctrlKey && e.key === 'e') {
            e.preventDefault();
            const activeChart = document.querySelector('canvas:hover');
            if (activeChart && activeChart.id) {
                executiveCharts.exportChart(activeChart.id);
            }
        }
    });
});

// Funções globais para acesso fácil
function updateChartData(chartId, data) {
    if (window.executiveCharts) {
        window.executiveCharts.updateChart(chartId, data);
    }
}

function exportChartAsImage(chartId) {
    if (window.executiveCharts) {
        window.executiveCharts.exportChart(chartId);
    }
}

function toggleChartType(chartId, type1, type2) {
    if (window.executiveCharts) {
        const chart = window.executiveCharts.charts.get(chartId);
        if (chart) {
            const currentType = chart.config.type;
            const newType = currentType === type1 ? type2 : type1;
            window.executiveCharts.changeChartType(chartId, newType);
        }
    }
}

// Exemplo de uso:
// <canvas id="myChart" data-chart="trend" data-url="/api/trend-data"></canvas>