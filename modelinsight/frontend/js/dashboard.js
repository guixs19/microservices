// Elementos do DOM
const jobIdSpan = document.getElementById('jobId');
const modelBtns = document.getElementById('modelBtns');
const metricsGrid = document.getElementById('metricsGrid');
const chartReal = document.getElementById('chartReal');
const chartPredicted = document.getElementById('chartPredicted');
const dataTableBody = document.getElementById('dataTableBody');

// Obter job_id da URL
const urlParams = new URLSearchParams(window.location.search);
const jobId = urlParams.get('job_id');
jobIdSpan.textContent = jobId;

// Estado do dashboard
let currentData = null;
let currentModel = null;
let charts = {};

// Carregar dados ao iniciar
document.addEventListener('DOMContentLoaded', async () => {
    if (!jobId) {
        showError('Nenhum job ID encontrado');
        return;
    }
    
    await loadDashboardData();
});

// Carregar dados do dashboard
async function loadDashboardData() {
    showLoading();
    
    try {
        const data = await api.getResults(jobId);
        currentData = data;
        
        // Atualizar interface
        updateModelButtons(data.models);
        
        // Selecionar melhor modelo por padrão
        const bestModel = data.models.find(m => m.is_best) || data.models[0];
        if (bestModel) {
            await selectModel(bestModel.name);
        }
        
        hideLoading();
        
        // Animar entrada
        gsap.from('.dashboard-panel', {
            duration: 0.8,
            y: 50,
            opacity: 0,
            stagger: 0.2,
            ease: 'power3.out'
        });
        
    } catch (error) {
        hideLoading();
        showError(error.message);
    }
}

// Atualizar botões de modelos
function updateModelButtons(models) {
    modelBtns.innerHTML = '';
    
    models.forEach(model => {
        const btn = document.createElement('button');
        btn.className = `model-btn ${model.is_best ? 'best' : ''}`;
        btn.textContent = model.name;
        btn.onclick = () => selectModel(model.name);
        
        modelBtns.appendChild(btn);
    });
}

// Selecionar modelo
async function selectModel(modelName) {
    // Atualizar UI dos botões
    document.querySelectorAll('.model-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.textContent === modelName) {
            btn.classList.add('active');
        }
    });
    
    currentModel = modelName;
    
    // Buscar detalhes do modelo
    const modelDetails = await api.getModelDetails(jobId, modelName);
    
    // Atualizar métricas
    updateMetrics(modelDetails.metrics);
    
    // Atualizar gráficos
    updateCharts(modelDetails.predictions);
    
    // Atualizar tabela
    updateDataTable(modelDetails.predictions);
}

// Atualizar cards de métricas
function updateMetrics(metrics) {
    metricsGrid.innerHTML = '';
    
    const metricCards = [
        { label: 'R² Score', value: metrics.r2, format: 'percent' },
        { label: 'MSE', value: metrics.mse, format: 'number' },
        { label: 'RMSE', value: metrics.rmse, format: 'number' },
        { label: 'MAE', value: metrics.mae, format: 'number' }
    ];
    
    metricCards.forEach(metric => {
        if (metric.value !== undefined) {
            const card = document.createElement('div');
            card.className = 'metric-card';
            
            const formattedValue = metric.format === 'percent' 
                ? (metric.value * 100).toFixed(2) + '%'
                : metric.value.toFixed(4);
            
            card.innerHTML = `
                <div class="metric-label">${metric.label}</div>
                <div class="metric-value">${formattedValue}</div>
            `;
            
            metricsGrid.appendChild(card);
            
            // Animar card
            gsap.from(card, {
                duration: 0.5,
                scale: 0,
                opacity: 0,
                ease: 'back.out',
                delay: 0.1 * Array.from(metricsGrid.children).indexOf(card)
            });
        }
    });
}

// Atualizar gráficos
function updateCharts(predictions) {
    if (!predictions) return;
    
    const ctxReal = chartReal.getContext('2d');
    const ctxPredicted = chartPredicted.getContext('2d');
    
    // Destruir gráficos existentes
    if (charts.real) charts.real.destroy();
    if (charts.predicted) charts.predicted.destroy();
    
    // Dados para os gráficos
    const indices = predictions.indices || predictions.actual.map((_, i) => i);
    
    // Gráfico de dados reais
    charts.real = new Chart(ctxReal, {
        type: 'line',
        data: {
            labels: indices,
            datasets: [{
                label: 'Dados Reais',
                data: predictions.actual,
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#94a3b8' }
                }
            },
            scales: {
                x: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } },
                y: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } }
            }
        }
    });
    
    // Gráfico de dados previstos
    charts.predicted = new Chart(ctxPredicted, {
        type: 'line',
        data: {
            labels: indices,
            datasets: [{
                label: 'Previsões do Modelo',
                data: predictions.predicted,
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#94a3b8' }
                }
            },
            scales: {
                x: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } },
                y: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } }
            }
        }
    });
}

// Atualizar tabela de dados
function updateDataTable(predictions) {
    if (!predictions) return;
    
    dataTableBody.innerHTML = '';
    
    // Mostrar primeiras 20 linhas
    const rows = Math.min(20, predictions.actual.length);
    
    for (let i = 0; i < rows; i++) {
        const tr = document.createElement('tr');
        
        const actual = predictions.actual[i];
        const predicted = predictions.predicted[i];
        const error = Math.abs(actual - predicted);
        const errorPercent = (error / actual) * 100;
        
        tr.innerHTML = `
            <td>${i + 1}</td>
            <td>${actual.toFixed(4)}</td>
            <td>${predicted.toFixed(4)}</td>
            <td class="${errorPercent < 10 ? 'text-success' : errorPercent < 20 ? 'text-warning' : 'text-danger'}">
                ${errorPercent.toFixed(2)}%
            </td>
        `;
        
        dataTableBody.appendChild(tr);
    }
}

// Funções auxiliares
function showLoading() {
    document.getElementById('loading').classList.add('active');
    document.querySelector('.dashboard-content').style.opacity = '0.3';
}

function hideLoading() {
    document.getElementById('loading').classList.remove('active');
    document.querySelector('.dashboard-content').style.opacity = '1';
}

function showError(message) {
    const alert = document.createElement('div');
    alert.className = 'alert error';
    alert.innerHTML = `
        <i class="fas fa-exclamation-circle"></i>
        <span>${message}</span>
    `;
    
    document.querySelector('.container').prepend(alert);
}