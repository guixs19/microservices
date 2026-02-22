/**
 * Sistema de Créditos - Frontend JavaScript
 * Gerencia autenticação, transações e atualizações em tempo real
 */

// ============================================
// CONFIGURAÇÃO GLOBAL
// ============================================

// Armazenar token JWT
let authToken = localStorage.getItem('token');

// ============================================
// FUNÇÕES UTILITÁRIAS
// ============================================

/**
 * Mostra mensagem para o usuário
 * @param {string} message - Mensagem a ser exibida
 * @param {string} type - Tipo: 'success' ou 'error'
 */
function showMessage(message, type) {
    const messageDiv = document.getElementById('message');
    if (messageDiv) {
        messageDiv.textContent = message;
        messageDiv.className = `alert alert-${type}`;
        messageDiv.style.display = 'block';
        
        // Auto-esconder após 5 segundos
        setTimeout(() => {
            messageDiv.style.display = 'none';
        }, 5000);
    } else {
        console.log(`[${type}] ${message}`);
    }
}

/**
 * Faz requisições autenticadas com JWT
 * @param {string} url - Endpoint completo
 * @param {Object} options - Opções do fetch
 * @returns {Promise} - Resposta do fetch
 */
async function authenticatedFetch(url, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    try {
        const response = await fetch(url, {
            ...options,
            headers,
            credentials: 'same-origin'
        });
        
        // Se não autorizado, fazer logout
        if (response.status === 401) {
            const data = await response.json().catch(() => ({}));
            if (data.detail?.includes('Could not validate credentials')) {
                logout();
                showMessage('Sessão expirada. Faça login novamente.', 'error');
            }
        }
        
        return response;
    } catch (error) {
        console.error('Erro na requisição:', error);
        showMessage('Erro de conexão com o servidor', 'error');
        throw error;
    }
}

// ============================================
// FUNÇÕES DE AUTENTICAÇÃO
// ============================================

/**
 * Login do usuário
 * @param {Event} event - Evento do formulário
 */
async function login(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    
    if (!username || !password) {
        showMessage('Preencha todos os campos', 'error');
        return;
    }
    
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    try {
        const response = await fetch('/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            authToken = data.access_token;
            localStorage.setItem('token', authToken);
            showMessage('Login realizado com sucesso!', 'success');
            
            // Redirecionar para dashboard
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1000);
        } else {
            const error = await response.json();
            showMessage(error.detail || 'Erro ao fazer login', 'error');
        }
    } catch (error) {
        console.error('Erro no login:', error);
        showMessage('Erro ao conectar com o servidor', 'error');
    }
}

/**
 * Registro de novo usuário
 * @param {Event} event - Evento do formulário
 */
async function register(event) {
    event.preventDefault();
    
    const username = document.getElementById('reg-username').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value;
    const confirmPassword = document.getElementById('reg-confirm-password').value;
    
    // Validações
    if (!username || !email || !password || !confirmPassword) {
        showMessage('Preencha todos os campos', 'error');
        return;
    }
    
    if (password !== confirmPassword) {
        showMessage('As senhas não coincidem', 'error');
        return;
    }
    
    if (password.length < 6) {
        showMessage('A senha deve ter pelo menos 6 caracteres', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/users/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password })
        });
        
        if (response.ok) {
            showMessage('Usuário registrado com sucesso! Faça login.', 'success');
            
            // Limpar formulário
            document.getElementById('reg-username').value = '';
            document.getElementById('reg-email').value = '';
            document.getElementById('reg-password').value = '';
            document.getElementById('reg-confirm-password').value = '';
            
            // Mudar para aba de login
            const loginTab = document.querySelector('[data-tab="login"]');
            if (loginTab) {
                loginTab.click();
            }
        } else {
            const error = await response.json();
            showMessage(error.detail || 'Erro ao registrar', 'error');
        }
    } catch (error) {
        console.error('Erro no registro:', error);
        showMessage('Erro ao conectar com o servidor', 'error');
    }
}

/**
 * Logout do usuário
 */
function logout() {
    authToken = null;
    localStorage.removeItem('token');
    showMessage('Logout realizado com sucesso!', 'success');
    
    // Redirecionar para página inicial
    setTimeout(() => {
        window.location.href = '/';
    }, 1000);
}

// ============================================
// FUNÇÕES DO DASHBOARD
// ============================================

/**
 * Atualiza o saldo do usuário
 */
async function updateBalance() {
    try {
        const response = await authenticatedFetch('/api/users/balance');
        if (response.ok) {
            const balance = await response.json();
            const balanceElement = document.getElementById('balance');
            if (balanceElement) {
                balanceElement.textContent = `R$ ${balance.toFixed(2)}`;
            }
        }
    } catch (error) {
        console.error('Erro ao atualizar saldo:', error);
    }
}

/**
 * Carrega o histórico de transações
 */
async function loadTransactions() {
    try {
        const response = await authenticatedFetch('/api/users/transactions');
        if (response.ok) {
            const transactions = await response.json();
            displayTransactions(transactions);
        }
    } catch (error) {
        console.error('Erro ao carregar transações:', error);
    }
}

/**
 * Exibe as transações na interface
 * @param {Array} transactions - Lista de transações
 */
function displayTransactions(transactions) {
    const list = document.getElementById('transaction-list');
    if (!list) return;
    
    list.innerHTML = '';
    
    if (transactions.length === 0) {
        list.innerHTML = '<p class="text-center">Nenhuma transação encontrada.</p>';
        return;
    }
    
    transactions.forEach(t => {
        const item = document.createElement('div');
        item.className = 'transaction-item';
        
        const date = new Date(t.timestamp).toLocaleString('pt-BR');
        const amountClass = t.type === 'credit' ? 'transaction-credit' : 'transaction-debit';
        const amountSign = t.type === 'credit' ? '+' : '-';
        
        item.innerHTML = `
            <div>
                <strong>${t.description || 'Transação'}</strong><br>
                <small>${date}</small>
            </div>
            <div class="${amountClass}">
                ${amountSign} R$ ${t.amount.toFixed(2)}
            </div>
        `;
        
        list.appendChild(item);
    });
    
    // Atualizar gráfico
    updateChart(transactions);
}

/**
 * Atualiza o gráfico de gastos
 * @param {Array} transactions - Lista de transações
 */
function updateChart(transactions) {
    const ctx = document.getElementById('spendingChart');
    if (!ctx) return;
    
    // Processar dados para o gráfico (últimos 7 dias)
    const last7Days = [...Array(7)].map((_, i) => {
        const d = new Date();
        d.setDate(d.getDate() - i);
        return d.toLocaleDateString('pt-BR');
    }).reverse();
    
    const dailySpending = last7Days.map(date => {
        return transactions
            .filter(t => {
                const tDate = new Date(t.timestamp).toLocaleDateString('pt-BR');
                return tDate === date && t.type === 'debit';
            })
            .reduce((sum, t) => sum + t.amount, 0);
    });
    
    // Se já existe um gráfico, destruir e recriar
    if (window.myChart) {
        window.myChart.destroy();
    }
    
    window.myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: last7Days,
            datasets: [{
                label: 'Gastos Diários (R$)',
                data: dailySpending,
                borderColor: '#f56565',
                backgroundColor: 'rgba(245, 101, 101, 0.1)',
                tension: 0.1,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: value => 'R$ ' + value.toFixed(2)
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            }
        }
    });
}

// ============================================
// OPERAÇÕES DE PAGAMENTO
// ============================================

/**
 * Simula um pagamento
 * @param {Event} event - Evento do formulário
 */
async function simulatePayment(event) {
    event.preventDefault();
    
    const amount = parseFloat(document.getElementById('payment-amount').value);
    const description = document.getElementById('payment-description').value.trim();
    
    if (isNaN(amount) || amount <= 0) {
        showMessage('O valor deve ser maior que zero', 'error');
        return;
    }
    
    try {
        const response = await authenticatedFetch('/api/payments/simulate', {
            method: 'POST',
            body: JSON.stringify({ amount, description })
        });
        
        if (response.ok) {
            const result = await response.json();
            showMessage(result.message, 'success');
            
            // Atualizar interface
            await updateBalance();
            await loadTransactions();
            
            // Limpar formulário
            document.getElementById('payment-amount').value = '';
            document.getElementById('payment-description').value = '';
        } else {
            const error = await response.json();
            showMessage(error.detail || 'Erro ao processar pagamento', 'error');
        }
    } catch (error) {
        console.error('Erro no pagamento:', error);
        showMessage('Erro ao processar pagamento', 'error');
    }
}

/**
 * Recarrega créditos
 * @param {Event} event - Evento do formulário
 */
async function rechargeCredits(event) {
    event.preventDefault();
    
    const amount = parseFloat(document.getElementById('recharge-amount').value);
    const description = document.getElementById('recharge-description').value.trim();
    
    if (isNaN(amount) || amount <= 0) {
        showMessage('O valor deve ser maior que zero', 'error');
        return;
    }
    
    try {
        const response = await authenticatedFetch('/api/payments/recharge', {
            method: 'POST',
            body: JSON.stringify({ amount, description })
        });
        
        if (response.ok) {
            const result = await response.json();
            showMessage(result.message, 'success');
            
            // Atualizar interface
            await updateBalance();
            await loadTransactions();
            
            // Limpar formulário
            document.getElementById('recharge-amount').value = '';
            document.getElementById('recharge-description').value = '';
        } else {
            const error = await response.json();
            showMessage(error.detail || 'Erro ao recarregar', 'error');
        }
    } catch (error) {
        console.error('Erro na recarga:', error);
        showMessage('Erro ao recarregar créditos', 'error');
    }
}

// ============================================
// EXPORTAÇÃO
// ============================================

/**
 * Exporta transações para CSV
 */
async function exportTransactions() {
    try {
        const response = await authenticatedFetch('/export/transactions');
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `transacoes_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
            
            showMessage('Exportação concluída!', 'success');
        } else {
            showMessage('Erro ao exportar transações', 'error');
        }
    } catch (error) {
        console.error('Erro na exportação:', error);
        showMessage('Erro ao exportar transações', 'error');
    }
}

// ============================================
// INICIALIZAÇÃO
// ============================================

/**
 * Inicializa a página de acordo com a URL
 */
function initializePage() {
    const path = window.location.pathname;
    
    // Página de dashboard
    if (path === '/dashboard') {
        if (!authToken) {
            window.location.href = '/';
            return;
        }
        
        // Carregar dados iniciais
        updateBalance();
        loadTransactions();
        
        // Configurar atualização periódica (a cada 30 segundos)
        setInterval(updateBalance, 30000);
        setInterval(loadTransactions, 60000);
        
        // Configurar formulários
        const paymentForm = document.getElementById('payment-form');
        if (paymentForm) {
            paymentForm.addEventListener('submit', simulatePayment);
        }
        
        const rechargeForm = document.getElementById('recharge-form');
        if (rechargeForm) {
            rechargeForm.addEventListener('submit', rechargeCredits);
        }
        
        // Configurar botões
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', logout);
        }
        
        const exportBtn = document.getElementById('export-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', exportTransactions);
        }
    }
    
    // Página inicial (login/registro)
    if (path === '/') {
        // Configurar abas
        const tabs = document.querySelectorAll('.tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', function() {
                const tabId = this.dataset.tab;
                
                tabs.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                
                document.querySelectorAll('.tab-content').forEach(content => {
                    content.classList.remove('active');
                });
                document.getElementById(`${tabId}-tab`).classList.add('active');
            });
        });
        
        // Configurar formulários
        const loginForm = document.getElementById('login-form');
        if (loginForm) {
            loginForm.addEventListener('submit', login);
        }
        
        const registerForm = document.getElementById('register-form');
        if (registerForm) {
            registerForm.addEventListener('submit', register);
        }
    }
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', initializePage);

// Expor funções globalmente (para debugging)
window.app = {
    login,
    register,
    logout,
    updateBalance,
    loadTransactions,
    simulatePayment,
    rechargeCredits,
    exportTransactions
};