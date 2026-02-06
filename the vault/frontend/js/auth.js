const API_URL = 'http://localhost:8000/api';

class AuthService {
    constructor() {
        this.token = localStorage.getItem('token');
        this.user = JSON.parse(localStorage.getItem('user')) || null;
    }

    async register(userData) {
        try {
            const response = await fetch(`${API_URL}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });

            const data = await response.json();
            
            if (response.ok) {
                this.setAuthData(data.token.access_token, data.user);
            }
            
            return data;
        } catch (error) {
            return {
                success: false,
                message: 'Erro na conexão com o servidor'
            };
        }
    }

    async login(loginData) {
        try {
            const response = await fetch(`${API_URL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(loginData)
            });

            const data = await response.json();
            
            if (response.ok) {
                this.setAuthData(data.token.access_token, data.user);
            }
            
            return data;
        } catch (error) {
            return {
                success: false,
                message: 'Erro na conexão com o servidor'
            };
        }
    }

    async getProfile() {
        if (!this.token) return null;

        try {
            const response = await fetch(`${API_URL}/profile`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (response.ok) {
                const user = await response.json();
                this.user = user;
                localStorage.setItem('user', JSON.stringify(user));
                return user;
            }
            
            return null;
        } catch (error) {
            return null;
        }
    }

    logout() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/index.html';
    }

    isAuthenticated() {
        return !!this.token;
    }

    setAuthData(token, user) {
        this.token = token;
        this.user = user;
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(user));
    }
}

const authService = new AuthService();

// Utilitários para manipulação do DOM
function showAlert(message, type = 'error') {
    const alertDiv = document.getElementById('alert');
    alertDiv.textContent = message;
    alertDiv.className = `alert alert-${type}`;
    alertDiv.style.display = 'block';
    
    setTimeout(() => {
        alertDiv.style.display = 'none';
    }, 5000);
}

function toggleLoading(button, isLoading) {
    const originalText = button.dataset.originalText || button.textContent;
    
    if (isLoading) {
        button.dataset.originalText = originalText;
        button.innerHTML = '<span class="spinner"></span> Carregando...';
        button.disabled = true;
    } else {
        button.textContent = originalText;
        button.disabled = false;
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', async () => {
    // Verificar autenticação
    if (authService.isAuthenticated()) {
        const user = await authService.getProfile();
        if (user) {
            // Mostrar perfil se estiver na página de login/cadastro
            if (window.location.pathname.includes('index.html') || 
                window.location.pathname.includes('register.html')) {
                window.location.href = '/profile.html';
            }
        } else {
            authService.logout();
        }
    }

    // Formulário de Login
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const button = loginForm.querySelector('button[type="submit"]');
            toggleLoading(button, true);
            
            const loginData = {
                username: document.getElementById('username').value,
                password: document.getElementById('password').value
            };
            
            const result = await authService.login(loginData);
            
            toggleLoading(button, false);
            
            if (result.success) {
                showAlert('Login realizado com sucesso!', 'success');
                setTimeout(() => {
                    window.location.href = '/profile.html';
                }, 1500);
            } else {
                showAlert(result.detail || result.message);
            }
        });
    }

    // Formulário de Registro
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const button = registerForm.querySelector('button[type="submit"]');
            toggleLoading(button, true);
            
            const userData = {
                username: document.getElementById('username').value,
                email: document.getElementById('email').value,
                full_name: document.getElementById('fullName').value,
                password: document.getElementById('password').value
            };
            
            const result = await authService.register(userData);
            
            toggleLoading(button, false);
            
            if (result.success) {
                showAlert('Cadastro realizado com sucesso!', 'success');
                setTimeout(() => {
                    window.location.href = '/profile.html';
                }, 1500);
            } else {
                showAlert(result.detail || result.message);
            }
        });
    }

    // Botão de Logout
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            authService.logout();
        });
    }

    // Mostrar informações do perfil
    const profileSection = document.getElementById('profileInfo');
    if (profileSection && authService.user) {
        profileSection.innerHTML = `
            <div class="profile-info">
                <p><strong>Username:</strong> ${authService.user.username}</p>
                <p><strong>Email:</strong> ${authService.user.email}</p>
                ${authService.user.full_name ? `<p><strong>Nome completo:</strong> ${authService.user.full_name}</p>` : ''}
            </div>
        `;
    }
});